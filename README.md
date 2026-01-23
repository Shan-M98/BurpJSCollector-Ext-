# BurpJSCollector

<p align="center">
  <b>Simple Burp Suite Extension for Collecting JavaScript File URLs</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-2.7%20%7C%203.x-blue.svg" alt="Python 2.7 | 3.x">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Burp-Suite-orange.svg" alt="Burp Suite">
  <img src="https://img.shields.io/badge/Maintained-Yes-brightgreen.svg" alt="Maintained">
</p>

---

## 📋 Overview

**BurpJSCollector** is a Burp Suite extension that solves a common frustration with JS Link Finder and similar tools - it gives you **complete, full URLs** to JavaScript files, not relative paths!

### The Problem with JS Link Finder

```
❌ Base: https://example.com
     /static/app.js
     /js/bundle.js
```

### The BurpJSCollector Solution

```
✅ https://example.com/static/app.js
✅ https://example.com/js/bundle.js
```

**Clean. Complete. Ready to use.**

Perfect companion to [JSExtractor](https://github.com/yourusername/JSExtractor)!

## ✨ Features

- ✅ **Automatic Collection** - Passively captures JS files as you browse
- ✅ **Full URLs Only** - No relative paths, no fragments
- ✅ **Auto-Deduplication** - No duplicates in your list
- ✅ **Multiple Sources** - Captures from:
  - Direct `.js` file requests
  - `<script src="">` tags in HTML
  - JavaScript imports/requires
  - Response body references
- ✅ **All JS File Types** - `.js`, `.jsx`, `.mjs`, `.ts`, `.min.js`, `.bundle.js`
- ✅ **CDN Filtering** - Toggle to hide common CDN libraries
- ✅ **Export to File** - One-click save as `.txt`
- ✅ **Copy to Clipboard** - Quick copy all URLs
- ✅ **Live Counter** - See collection progress in real-time
- ✅ **Simple UI** - Clean, straightforward interface

## 🚀 Quick Start

### Prerequisites

1. **Burp Suite** (Community or Professional)
2. **Jython Standalone JAR** - [Download here](https://www.jython.org/download)

### Installation

#### Step 1: Download Jython

1. Visit https://www.jython.org/download
2. Download **Jython Standalone JAR** (e.g., `jython-standalone-2.7.3.jar`)
3. Save it somewhere accessible

#### Step 2: Configure Burp

1. Open **Burp Suite**
2. Go to **Extender** → **Options**
3. Under **Python Environment**, click **Select file...**
4. Browse to your `jython-standalone-2.7.3.jar`
5. Click **Open**

#### Step 3: Load Extension

1. In Burp, go to **Extender** → **Extensions** → **Add**
2. Set **Extension Type** to **Python**
3. Click **Select file...** and choose `BurpJSCollector.py`
4. Click **Next**

✅ You should see: `[+] JS File Collector loaded successfully`

#### Step 4: Verify

Look for a new tab in Burp called **"JS Collector"** - you're ready!

## 📖 Usage

### Basic Workflow

```
1. Browse target site (Burp proxy enabled)
   ↓
2. Extension automatically captures JS file URLs
   ↓
3. Click "Export to File" → save as js_files.txt
   ↓
4. Use with JSExtractor: python js_recon.py js_files.txt
```

### UI Overview

```
┌─ JS Collector ──────────────────────────────────────┐
│                                                      │
│  Collected: 47 unique JS files                      │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │ https://example.com/static/app.js          │    │
│  │ https://example.com/js/bundle.min.js       │    │
│  │ https://cdn.example.com/main.js            │    │
│  │ https://api.example.com/v1/client.js       │    │
│  │ ...                                         │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  [Export to File] [Copy to Clipboard] [Clear]      │
│  [ ] Filter out CDN libraries                       │
│                                                      │
└──────────────────────────────────────────────────────┘
```

### Features Explained

**Export to File**
- Saves all URLs to a `.txt` file
- One URL per line
- Default filename: `js_files.txt`
- Perfect for JSExtractor input

**Copy to Clipboard**
- Instantly copies all URLs
- Paste anywhere you need

**Clear**
- Empties the list
- Start fresh for new target

**Filter CDN Libraries**
- Hides common CDN URLs (jQuery, React, etc.)
- Focus on target-specific JS files

## 🎯 Complete Workflow with JSExtractor

```bash
# Step 1: Collect JS URLs in Burp
#   - Browse target site
#   - Extension auto-collects
#   - Export to js_files.txt

# Step 2: Analyze with JSExtractor
cd JSExtractor
python js_recon.py ../js_files.txt

# Step 3: Review findings
cat scans/js_files_*/results/FINDINGS.txt

# Step 4: Test discovered endpoints
cat scans/js_files_*/results/paths_api_routes.txt
```

## 📊 What Gets Collected

### File Types
- `.js` - Standard JavaScript
- `.jsx` - React JavaScript
- `.mjs` - ES6 Modules
- `.ts` - TypeScript
- `.min.js` - Minified JavaScript
- `.bundle.js` - Bundled JavaScript

### Sources
- Direct `.js` requests
- `<script src="">` tags
- `import ... from "..."`
- `require("...")`
- `<link href="...js">`
- URL references in CSS

### URL Formats
- Absolute: `https://example.com/app.js` ✅
- Protocol-relative: `//cdn.example.com/app.js` ✅ (converted)
- Relative: `/static/app.js` ✅ (converted to absolute)
- With params: `app.js?v=1.2.3` ✅

## 🔍 Examples

### Example 1: Bug Bounty Workflow

```bash
# 1. Configure browser to use Burp proxy
# 2. Browse target website normally
# 3. Go to "JS Collector" tab in Burp
# 4. See collected JS files (Counter shows: "Collected: 150 unique JS files")
# 5. Click "Export to File" → save as target_js.txt
# 6. Analyze: python js_recon.py target_js.txt
```

### Example 2: Multiple Targets

```bash
# Target A
# Browse https://target-a.com
# Export as target_a_js.txt
# Click "Clear"

# Target B
# Browse https://target-b.com
# Export as target_b_js.txt

# Analyze separately
python js_recon.py target_a_js.txt
python js_recon.py target_b_js.txt
```

### Example 3: Clean List (No CDNs)

```bash
# 1. Browse target
# 2. Enable "Filter out CDN libraries" checkbox
# 3. Export → get only custom JS files
# 4. Focus analysis on target code
```

## 🆚 Comparison to JS Link Finder

| Feature | JS Link Finder | BurpJSCollector |
|---------|----------------|------------------|
| URL Format | Base + Paths | Complete URLs ✅ |
| Ready to Use | No (manual join) | Yes ✅ |
| Export | Complex | One-click ✅ |
| CDN Filter | No | Yes ✅ |
| Auto-dedupe | No | Yes ✅ |
| Clipboard | No | Yes ✅ |
| Live Counter | No | Yes ✅ |

## 🛡️ Security Notice

This tool is for **authorized security testing only**:
- ✅ Bug bounty programs
- ✅ Penetration testing with permission
- ✅ Your own applications
- ❌ Unauthorized scanning

**You are responsible for ensuring proper authorization.**

## 🐛 Troubleshooting

### Extension Won't Load

**Error:** "Failed to load extension"

**Solution:**
1. Verify Jython is configured: Extender → Options → Python Environment
2. Ensure `jython-standalone-2.7.3.jar` is selected
3. Restart Burp Suite

### No URLs Collected

**Issue:** Counter stays at 0

**Solution:**
1. Verify proxy is working (check Proxy → HTTP history)
2. Ensure you're browsing sites with JavaScript
3. Check Extender → Output for errors

### Export Not Working

**Solution:**
1. Check write permissions on save location
2. Try saving to different directory
3. Check Extender → Errors tab

## 📝 License

This project is licensed under the MIT License with Attribution Requirement - see the [LICENSE](LICENSE) file for details.

### 🏆 Attribution Requirements

If you use this tool commercially or create improvements/modifications:

✅ **Required:**
- Provide clear attribution: "Based on BurpJSCollector by Shan Majeed"
- Include a link to this repository
- State if you've made modifications

✅ **Example Attribution:**
```
This tool uses BurpJSCollector by Shan Majeed (https://github.com/yourusername/BurpJSCollector)
Modified to add [your changes]
```

### 📣 Give Credit

If you:
- Use this in a commercial product
- Create an improved version
- Fork and modify it
- Include it in another tool

**Please credit the original author!** It supports open-source development and helps the community.

## 🙏 Acknowledgments

- Burp Suite community
- Bug bounty hunters for feedback
- Security research community

## 🤝 Related Projects

**[JSExtractor](https://github.com/yourusername/JSExtractor)** - Analyze collected JS files for secrets, endpoints, and vulnerabilities

## ⭐ Show Your Support

If you find BurpJSCollector useful:
- Star the repository ⭐
- Share with the community
- Report bugs
- Suggest improvements
- Contribute code

---

<p align="center">
  Made with ❤️ for the security research community
</p>

<p align="center">
  <b>Happy Hunting! 🎯</b>
</p>
