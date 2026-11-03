"""System metrics, independent of AstrBot. Call collect() in a worker thread."""
import platform
import time
from dataclasses import dataclass
from datetime import datetime

import psutil


@dataclass(frozen=True)
class Resource:
    used: float
    total: float
    percent: float


@dataclass(frozen=True)
class Snapshot:
    cpu_percent: float
    cores: int
    frequency: float | None
    ram: Resource
    swap: Resource
    disk: Resource
    system: str
    processor: str
    bot_uptime: int
    system_uptime: int
    plugins: int
    timestamp: str


def resource(value) -> Resource:
    return Resource(value.used / 1024**3, value.total / 1024**3, float(value.percent))


def format_uptime(seconds: int) -> str:
    days, remainder = divmod(max(0, int(seconds)), 86400)
    hours, remainder = divmod(remainder, 3600)
    return f"{days}d {hours:02}h {remainder // 60:02}m"


def collect(disk_path: str, plugins: int) -> Snapshot:
    cpu = psutil.cpu_percent(interval=0.5)
    try:
        freq = psutil.cpu_freq()
        frequency = freq.current / 1000 if freq and freq.current > 0 else None
    except (OSError, NotImplementedError):
        frequency = None
    ram, swap = psutil.virtual_memory(), psutil.swap_memory()
    disk = psutil.disk_usage(disk_path)
    now = time.time()
    try:
        started = psutil.Process().create_time()
    except psutil.Error:
        started = now
    return Snapshot(
        cpu, psutil.cpu_count(logical=False) or psutil.cpu_count() or 1,
        frequency, resource(ram), resource(swap), resource(disk),
        f"{platform.system()} {platform.release()}",
        platform.processor() or platform.machine() or "Unknown CPU",
        max(0, int(now - started)), max(0, int(now - psutil.boot_time())),
        plugins, datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
    )


def text_status(data: Snapshot, nickname: str) -> str:
    rows = [f"{nickname} · 运行状态", f"CPU: {data.cpu_percent:.1f}% / {data.cores} cores"]
    for name in ("ram", "swap", "disk"):
        item = getattr(data, name)
        rows.append(f"{name.upper()}: {item.used:.2f} / {item.total:.2f} GiB ({item.percent:.1f}%)")
    rows.extend([f"AstrBot 进程运行: {format_uptime(data.bot_uptime)}",
                 f"系统运行: {format_uptime(data.system_uptime)}", f"已启用插件: {data.plugins}"])
    return "\n".join(rows)
