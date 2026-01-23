# Contributing to BurpJSCollector

Thank you for your interest in contributing to BurpJSCollector! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Burp Suite version
- Python/Jython version
- Error messages (from Extender → Output/Errors)
- Screenshots (if UI related)

### Suggesting Features

Have an idea? Create an issue with:
- Clear description of the feature
- Use case/benefit
- Example of how it would work in the UI

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow existing code style
   - Test in both Burp Community and Professional (if possible)
   - Ensure Jython 2.7 compatibility

4. **Test your changes**
   - Load extension in Burp
   - Test all buttons (Export, Copy, Clear)
   - Test CDN filter
   - Browse test sites to verify collection

5. **Commit your changes**
   ```bash
   git commit -m "Add: description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Clear description of changes
   - Screenshots of UI changes
   - Testing notes

### Code Guidelines

- **Python 2.7 compatible**: Extension must work with Jython 2.7
- **Burp API**: Use official Burp Extender API
- **Comments**: Add docstrings for functions
- **Error handling**: Fail gracefully, log errors
- **UI**: Keep interface simple and intuitive

### Testing Checklist

Before submitting PR:
- [ ] Extension loads without errors
- [ ] Collects JS files from HTTP traffic
- [ ] Export button works
- [ ] Copy to clipboard works
- [ ] Clear button works
- [ ] CDN filter works
- [ ] Counter updates correctly
- [ ] No memory leaks during long sessions

### Attribution

**Important:** When contributing, you agree that your code will be licensed under the same MIT License with Attribution Requirement. Your contributions will be credited, and the original author (Shan Majeed) must still be attributed in any derivative works.

## Questions?

Feel free to open an issue for questions or discussions!

---

Thank you for contributing to the security community! 🙏
