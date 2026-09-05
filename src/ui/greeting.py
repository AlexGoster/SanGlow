from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.i18n import get_current_lang


class TimeOfDay(Enum):
    MORNING = "morning"
    DAY = "day"
    EVENING = "evening"
    NIGHT = "night"


_EMOJI = {
    TimeOfDay.MORNING: "\u2600\ufe0f",
    TimeOfDay.DAY: "\ud83c\udf1e",
    TimeOfDay.EVENING: "\ud83c\udf05",
    TimeOfDay.NIGHT: "\ud83c\udf19",
}


_GREETINGS = {
    "Русский": {
        TimeOfDay.MORNING: [
            "Доброе утро",
            "Утро начинается",
            "Доброе утро, {name}",
            "Просыпайся, {name}",
            "Утро, {name}",
        ],
        TimeOfDay.DAY: [
            "Добрый день",
            "Привет, {name}",
            "Хорошего дня, {name}",
            "День в ритме, {name}",
            "Привет, {name}",
        ],
        TimeOfDay.EVENING: [
            "Добрый вечер",
            "Вечерний ритм, {name}",
            "Вечер, {name}",
            "Отдыхай, {name}",
            "Вечер в ритме, {name}",
        ],
        TimeOfDay.NIGHT: [
            "Спокойной ночи",
            "Ночная музыка, {name}",
            "Тихий вечер, {name}",
            "Ночной микс, {name}",
            "Спокойной ночи, {name}",
        ],
    },
    "English": {
        TimeOfDay.MORNING: [
            "Good morning",
            "Rise and shine",
            "Good morning, {name}",
            "Wake up, {name}",
            "Morning, {name}",
        ],
        TimeOfDay.DAY: [
            "Good afternoon",
            "Hey, {name}",
            "Have a great day, {name}",
            "Day in rhythm, {name}",
            "Hello, {name}",
        ],
        TimeOfDay.EVENING: [
            "Good evening",
            "Evening vibe, {name}",
            "Evening, {name}",
            "Relax, {name}",
            "Evening in rhythm, {name}",
        ],
        TimeOfDay.NIGHT: [
            "Good night",
            "Night music, {name}",
            "Quiet evening, {name}",
            "Night mix, {name}",
            "Good night, {name}",
        ],
    },
    "Deutsch": {
        TimeOfDay.MORNING: [
            "Guten Morgen",
            "Der Morgen beginnt",
            "Guten Morgen, {name}",
            "Wach auf, {name}",
            "Morgen, {name}",
        ],
        TimeOfDay.DAY: [
            "Guten Tag",
            "Hallo, {name}",
            "Schönen Tag, {name}",
            "Tag im Rhythmus, {name}",
            "Hallo, {name}",
        ],
        TimeOfDay.EVENING: [
            "Guten Abend",
            "Abendstimmung, {name}",
            "Abend, {name}",
            "Entspann dich, {name}",
            "Abend im Rhythmus, {name}",
        ],
        TimeOfDay.NIGHT: [
            "Gute Nacht",
            "Nachtmusik, {name}",
            "Ruhiger Abend, {name}",
            "Nachtmix, {name}",
            "Gute Nacht, {name}",
        ],
    },
    "Français": {
        TimeOfDay.MORNING: [
            "Bonjour",
            "Le matin commence",
            "Bonjour, {name}",
            "Réveille-toi, {name}",
            "Matin, {name}",
        ],
        TimeOfDay.DAY: [
            "Bonjour",
            "Salut, {name}",
            "Bonne journée, {name}",
            "Jour en rythme, {name}",
            "Bonjour, {name}",
        ],
        TimeOfDay.EVENING: [
            "Bonsoir",
            "Ambiance du soir, {name}",
            "Soir, {name}",
            "Détends-toi, {name}",
            "Soir en rythme, {name}",
        ],
        TimeOfDay.NIGHT: [
            "Bonne nuit",
            "Musique nocturne, {name}",
            "Soirée calme, {name}",
            "Mix nocturne, {name}",
            "Bonne nuit, {name}",
        ],
    },
    "Español": {
        TimeOfDay.MORNING: [
            "Buenos días",
            "El día comienza",
            "Buenos días, {name}",
            "Despierta, {name}",
            "Mañana, {name}",
        ],
        TimeOfDay.DAY: [
            "Buenas tardes",
            "Hola, {name}",
            "Que tengas un buen día, {name}",
            "Día en ritmo, {name}",
            "Hola, {name}",
        ],
        TimeOfDay.EVENING: [
            "Buenas noches",
            "Ritmo nocturno, {name}",
            "Noche, {name}",
            "Relájate, {name}",
            "Noche en ritmo, {name}",
        ],
        TimeOfDay.NIGHT: [
            "Buenas noches",
            "Música nocturna, {name}",
            "Noche tranquila, {name}",
            "Mix nocturno, {name}",
            "Buenas noches, {name}",
        ],
    },
}


_MOOD_PLAYLISTS = {
    TimeOfDay.MORNING: [
        {"name": "Утренний подъем", "description": "Энергичные треки для начала дня", "genres": ["pop", "dance", "electronic"]},
        {"name": "Кофе и музыка", "description": "Спокойные треки для утреннего кофе", "genres": ["lofi", "jazz", "acoustic"]},
        {"name": "Зарядка", "description": "Мотивирующие треки для тренировки", "genres": ["workout", "hip-hop", "rock"]},
    ],
    TimeOfDay.DAY: [
        {"name": "Рабочий ритм", "description": "Фоновая музыка для работы", "genres": ["lofi", "ambient", "focus"]},
        {"name": "В хорошем настроении", "description": "Позитивные треки на весь день", "genres": ["pop", "indie", "alternative"]},
        {"name": "Дневной микс", "description": "Смесь разных жанров", "genres": ["pop", "rock", "hip-hop"]},
    ],
    TimeOfDay.EVENING: [
        {"name": "Вечерний чилл", "description": "Расслабляющая музыка после работы", "genres": ["lofi", "jazz", "r&b"]},
        {"name": "Закатные треки", "description": "Музыка для встречи заката", "genres": ["indie", "alternative", "dream-pop"]},
        {"name": "Вечерняя прогулка", "description": "Треки для вечерней прогулки", "genres": ["electronic", "chillwave", "synth-pop"]},
    ],
    TimeOfDay.NIGHT: [
        {"name": "Ночной джаз", "description": "Спокойный джаз для ночи", "genres": ["jazz", "bossa-nova", "lounge"]},
        {"name": "Звездная ночь", "description": "Атмосферная музыка для ночи", "genres": ["ambient", "space", "electronic"]},
        {"name": "Спокойной ночи", "description": "Тихие треки для засыпания", "genres": ["classical", "piano", "nature"]},
    ],
}


def get_time_of_day() -> TimeOfDay:
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return TimeOfDay.MORNING
    elif 12 <= hour < 18:
        return TimeOfDay.DAY
    elif 18 <= hour < 23:
        return TimeOfDay.EVENING
    else:
        return TimeOfDay.NIGHT


def get_greeting(username: str | None = None) -> Greeting:
    tod = get_time_of_day()
    lang = get_current_lang()
    greetings = _GREETINGS.get(lang, _GREETINGS["Русский"])
    text = greetings[tod][0]
    if "{name}" in text and username:
        safe_name = username[:50].strip() or "User"
        text = text.format(name=safe_name)
    return Greeting(text=text, time_of_day=tod, emoji=_EMOJI.get(tod, ""))


def get_suggested_playlists(user_likes: list[str] | None = None) -> list[dict]:
    tod = get_time_of_day()
    playlists = _MOOD_PLAYLISTS[tod]

    if user_likes:
        scored = []
        for pl in playlists:
            score = sum(1 for g in pl["genres"] if any(g.lower() in like.lower() for like in user_likes))
            scored.append((score, pl))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored]

    return playlists
