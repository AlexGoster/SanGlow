## Final Security Release (v1.0.3)

### What's New:
- **Windows Manifest**: Added application manifest for proper Windows integration
- **Version Info**: EXE now has proper version metadata (CompanyName: AlexGoster)
- **Encrypted Spotify Tokens**: All Spotify tokens encrypted at rest in database
- **Publisher**: AlexGoster (visible in Windows Properties)

### Security Features:
- JWT with 15-minute expiry, JTI blacklist, algorithm validation
- SSRF protection (blocks localhost, 127.0.0.1, 10.x, 172.16.x, 192.168.x)
- Rate limiting on all social actions
- bcrypt 14 rounds for password hashing
- 600k PBKDF2 iterations for encryption
- HTTPS-only audio downloads with domain whitelist
- File size limits (50MB max)
- Secure temp file handling with 0o700 permissions
- Thread-safe brute-force protection

### Files:
- `SanGlow-x64.zip` - Portable x64 version
- `SanGlow-x86.zip` - Portable x86 version
- `sanglow_setup_x64.exe` - Windows installer (x64)
- `sanglow_setup_x86.exe` - Windows installer (x86)

### Notes:
- Publisher: AlexGoster
- License: MIT
- Python 3.14
