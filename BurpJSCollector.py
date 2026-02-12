#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
BurpJSCollector - Simple JavaScript URL Collector for Burp Suite
Automatically collects full URLs to JavaScript files from proxy traffic
"""

from burp import IBurpExtender, ITab, IHttpListener
from java.awt import BorderLayout, FlowLayout, Dimension
from java.awt.datatransfer import StringSelection
from java.awt import Toolkit
from javax.swing import (JPanel, JButton, JScrollPane, JTextArea,
                         JLabel, JCheckBox, JFileChooser, BorderFactory,
                         SwingUtilities, BoxLayout, Box)
from javax.swing.filechooser import FileNameExtensionFilter
from java.io import File
from java.net import URL
import re
from urlparse import urlparse, urljoin


def normalize_url(url):
    """Normalize a URL by stripping default ports (:443 for https, :80 for http)."""
    url = re.sub(r'(https://[^/:]+):443(?=/|$)', r'\1', url)
    url = re.sub(r'(http://[^/:]+):80(?=/|$)', r'\1', url)
    return url

class BurpExtender(IBurpExtender, ITab, IHttpListener):

    def registerExtenderCallbacks(self, callbacks):
        # Keep a reference to callbacks
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()

        # Set extension name
        callbacks.setExtensionName("JS File Collector")

        # Initialize data structures
        self.js_urls = set()  # Use set for automatic deduplication

        # Load previously saved URLs from Burp project file
        self._load_urls()

        # CDN patterns to filter (if enabled)
        self.cdn_patterns = [
            'jquery.com', 'googleapis.com', 'cloudflare.com',
            'jsdelivr.net', 'unpkg.com', 'cdnjs.cloudflare.com',
            'bootstrapcdn.com', 'fontawesome.com', 'polyfill.io'
        ]

        # Create UI
        self._create_ui()

        # Register as HTTP listener
        callbacks.registerHttpListener(self)

        # Add custom tab to Burp
        callbacks.addSuiteTab(self)

        # Update display with any loaded URLs
        SwingUtilities.invokeLater(lambda: self._update_display())

        print("[+] JS File Collector loaded successfully")
        if self.js_urls:
            print("[+] Restored {} JS URLs from previous session".format(len(self.js_urls)))
        print("[+] Monitoring all traffic for JavaScript files...")

    def _create_ui(self):
        """Create the extension UI"""
        self.panel = JPanel(BorderLayout())

        # Top panel with counter and controls
        top_panel = JPanel()
        top_panel.setLayout(BoxLayout(top_panel, BoxLayout.Y_AXIS))
        top_panel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10))

        # Counter label
        self.counter_label = JLabel("Collected: 0 unique JS files")
        self.counter_label.setFont(self.counter_label.getFont().deriveFont(14.0))
        counter_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        counter_panel.add(self.counter_label)
        top_panel.add(counter_panel)

        top_panel.add(Box.createVerticalStrut(5))

        # Text area for URLs
        self.text_area = JTextArea()
        self.text_area.setEditable(False)
        self.text_area.setLineWrap(False)
        self.text_area.setFont(self.text_area.getFont().deriveFont(12.0))
        scroll_pane = JScrollPane(self.text_area)
        scroll_pane.setPreferredSize(Dimension(800, 400))

        # Bottom panel with buttons
        button_panel = JPanel(FlowLayout(FlowLayout.LEFT))
        button_panel.setBorder(BorderFactory.createEmptyBorder(5, 5, 5, 5))

        # Export button
        self.export_button = JButton("Export to File", actionPerformed=self.export_to_file)
        button_panel.add(self.export_button)

        # Copy button
        self.copy_button = JButton("Copy to Clipboard", actionPerformed=self.copy_to_clipboard)
        button_panel.add(self.copy_button)

        # Clear button
        self.clear_button = JButton("Clear List", actionPerformed=self.clear_list)
        button_panel.add(self.clear_button)

        # CDN filter checkbox
        self.cdn_filter_checkbox = JCheckBox("Filter out CDN libraries", actionPerformed=self.toggle_cdn_filter)
        self.cdn_filter_checkbox.setSelected(False)
        button_panel.add(self.cdn_filter_checkbox)

        # Add components to main panel
        self.panel.add(top_panel, BorderLayout.NORTH)
        self.panel.add(scroll_pane, BorderLayout.CENTER)
        self.panel.add(button_panel, BorderLayout.SOUTH)

    def getTabCaption(self):
        """Return the tab name"""
        return "JS Collector"

    def getUiComponent(self):
        """Return the UI component"""
        return self.panel

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
        """Process each HTTP message"""
        # Only process responses
        if messageIsRequest:
            return

        try:
            # Get request info
            request_info = self._helpers.analyzeRequest(messageInfo)
            url = request_info.getUrl()

            # Skip out-of-scope URLs
            if not self._callbacks.isInScope(url):
                return

            # Get response
            response = messageInfo.getResponse()
            if response is None:
                return

            response_info = self._helpers.analyzeResponse(response)

            # Check if the URL itself is a JS file
            url_str = str(url)
            if self._is_js_file(url_str):
                self._add_js_url(url_str)

            # Scan response body for JS file references
            body_offset = response_info.getBodyOffset()
            body = response[body_offset:].tostring()

            # Look for JavaScript file references in the body
            self._extract_js_from_body(body, url_str)

        except Exception as e:
            print("[!] Error processing message: {}".format(str(e)))

    def _is_js_file(self, url):
        """Check if URL points to a JavaScript file"""
        # Strip query string and fragment before checking extension
        path = url.split('?')[0].split('#')[0].lower()
        js_extensions = ('.js', '.jsx', '.mjs', '.ts')
        if not path.endswith(js_extensions):
            return False
        # Guard against .ts matching non-JS paths like /timestamps
        if path.endswith('.ts') and not re.search(r'/[^/]+\.ts$', path):
            return False
        return True

    def _extract_js_from_body(self, body, base_url):
        """Extract JavaScript file references from response body"""
        try:
            # Decode body
            body_str = body
            if isinstance(body, bytes):
                try:
                    body_str = body.decode('utf-8', errors='ignore')
                except:
                    body_str = body.decode('latin-1', errors='ignore')

            # Regex patterns for JS file references (.js, .jsx, .mjs, .ts)
            js_ext = r'\.(?:js|jsx|mjs|ts)'
            patterns = [
                r'<script[^>]+src=["\']([^"\']*?' + js_ext + r'[^"\']*)["\']',  # <script src="...">
                r'import\s+.*?from\s+["\']([^"\']+' + js_ext + r'[^"\']*)["\']',  # import from "..."
                r'require\(["\']([^"\']+' + js_ext + r'[^"\']*)["\']',  # require("...")
                r'href=["\']([^"\']*?' + js_ext + r'[^"\']*)["\']',  # href="..."
                r'url\(["\']?([^"\'()]+' + js_ext + r'[^"\'()]*)["\']?\)',  # url(...)
            ]

            for pattern in patterns:
                matches = re.findall(pattern, body_str, re.IGNORECASE)
                for match in matches:
                    # Construct full URL
                    full_url = self._make_absolute_url(match, base_url)
                    if full_url and self._is_js_file(full_url):
                        self._add_js_url(full_url)

        except Exception as e:
            pass  # Silently handle body parsing errors

    def _make_absolute_url(self, url, base_url):
        """Convert relative URL to absolute URL"""
        try:
            if url.startswith('http://') or url.startswith('https://'):
                return url
            elif url.startswith('//'):
                # Protocol-relative URL
                parsed_base = urlparse(base_url)
                return parsed_base.scheme + ':' + url
            else:
                # Relative URL
                return urljoin(base_url, url)
        except:
            return None

    def _is_cdn_url(self, url):
        """Check if URL is from a CDN"""
        url_lower = url.lower()
        for pattern in self.cdn_patterns:
            if pattern in url_lower:
                return True
        return False

    def _add_js_url(self, url):
        """Add a JavaScript URL to the collection"""
        # Remove fragments and normalize default ports
        url = url.split('#')[0]
        url = normalize_url(url)

        # Skip out-of-scope URLs
        try:
            java_url = URL(url)
            if not self._callbacks.isInScope(java_url):
                return
        except:
            return  # Skip invalid URLs

        # Skip if CDN filter is enabled and this is a CDN URL
        if self.cdn_filter_checkbox.isSelected() and self._is_cdn_url(url):
            return

        # Add to set (automatically deduplicates)
        if url not in self.js_urls:
            self.js_urls.add(url)
            self._save_urls()
            # Update UI on Swing thread
            SwingUtilities.invokeLater(lambda: self._update_display())

    def _save_urls(self):
        """Save collected URLs to Burp project file"""
        try:
            data = '\n'.join(sorted(self.js_urls))
            self._callbacks.saveExtensionSetting("js_urls", data)
        except Exception as e:
            print("[!] Error saving URLs: {}".format(str(e)))

    def _load_urls(self):
        """Load previously saved URLs from Burp project file"""
        try:
            data = self._callbacks.loadExtensionSetting("js_urls")
            if data:
                urls = [u.strip() for u in data.split('\n') if u.strip()]
                self.js_urls = set(urls)
        except Exception as e:
            print("[!] Error loading saved URLs: {}".format(str(e)))

    def _update_display(self):
        """Update the text area with current URLs"""
        sorted_urls = sorted(list(self.js_urls))
        self.text_area.setText('\n'.join(sorted_urls))
        self.counter_label.setText("Collected: {} unique JS files".format(len(self.js_urls)))

    def export_to_file(self, event):
        """Export URLs to a text file"""
        if len(self.js_urls) == 0:
            self._callbacks.printOutput("[!] No JavaScript files to export")
            return

        # File chooser
        chooser = JFileChooser()
        chooser.setDialogTitle("Save JavaScript URLs")
        chooser.setSelectedFile(File("js_files.txt"))

        # Filter for .txt files
        txt_filter = FileNameExtensionFilter("Text Files (*.txt)", "txt")
        chooser.setFileFilter(txt_filter)

        ret = chooser.showSaveDialog(self.panel)

        if ret == JFileChooser.APPROVE_OPTION:
            file_path = chooser.getSelectedFile().getAbsolutePath()

            # Ensure .txt extension
            if not file_path.endswith('.txt'):
                file_path += '.txt'

            try:
                with open(file_path, 'w') as f:
                    sorted_urls = sorted(list(self.js_urls))
                    for url in sorted_urls:
                        f.write(url + '\n')

                self._callbacks.printOutput("[+] Exported {} URLs to: {}".format(len(self.js_urls), file_path))
                print("[+] Exported {} URLs to: {}".format(len(self.js_urls), file_path))

            except Exception as e:
                self._callbacks.printError("[!] Error exporting file: {}".format(str(e)))

    def copy_to_clipboard(self, event):
        """Copy all URLs to clipboard"""
        if len(self.js_urls) == 0:
            self._callbacks.printOutput("[!] No JavaScript files to copy")
            return

        sorted_urls = sorted(list(self.js_urls))
        clipboard_text = '\n'.join(sorted_urls)

        # Copy to clipboard
        selection = StringSelection(clipboard_text)
        clipboard = Toolkit.getDefaultToolkit().getSystemClipboard()
        clipboard.setContents(selection, None)

        self._callbacks.printOutput("[+] Copied {} URLs to clipboard".format(len(self.js_urls)))
        print("[+] Copied {} URLs to clipboard".format(len(self.js_urls)))

    def clear_list(self, event):
        """Clear the URL list"""
        self.js_urls.clear()
        self._save_urls()
        self._update_display()
        self._callbacks.printOutput("[+] Cleared JavaScript URL list")
        print("[+] Cleared JavaScript URL list")

    def toggle_cdn_filter(self, event):
        """Toggle CDN filtering and refresh display"""
        if self.cdn_filter_checkbox.isSelected():
            # Remove CDN URLs from current list
            non_cdn_urls = set()
            for url in self.js_urls:
                if not self._is_cdn_url(url):
                    non_cdn_urls.add(url)
            self.js_urls = non_cdn_urls
            self._save_urls()
            self._callbacks.printOutput("[+] CDN filter enabled")
        else:
            self._callbacks.printOutput("[+] CDN filter disabled")

        self._update_display()
