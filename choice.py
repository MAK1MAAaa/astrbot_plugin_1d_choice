from __future__ import annotations

import secrets
import unicodedata
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class InvalidReason(str, Enum):
    TOO_LONG = "题面超过长度上限"
    TOO_MANY = "选项数量超过上限"
    TOO_FEW = "没有给出至少两个选项"
    EMPTY = "存在空选项或只有不可见字符的选项"
    DUPLICATE = "存在相同的选项"
    NON_TEXT = "混入了图片等无法作为文字选项解析的消息段"


@dataclass(frozen=True, slots=True)
class ChoiceSettings:
    max_input_length: int = 2000
    max_options: int = 32
    fallback_cooldown_seconds: int = 10

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> ChoiceSettings:
        def integer(key: str, default: int, minimum: int) -> int:
            value = config.get(key, default)
            if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
                raise ValueError(f"配置 {key} 必须为不小于 {minimum} 的整数")
            return value

        return cls(
            max_input_length=integer("max_input_length", 2000, 2),
            max_options=integer("max_options", 32, 2),
            fallback_cooldown_seconds=integer("fallback_cooldown_seconds", 10, 0),
        )


@dataclass(frozen=True, slots=True)
class ChoiceQuestion:
    text: str
    options: tuple[str, ...] = ()
    reason: InvalidReason | None = None

    def choose(self) -> str:
        if self.reason is not None or len(self.options) < 2:
            raise ValueError("不能从无效选择题中抽取答案")
        return secrets.choice(self.options)


def comparison_key(option: str) -> str:
    normalized = unicodedata.normalize("NFKC", option)
    visible = "".join(
        char
        for char in normalized
        if unicodedata.category(char) not in {"Cf", "Cc"} or char.isspace()
    )
    return " ".join(visible.split()).casefold()


def parse_question(text: str, settings: ChoiceSettings) -> ChoiceQuestion | None:
    text = text.strip()
    if not text.startswith("1d"):
        return None
    if len(text) > settings.max_input_length:
        return ChoiceQuestion(text, reason=InvalidReason.TOO_LONG)
    body = text[2:].strip()
    options = tuple(option.strip() for option in body.split("还是"))
    if len(options) > settings.max_options:
        return ChoiceQuestion(text, reason=InvalidReason.TOO_MANY)
    keys = [comparison_key(option) for option in options]
    if not all(keys):
        return ChoiceQuestion(text, reason=InvalidReason.EMPTY)
    if len(options) < 2:
        return ChoiceQuestion(text, reason=InvalidReason.TOO_FEW)
    if len(set(keys)) != len(keys):
        return ChoiceQuestion(text, reason=InvalidReason.DUPLICATE)
    return ChoiceQuestion(text, options=options)


class FallbackCooldown:
    """Reserve before any await; bounded, expiring state prevents concurrent spam."""

    def __init__(self, seconds: int, max_entries: int = 2048):
        self.seconds = seconds
        self.max_entries = max_entries
        self._expires: OrderedDict[tuple[str, str], float] = OrderedDict()

    def reserve(self, key: tuple[str, str], now: float) -> bool:
        if self.seconds == 0:
            return True
        while self._expires and next(iter(self._expires.values())) <= now:
            self._expires.popitem(last=False)
        if self._expires.get(key, 0) > now:
            return False
        self._expires[key] = now + self.seconds
        self._expires.move_to_end(key)
        while len(self._expires) > self.max_entries:
            self._expires.popitem(last=False)
        return True

    def clear(self) -> None:
        self._expires.clear()
