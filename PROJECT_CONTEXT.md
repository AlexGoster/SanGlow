# SanGlow - Project Context (для нового сеанса)

## Описание проекта
SanGlow — десктопное приложение для стриминга/плеера музыки (PyQt6 + Python). GitHub репозиторий: `AlexGoster/SanGlow`

## Структура проекта

```
SanGlow/
├── .venv/                          # Python 3.14, pygame-ce (НЕ pygame)
├── assets/
│   ├── icon.ico                    # Иконка (.ico для exe/installer)
│   └── icon.png                    # Иконка (.png для UI)
├── config/
│   ├── __init__.py
│   └── settings.py                 # Настройки, DATA_DIR, USER_DATA_DIR (%APPDATA%\SanGlow)
├── data/                           # Черный список токенов, ключи шифрования
├── src/
│   ├── __init__.py
│   ├── main.py                     # Точка входа: логирование, crash handler, LoginDialog → MainWindow
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── email_verification.py   # SMTP, 6-значный код, автоподтверждение без SMTP
│   │   ├── jwt_handler.py          # JWT токены, blacklist, timestamped
│   │   └── service.py              # AuthService: register/login/verify/change_password
│   ├── importers/
│   │   ├── __init__.py
│   │   ├── playlist_importer.py
│   │   ├── soundcloud.py
│   │   ├── telegram_music.py       # hashlib.sha256 для ID треков
│   │   ├── yandex_music.py
│   │   ├── youtube_music.py
│   │   └── zvuk_music.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py             # SQLAlchemy engine, init_db, get_db_session
│   │   ├── history.py
│   │   ├── playlist.py
│   │   ├── social.py               # Comment, Like, Favorite, Wave, WaveTrack
│   │   └── user.py                 # User: email_verified, verification_code, password history
│   ├── player/
│   │   ├── __init__.py
│   │   └── engine.py               # pygame-ce: скачивание, воспроизведение, скорость
│   ├── social/
│   │   ├── __init__.py
│   │   └── service.py              # validate_url на cover_url/preview_url
│   ├── spotify/
│   │   ├── __init__.py
│   │   ├── auth.py                 # instance-based auth_code/state_param
│   │   └── client.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── greeting.py
│   │   ├── main_window.py
│   │   ├── styles/
│   │   │   └── dark_theme.py       # LANE-style: #1a1a1a, #e8734a, #e0d6cc
│   │   └── widgets/
│   │       ├── __init__.py
│   │       ├── login_dialog.py     # 3-page stack: login → register → verify email, captcha
│   │       └── player_bar.py
│   └── utils/
│       ├── __init__.py
│       ├── captcha.py              # MathCaptcha (+, -, *)
│       ├── encryption.py           # Fernet, PBKDF2, DATA_DIR
│       └── validators.py           # sanitize_input, validate_url (SSRF protection)
├── tests/
│   ├── __init__.py
│   └── test_auth.py                # 5 тестов, все проходят
├── conftest.py                     # Тестовая БД изолирована
├── build.py                        # PyInstaller сборка
├── installer.iss                   # Inno Setup 6 (v1.0.9)
├── SanGlow.spec                    # PyInstaller spec
├── .gitignore
├── pyproject.toml
├── version_info.txt
├── RELEASE_NOTES.md
├── SECURITY.md
└── README.md
```

## Ключевые зависимости
```
PyQt6>=6.5
spotipy>=2.23
SQLAlchemy>=2.0
PyJWT>=2.8
cryptography>=41.0
httpx>=0.25
pygame-ce>=2.5
bcrypt>=4.1
pyinstaller>=6.0
pydantic>=2.0
pydantic-settings>=2.0
Pillow>=10.0
zvuk-music>=0.2
```

## Конфигурация
- `.env` файл (не в git):
  ```
  SPOTIFY_CLIENT_ID=...
  SPOTIFY_CLIENT_SECRET=...
  ZVUK_TOKEN=...
  SMTP_HOST=smtp.gmail.com
  SMTP_PORT=587
  SMTP_USER=
  SMTP_PASSWORD=
  FROM_EMAIL=
  ```
- Автогенерация `JWT_SECRET_KEY` и `ENCRYPTION_KEY` в `%APPDATA%\SanGlow\data\`

## База данных
- SQLite: `%APPDATA%\SanGlow\data\sanglow.db` (frozen) или `sanglow.db` (dev)
- Таблицы: users, playlists, comments, likes, favorites, waves, wave_tracks
- Поля User: id, username, email, password_hash, display_name, avatar_url, bio, spotify_*, is_active, email_verified, verification_code, verification_expires, failed_login_attempts, last_failed_login, password_changed_at, old_passwords (encrypted), created_at, updated_at

## Текущая версия: 1.0.9
## Издатель: AlexGoster
## Лицензия: MIT (2024-2026 AlexGoster)
## Репозиторий: https://github.com/AlexGoster/SanGlow

## Сборка
1. PyInstaller: `python -m PyInstaller build.py --noconfirm --windowed --name SanGlow --icon assets\icon.ico --add-data "assets;assets" --add-data "config;config" --add-data "src;src" --hidden-import src --hidden-import config --hidden-import pygame`
2. Копирование `dist\SanGlow` → `dist\SanGlow-{arch}` → переименование exe
3. Inno Setup: `"C:\Users\Lenovo\AppData\Local\Programs\Inno Setup 6\ISCC.exe" installer.iss`
4. Portable zip: `Compress-Archive`

## История релизов
- v1.0.5: Email verification, captcha, PermissionError fix
- v1.0.6: Auto-verify email when SMTP not configured, show code on screen
- v1.0.7: Fixed DB path crash (database.py imports USER_DATA_DIR)
- v1.0.8: Fixed installer version info, added desktop shortcut + auto-launch
- v1.0.9: (текущий) Fixed installer.iss tasks/flags, desktop shortcut checkedonce

## Проблемы
- SmartScreen warning: нужен code signing certificate ($70-200/год)
- Нет 32-bit Python → x86 сборка невозможна
- git history: SanGlow zips ~105MB превышают 100MB лимит GitHub → нужно `git rm --cached` + `git filter-branch`
