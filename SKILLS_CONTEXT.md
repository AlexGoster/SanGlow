# SanGlow - Skills & Knowledge Context (для нового сеанса)

## Окружение
- **ОС**: Windows 11, Python 3.14 (только 64-bit), виртуальное окружение `.venv` (с точкой!)
- **Путь к проекту**: `C:\Users\Lenovo\Desktop\для ноута\Программы\Python\Pythonpro\SanGlow`
- **GitHub CLI**: `gh` установлен и авторизован как `AlexGoster`
- **Inno Setup 6**: `C:\Users\Lenovo\AppData\Local\Programs\Inno Setup 6\ISCC.exe`
- **PyInstaller**: 6.22.2, pygame-ce 2.5.8, SDL 2.32.10
- **Shell**: PowerShell 5.1

## Важные особенности проекта

### pygame-ce (НЕ pygame!)
```python
import pygame  # Это pygame-ce, установлен через pip install pygame-ce
# Не использовать pygame! Всё работает через обычный import pygame
```

### Пути данных (frozen vs dev)
```python
# config/settings.py:
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
    USER_DATA_DIR = Path(os.environ.get("APPDATA", Path.home() / ".config")) / "SanGlow"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    USER_DATA_DIR = BASE_DIR
DATA_DIR = USER_DATA_DIR / "data"
```

### База данных
```python
# database.py - frozen apps:
if getattr(sys, "frozen", False):
    from config.settings import USER_DATA_DIR
    return USER_DATA_DIR / "sanglow.db"
# НЕ использовать Path(sys.executable).parent для БД!
```

### Email verification - timezone fix
```python
# email_verification.py - SQLite хранит naive datetimes:
def verify_code(stored_code, stored_expires, input_code):
    now = datetime.now(timezone.utc)
    expires = stored_expires if stored_expires.tzinfo else stored_expires.replace(tzinfo=timezone.utc)
    if now > expires:
        return False
    return secrets.compare_digest(stored_code, input_code.strip())
```

### Auto-verify при отсутствии SMTP
```python
# service.py - register():
email_sent = send_verification_email(email, code, username)
if not email_sent:
    user.email_verified = True  # Автоподтверждение
    user.verification_code = None
    user.verification_expires = None
    self.db.commit()
    # Возвращает токены сразу
```

## Инструменты сборки

### PyInstaller
```powershell
.\.venv\Scripts\python.exe -m PyInstaller build.py --noconfirm --windowed --name SanGlow --icon assets\icon.ico --add-data "assets;assets" --add-data "config;config" --add-data "src;src" --hidden-import src --hidden-import config --hidden-import pygame
```

### Inno Setup
```powershell
& "C:\Users\Lenovo\AppData\Local\Programs\Inno Setup 6\ISCC.exe" "C:\Users\Lenovo\Desktop\для ноута\Программы\Python\Pythonpro\SanGlow\installer.iss"
```

### Portable zip
```powershell
Compress-Archive -Path "dist\SanGlow\*" -DestinationPath "SanGlow-v1.0.9-x64.zip"
```

## Git операции

### Очистка истории от больших zips
```powershell
git rm --cached *.zip
git commit -m "Remove zips from tracking"
git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch *.zip' --prune-empty -- --all
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin master --force
```

### Публикация релиза
```powershell
gh release create v1.0.9 --title "SanGlow v1.0.9" --notes "..." --latest "SanGlow-v1.0.9-x64.zip" --repo AlexGoster/SanGlow
```

## Дизайн (LANE-style)
```python
# dark_theme.py:
BG_PRIMARY = "#1a1a1a"      # Основной фон
BG_SECONDARY = "#242424"    # Вторичный фон
ACCENT = "#e8734a"          # Оранжевый акцент
TEXT_PRIMARY = "#e0d6cc"     # Основной текст
TEXT_SECONDARY = "#a09888"   # Вторичный текст
BORDER = "#333333"          # Рамки
```

## Безопасность (5 раундов, 30 уязвимостей исправлено)
1. JWT: algorithm validation, blacklist, timestamped entries
2. Encryption: PBKDF2 600K iterations, Fernet
3. SSRF: URL validation, hostname regex, private IP blocking
4. Auth: rate limiting, lockout, common password check
5. Data: sanitize display names, filenames, track IDs
6. Email: verification codes, timezone-aware expiry

## Пользователь (AlexGoster)
- Язык: русский
- Не хочет эмодзи в приветствии
- Диапазон дат: 2024-2026
- Хочет 32/64 бит инсталлеры (но 32-bit Python нет)
- Максимальный уровень безопасности
- Хочет i18n и улучшения безопасности в новом коде

## Тесты
```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v
# 5 тестов, все проходят
```

## Известные проблемы
- SmartScreen: нужен code signing certificate
- Нет 32-bit Python: x86 сборка невозможна
- git history: zips ~105MB > 100MB лимит GitHub
- `WindowVisible=yes` в Inno Setup устарел и игнорируется

## Чек-лист перед коммитом
1. Не добавлять zips в git (`git add -A` подхватывает!)
2. Не коммитить `.venv/`, `build/`, `dist/`, `__pycache__/`, `installer_output/`
3. Обновить версию в `installer.iss`, `build.py`, `version_info.txt`
4. Запустить тесты: `.\.venv\Scripts\python.exe -m pytest tests/ -v`
