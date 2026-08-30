<p align="center">
  <img src="assets/icon.png" width="150" alt="SanGlow Logo">
</p>

<h1 align="center">SanGlow</h1>

<p align="center">
  <strong>Персональный музыкальный плеер с импортом из 6 сервисов</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/PyQt6-GUI-41CD52?style=flat-square&logo=qt&logoColor=white">
  <img src="https://img.shields.io/badge/Spotify-1DB954?style=flat-square&logo=spotify&logoColor=white">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square">
  <img src="https://img.shields.io/github/v/release/AlexGoster/sanglow?style=flat-square&color=e8734a">
</p>

<p align="center">
  <a href="https://github.com/AlexGoster/sanglow/releases/latest">
    <img src="https://img.shields.io/badge/Download-Latest_Release-e8734a?style=for-the-badge&logo=github&logoColor=white">
  </a>
</p>

<p align="center">
  <sub>Windows · macOS · Linux — все сборки в одном релизе</sub>
</p>

---

## Возможности

| | Функция | Описание |
|---|---------|----------|
| 🎵 | **Импорт** | Spotify, YouTube Music, Yandex Music, SoundCloud, Telegram, Zvuk |
| 🔍 | **Поиск** | Поиск треков, артистов, плейлистов |
| 🎨 | **Тёмная тема** | Минималистичный дизайн в стиле LANE |
| ⏩ | **Скорость** | Настройка темпа 0.25x – 2.0x |
| ❤️ | **Лайки** | Отмечай любимые треки |
| ⭐ | **Избранное** | Коллекция избранных треков |
| 💬 | **Комментарии** | Оставляй комментарии к трекам |
| 🌊 | **Волны** | Создавай свои плейлисты-волны |
| 🔐 | **Безопасность** | JWT + bcrypt + AES шифрование |
| 📱 | **Профили** | Регистрация, вход, история |

---

## Поддерживаемые сервисы

| Сервис | Поиск | Плейлисты | URL-импорт | Качество |
|--------|:-----:|:---------:|:----------:|:--------:|
| **Spotify** | ✅ | ✅ | ✅ | Превью |
| **YouTube Music** | ✅ | ✅ | ✅ | Превью |
| **Yandex Music** | ✅ | ✅ | ✅ | Превью |
| **SoundCloud** | ✅ | ✅ | ✅ | Превью |
| **Telegram** | ✅ | ✅ | ✅ | Аудио |
| **Zvuk** | ✅ | ✅ | ✅ | FLAC |

---

## Установка

Перейди в раздел [**Releases**](https://github.com/AlexGoster/sanglow/releases/latest) и скачай файл для своей ОС:

| ОС | Файл | Установка |
|----|------|-----------|
| **Windows** | `sanglow_setup.exe` | Запусти установщик |
| **Windows (portable)** | `SanGlow-Windows.zip` | Распакуй → `SanGlow.exe` |
| **macOS** | `SanGlow-macOS.dmg` | Открой .dmg → перетащи в Applications |
| **Linux** | `SanGlow-Linux.tar.gz` | `tar -xzf` → `./SanGlow` |



## Структура проекта

```
SanGlow/
├── assets/
├── config/
│   └── settings.py
├── src/
│   ├── auth/
│   ├── importers/
│   ├── models/
│   ├── player/
│   ├── social/
│   ├── spotify/
│   ├── ui/
│   ├── utils/
│   └── main.py
├── tests/
├── .github/workflows/
├── build.py
├── installer.iss
├── pyproject.toml
└── README.md
```

---

## Технологии

| Компонент | Технология |
|-----------|-----------|
| GUI | PyQt6 |
| Плеер | pygame-ce |
| БД | SQLAlchemy + SQLite |
| API | spotipy, httpx, zvuk-music |
| Безопасность | PyJWT, bcrypt, cryptography |
| Сборка | PyInstaller + Inno Setup |
| CI/CD | GitHub Actions |

---

## Лицензия

[MIT License](LICENSE) — 2024-2026 AlexGoster
