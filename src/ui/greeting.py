from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


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


@dataclass
class Greeting:
    text: str
    time_of_day: TimeOfDay
    emoji: str = ""


_GREETINGS = {
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
    text = random.choice(_GREETINGS[tod])
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
