# Contributing to Lobby Display

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Ways to Contribute

- **Report bugs** - Open an issue with reproduction steps
- **Suggest features** - Open an issue describing the use case
- **Write documentation** - Improve guides, add examples
- **Submit code** - Fix bugs or implement features via pull requests
- **Test releases** - Try beta versions and report issues

## Development Setup

### Prerequisites

- Raspberry Pi or Linux machine for testing
- Python 3.11+
- Git

### Fork and Clone

```bash
# Fork the repo on GitHub, then:
git clone https://github.com/YOUR_USERNAME/lobby-display.git
cd lobby-display
```

### Create Virtual Environment

```bash
cd src
python3 -m venv venv
source venv/bin/activate
pip install flask pillow pygame zeroconf
```

### Run in Development Mode

```bash
# Terminal 1: Web server
python3 app.py

# Terminal 2: Display (requires X11/display)
python3 display.py
```

### Code Style

#### Python

- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings for functions and classes
- Keep functions focused and under 50 lines when possible

Example:

```python
def get_playlist_items(playlist_id):
    """
    Retrieve all items in a playlist with their effective durations.
    
    Args:
        playlist_id (int): The playlist database ID
        
    Returns:
        list: Playlist items with metadata
    """
    # Implementation here
    pass
```

#### HTML/CSS

- Use 2-space indentation
- Include comments for complex sections
- Maintain existing color scheme (#1a1a2e, #e94560, etc.)

#### Commit Messages

Use clear, descriptive commit messages:

```text
Good: "Fix image rotation for 90-degree displays"
Good: "Add support for WebP image format"
Bad: "fix stuff"
Bad: "update"
```

#### Format

```text
Short summary (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Include motivation for change and contrast with previous behavior.
```

#### Pull Request Process

1. Create a branch for your changes

    ```bash
    git checkout -b feature/your-feature-name
    ```

2. Make your changes with clear, focused commits
3. Test thoroughly:
    - Web interface functions
    - Display rendering
    - Playlist management
    - Settings persistence
4. Update documentation if needed:
    - [README.md](./README.md) for feature overview
    - [gettingstarted.md](./gettingstarted.md) for user instructions
    - This file for development changes
5. Submit pull request with:
    - Clear description of changes
    - Link to related issue(s)
    - Screenshots for UI changes
    - Test results

### Testing Checklist

Before submitting a PR, verify:

#### Functionality

- [ ] Images upload successfully
- [ ] Playlists create, edit, and delete
- [ ] Active playlist switches correctly
- [ ] Settings save and persist
- [ ] Display shows images in correct order
- [ ] mDNS broadcasting works

#### Compatibility

- [ ] Works on Raspberry Pi 3
- [ ] Works on Raspberry Pi 4/5 (64-bit)
- [ ] Tested with clean install

#### Edge Cases

- [ ] Empty playlist handling
- [ ] Large image files (>10MB)
- [ ] Special characters in filenames
- [ ] Network interruption recovery

### Reporting Bugs

#### Before Reporting

- Check existing issues
- Test with latest version
- Try with clean data directory

#### Bug Report Template

```markdown
**Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Device: [e.g., Raspberry Pi 4]
- OS: [e.g., Raspberry Pi OS 64-bit]
- Version: [e.g., 1.0.0]

**Logs**
Paste relevant logs from `journalctl` or terminal output
```

### Feature Requests

#### Suggesting Features

Open an issue with:

- **Use case** - Why is this feature needed?
- **Proposed solution** - How should it work?
- **Alternatives** - What else was considered?
- **Additional context** - Mockups, examples, etc.

#### Feature Acceptance Criteria

Features are more likely to be accepted if they:

- Align with project goals (standalone, simple, reliable)
- Don't add external dependencies (especially cloud services)
- Include tests and documentation
- Consider backward compatibility

### Project Architecture

Understanding the codebase:

#### Core Components

| File | Purpose |
| - | - |
| `app.py` | Flask web server, API endpoints, database |
| `display.py` | Pygame-based slideshow renderer |
| `mdns.py` | Zeroconf/mDNS broadcasting |
| `AppRun` | AppImage entry point, service installer |
| `templates/` | Jinja2 HTML templates |

#### Data Flow

```text
User Upload → app.py → database.db + uploads/  
                ↓  
            API endpoint ← display.py (slideshow)  
                ↓  
            mDNS broadcast (optional discovery)  
```

#### Code Review

All submissions require review before merging. Reviewers will check:

- Code quality and style
- Test coverage
- Documentation updates
- Backward compatibility
- Security implications

### Release Process

Maintainers will:

1. Review and merge approved PRs
2. Update version numbers
3. Run full test suite
4. Build AppImage for both architectures
5. Create GitHub release with notes
6. Update documentation

### Community

- Be respectful and constructive
- Help others in issues and discussions
- Share your use cases and configurations
- Credit contributors appropriately

### License

By contributing, you agree that your contributions will be licensed under the MIT License.

### Questions?

- Open a GitHub Discussion for general questions
- Comment on relevant issues for specific questions
- Check existing documentation first
Thank you for contributing to Lobby Display!
