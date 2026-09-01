from __future__ import annotations

import random


class MathCaptcha:
    def __init__(self) -> None:
        self._a = random.randint(1, 20)
        self._b = random.randint(1, 20)
        self._op = random.choice(["+", "-", "*"])
        if self._op == "+":
            self._answer = self._a + self._b
        elif self._op == "-":
            if self._a < self._b:
                self._a, self._b = self._b, self._a
            self._answer = self._a - self._b
        else:
            self._a = random.randint(1, 10)
            self._b = random.randint(1, 10)
            self._answer = self._a * self._b

    @property
    def question(self) -> str:
        return f"What is {self._a} {self._op} {self._b}?"

    def check(self, answer: str) -> bool:
        try:
            return int(answer.strip()) == self._answer
        except (ValueError, TypeError):
            return False
