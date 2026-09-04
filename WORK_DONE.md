# SanGlow - Work Done & Skills

## Completed Work

### Core App
- Full PyQt6 desktop app with sidebar navigation
- Login/Register with email verification
- Captcha protection on registration
- JWT authentication system
- SQLAlchemy database (SQLite)
- Music player with pygame-ce
- Spotify integration (search, playlists)
- System tray with controls
- Global media hotkeys
- Windows autostart support

### UI/UX
- LANE-style dark theme (#1a1a1a + #e8734a orange)
- Fullscreen mode (showMaximized)
- Responsive layout (900x600 min)
- Error handling with user-friendly messages
- Word wrap on error labels
- Scroll area on registration form

### Security (Rounds 1-5)
1. Password hashing (bcrypt)
2. JWT with expiry + refresh tokens
3. Input sanitization (XSS prevention)
4. SQL injection prevention (ORM)
5. Rate limiting (5 attempts / 15 min lockout)
6. Captcha on registration
7. Auto-verify when SMTP not configured
8. Password validation (10+ chars, upper, lower, digit, special)
9. Username validation (3-50 chars, alphanumeric + underscore)
10. Email validation regex

### Build & Deploy
- PyInstaller .exe build (x64 only)
- Inno Setup installer
- GitHub releases (v1.0.5 - v1.1.0)
- Zip under 100MB (trimmed Qt6 files)

## Skills Used
- Python 3.14, PyQt6, SQLAlchemy
- PyInstaller, Inno Setup
- Git, GitHub CLI
- Windows Registry (autostart)
- ctypes/user32 (media hotkeys)
- JWT, bcrypt, cryptography
- pytest (5 tests passing)

## Bug Fixes
- MainWindow garbage collection (stored at module scope)
- White screen crash (showMaximized moved to main.py)
- Registration error messages (existing account check)
- Password validation (added _ and -)
- Error text truncation (word wrap)
- Registration form overflow (scroll area)
