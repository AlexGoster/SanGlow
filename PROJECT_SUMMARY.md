# SanGlow - Project Summary

## What is SanGlow?
Desktop music streaming/player app (PyQt6 + Python) for GitHub portfolio.

## Tech Stack
- Python 3.14, PyQt6, SQLAlchemy, pygame-ce
- PyInstaller for .exe, Inno Setup for installer
- GitHub CLI for releases

## Key Features
- Spotify-like UI (dark gray + orange accent)
- System tray (minimize to tray, context menu)
- Global media hotkeys (Play/Pause, Next, Prev, Stop)
- Autostart on Windows login
- Registration/Login with email verification
- Captcha protection
- Rate limiting on failed logins
- JWT authentication

## Security (30+ fixes)
- Password hashing (bcrypt)
- JWT tokens with expiry
- Input sanitization
- SQL injection prevention (SQLAlchemy ORM)
- Rate limiting on auth attempts
- Captcha on registration
- Auto-verify when SMTP not configured

## Build Commands
```
.\.venv\Scripts\python.exe build.py          # Build exe
ISCC.exe installer.iss                        # Build installer
gh release upload v1.1.0 file.zip --repo AlexGoster/SanGlow  # Upload
```

## Project Structure
```
src/
  main.py              - Entry point
  auth/service.py      - Auth logic (register, login, verify)
  ui/main_window.py    - Main app window
  ui/tray.py           - System tray
  ui/widgets/login_dialog.py - Login/Register UI
  player/engine.py     - Music playback
  spotify/             - Spotify integration
  utils/smtc.py        - Media hotkeys
  utils/autostart.py   - Windows autostart
config/settings.py     - App config
```

## Common Issues
- `git add -A` re-adds zips: check .gitignore
- Build must run as `python build.py` not `python -m PyInstaller`
- `winsdk` cannot install (needs VS C++ compiler)
- SmartScreen warning persists without code signing cert
