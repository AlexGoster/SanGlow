## Security Release v1.0.4

### Fixed:
- Installer rebuilt with proper file copy (not symlink)
- All 4 files verified and ready

### Security Features:
- JWT with 15-minute expiry, JTI blacklist
- SSRF protection (blocks localhost, internal IPs)
- Rate limiting on social actions
- bcrypt 14 rounds for passwords
- 600k PBKDF2 iterations for encryption
- Encrypted Spotify tokens at rest
- HTTPS-only downloads with domain whitelist
- Windows manifest with version info

### Files:
- `SanGlow-x64.zip` - Portable x64
- `SanGlow-x86.zip` - Portable x86
- `sanglow_setup_x64.exe` - Windows installer x64
- `sanglow_setup_x86.exe` - Windows installer x86

### Publisher: AlexGoster
### License: MIT
