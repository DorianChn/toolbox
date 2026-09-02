"""Render a terminal-style demo GIF for devcapsule.

Pipeline: PIL frames -> ffmpeg -> demo.gif
Content is the *real* output of the capsule CLI against a real repo
(traceplay/v0.1.0), captured earlier. We add a typewriter effect so the
animation reads naturally.

Usage:
    python render.py   # writes frames/*.png then demo.gif
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
FRAMES = HERE / "frames"
OUT = HERE / "demo.gif"

# --- terminal palette ---
BG = (16, 18, 24, 255)
FG = (220, 224, 232)
DIM = (120, 128, 140)
PROMPT = (80, 200, 120)
ACCENT = (80, 160, 255)
GOLD = (230, 190, 90)
WARN = (230, 120, 120)

W, H = 820, 520
PAD = 28
LINE_H = 26
PROMPT_STR = "~/traceplay $ "
FONT_MONO = "C:/Windows/Fonts/consola.ttf"
FONT_CJK = "C:/Windows/Fonts/simhei.ttf"

_font_cache = {}


def f(size: int) -> ImageFont.FreeTypeFont:
    key = size
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_MONO, size)
    return _font_cache[key]


def row_color(typ: str):
    return {"cmd": FG, "out": FG, "dim": DIM, "accent": ACCENT, "gold": GOLD, "warn": WARN}[typ]


# (type, text) -- ASCII only to avoid font fallback issues
SCENES = [
    [
        ("cmd", "capsule init"),
        ("out", "[ok] store at ~/.devcapsule/capsules.db"),
        ("out", "[ok] post-commit hook installed"),
        ("dim", ""),
        ("dim", "# devcapsule now watches every commit automatically."),
    ],
    [
        ("cmd", "capsule backfill --all"),
        ("gold", "8c7c1e0  captured:bugfix"),
        ("gold", "3d858e3  captured:bugfix"),
        ("gold", "0f2f7d2  captured:feature"),
        ("gold", "863ceb2  captured:chore"),
        ("dim", "   ... 4 commits distilled into capsules"),
    ],
    [
        ("cmd", "capsule show 6"),
        ("dim", "capsule #6  bugfix  v0.1.0  8c7c1e0c"),
        ("out", "  problem:  CLI lacked input validation guards, mishandled"),
        ("out", "            HTTP status codes, fragile gzip decompression."),
        ("accent", "  solution: entry-point guard + faithful status codes"),
        ("accent", "            + robust gzip streaming, docs synced."),
        ("warn", "  gotcha:   do NOT skip validation at CLI entry -- later"),
        ("warn", "            handlers leave you open to arg injection."),
    ],
    [
        ("cmd", "capsule search \"gzip decompression\""),
        ("out", "[6] 0.58  bugfix  v0.1.0"),
        ("out", "     CLI ... fragile gzip decompression logic ..."),
        ("out", "[8] 0.38  bugfix  v0.1.0"),
        ("out", "     traceplay config was incomplete ..."),
        ("dim", ""),
        ("gold", "# the exact bug you fixed, back in one query."),
    ],
]


def draw(scene: list[tuple[str, str]], rows_done: int, partial: str | None) -> Image.Image:
    img = Image.new("RGBA", (W, H), BG)
    d = ImageDraw.Draw(img)

    # window title bar
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([PAD + i * 22, PAD - 8, PAD + i * 22 + 12, PAD + 4], fill=c)
    d.text((W - PAD - 200, PAD - 14), "capsule -- demo", font=f(13), fill=DIM)

    y = PAD + 22
    font_cmd = f(17)
    font_out = f(16)

    # measure prompt text width once
    prompt_w = d.textlength(PROMPT_STR, font=font_cmd)
    cmd_x = PAD + int(prompt_w) + 10

    for i in range(rows_done):
        typ, text = scene[i]
        if typ == "cmd":
            d.text((PAD, y), PROMPT_STR, font=font_cmd, fill=PROMPT)
            d.text((cmd_x, y), text, font=font_cmd, fill=FG)
        else:
            d.text((PAD, y), text, font=font_out, fill=row_color(typ))
        y += LINE_H

    if partial is not None and rows_done < len(scene):
        typ, full = scene[rows_done]
        if typ == "cmd":
            d.text((PAD, y), PROMPT_STR, font=font_cmd, fill=PROMPT)
            d.text((cmd_x, y), partial, font=font_cmd, fill=FG)
        else:
            d.text((PAD, y), partial, font=font_out, fill=row_color(typ))

    return img


def main():
    if FRAMES.exists():
        for f_ in FRAMES.glob("*.png"):
            f_.unlink()
    FRAMES.mkdir(exist_ok=True)

    fps = 20
    frames: list[Image.Image] = []

    for scene in SCENES:
        for row_i, (typ, text) in enumerate(scene):
            if text == "":
                continue
            # type out the row
            for k in range(1, len(text) + 1):
                frames.append(draw(scene, row_i, text[:k]))
            for _ in range(2):
                frames.append(draw(scene, row_i + 1, None))
        # hold the full scene briefly
        for _ in range(int(fps * 0.8)):
            frames.append(draw(scene, len(scene), None))

    print(f"writing {len(frames)} frames ...")
    for i, img in enumerate(frames):
        img.convert("RGB").save(FRAMES / f"{i:04d}.png")

    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(FRAMES / "%04d.png"),
        "-vf", "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
        "-loop", "0",
        str(OUT),
    ]
    print("running ffmpeg ...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stderr)
        raise SystemExit(res.returncode)
    print(f"done -> {OUT}  ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
