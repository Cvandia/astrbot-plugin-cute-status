"""Validated AstrBot plugin settings."""

from dataclasses import dataclass
from math import isfinite
from typing import Mapping


@dataclass(frozen=True)
class Settings:
    nickname: str = "AstrBot"
    only_admin: bool = False
    to_me: bool = False
    cooldown: float = 10.0
    disk_path: str = "/"
    font_path: str = ""

    @classmethod
    def parse(cls, raw: Mapping):
        values = {k: raw.get(k, field.default) for k, field in cls.__dataclass_fields__.items()}
        for key in ("only_admin", "to_me"):
            if not isinstance(values[key], bool):
                raise ValueError(f"{key} 必须是布尔值")
        for key in ("nickname", "disk_path", "font_path"):
            if not isinstance(values[key], str):
                raise ValueError(f"{key} 必须是字符串")
        values["nickname"] = values["nickname"].strip()[:64] or "AstrBot"
        if not values["disk_path"].strip():
            raise ValueError("disk_path 不能为空")
        cd = float(values["cooldown"])
        if not isfinite(cd) or not 0 <= cd <= 3600:
            raise ValueError("cooldown 必须在 0–3600 秒之间")
        values["cooldown"] = cd
        return cls(**values)
