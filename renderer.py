"""Self-contained pastel status card; no browser or remote asset requests."""
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .status import Snapshot, format_uptime

FONT = Path(__file__).parent / "assets" / "CuteStatusSans.otf"
COLORS = ("#74b9ee", "#eea5bf", "#efb396", "#b2a2ce")


def render(data: Snapshot, nickname: str, font_path: str = "") -> bytes:
    font_file = font_path or str(FONT)
    def font(size):
        return ImageFont.truetype(font_file, size)

    image = Image.new("RGB", (1000, 1340), "#fff6f4")
    draw = ImageDraw.Draw(image)
    ink, muted = "#695e70", "#9b8b9a"

    def text(x, y, value, size=26, fill=ink, max_width=820):
        value = str(value).replace("\n", " ")
        fnt = font(size)
        while value and draw.textlength(value, font=fnt) > max_width:
            value = value[:-2] + "…" if len(value) > 2 else ""
        draw.text((x, y), value, font=fnt, fill=fill)

    # All decorative artwork is drawn locally.
    for x, y, r, color in [(40, 50, 120, "#fce4ee"), (880, 120, 160, "#e7f2fc"),
                            (900, 1260, 130, "#f2e8fa")]:
        draw.ellipse((x-r, y-r, x+r, y+r), fill=color)
    text(70, 58, "CUTE STATUS", 26, muted)
    text(70, 103, nickname, 54, max_width=650)
    text(73, 185, "今天也在元气满满地运行中", 26, muted)
    # Little cat mascot.
    draw.polygon([(791, 109), (789, 59), (832, 91), (873, 90), (918, 59), (916, 115)], fill="#fffdfb", outline=ink, width=3)
    draw.ellipse((786, 82, 922, 183), fill="#fffdfb", outline=ink, width=3)
    for x in (826, 880):
        draw.ellipse((x, 121, x+7, 132), fill=ink)
    draw.line([(847, 143), (854, 149), (861, 143)], fill=ink, width=3)
    for x in (808, 891):
        draw.ellipse((x, 140, x+17, 149), fill="#f3b4c9")

    freq = f"{data.frequency:.2f} GHz" if data.frequency is not None else "N/A GHz"
    rows = [("CPU", data.cpu_percent, f"{data.cores} cores · {freq}"),
            ("RAM", data.ram.percent, f"{data.ram.used:.2f} / {data.ram.total:.2f} GiB"),
            ("SWAP", data.swap.percent, f"{data.swap.used:.2f} / {data.swap.total:.2f} GiB"),
            ("DISK", data.disk.percent, f"{data.disk.used:.2f} / {data.disk.total:.2f} GiB")]
    for idx, (name, percent, detail) in enumerate(rows):
        y, color = 272 + idx*166, COLORS[idx]
        draw.rounded_rectangle((60, y, 940, y+146), radius=28, fill="white")
        ring = (88, y+24, 186, y+122)
        draw.arc(ring, -90, 270, fill="#f3eef2", width=12)
        if percent > 0:
            draw.arc(ring, -90, -90+min(100, max(0, percent))*3.6, fill=color, width=12)
        text(108, y+57, f"{percent:.0f}%", 20, max_width=80)
        text(220, y+20, name, 30, color)
        text(220, y+67, detail, 29)
        draw.rounded_rectangle((220, y+118, 902, y+125), radius=3, fill="#f3eef2")
        if percent > 0:
            draw.rounded_rectangle((220, y+118, 220+682*min(100, percent)/100, y+125), radius=3, fill=color)

    draw.rounded_rectangle((60, 956, 940, 1235), radius=28, fill="#fffcfd")
    for i, (label, value) in enumerate([
        ("处理器", data.processor), ("系统", data.system),
        ("框架", f"AstrBot · Cute Status 1.0.0 · {data.plugins} plugins"),
        ("进程运行", format_uptime(data.bot_uptime)),
        ("系统运行", format_uptime(data.system_uptime)),
    ]):
        text(88, 974+i*49, label, 23, muted, 160)
        text(260, 974+i*49, value, 23, max_width=640)
    text(70, 1272, data.timestamp, 22, muted)
    text(700, 1272, "Have a cute day!", 22, muted, 240)
    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    return output.getvalue()
