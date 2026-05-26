#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dataset' / 'images'
OUT.mkdir(parents=True, exist_ok=True)

BG = '#f5efe2'
INK = '#2c241b'
ACCENT = '#a44d2a'
BLUE = '#2e6f95'
WATER = '#8fc7d9'
MIRROR = '#c7d7e8'
SHADOW = '#5f7d8a'

try:
    FONT = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 28)
    FONT_SMALL = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 22)
except Exception:
    FONT = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()


def save(img: Image.Image, name: str) -> None:
    img.save(OUT / name)


def draw_hat(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0, color: str = ACCENT) -> None:
    w = int(84 * scale)
    h = int(26 * scale)
    crown_w = int(42 * scale)
    crown_h = int(30 * scale)
    draw.ellipse((x, y, x + w, y + h), fill=color, outline=INK, width=3)
    cx = x + (w - crown_w) // 2
    cy = y - int(12 * scale)
    draw.rounded_rectangle((cx, cy, cx + crown_w, cy + crown_h), radius=int(8 * scale), fill=color, outline=INK, width=3)


def draw_person(draw: ImageDraw.ImageDraw, x: int, y: int, hats: int = 1) -> None:
    draw.ellipse((x + 28, y, x + 72, y + 44), fill='#f0c7a4', outline=INK, width=3)
    draw.line((x + 50, y + 44, x + 50, y + 120), fill=INK, width=5)
    draw.line((x + 50, y + 60, x + 15, y + 95), fill=INK, width=5)
    draw.line((x + 50, y + 60, x + 85, y + 95), fill=INK, width=5)
    draw.line((x + 50, y + 120, x + 25, y + 170), fill=INK, width=5)
    draw.line((x + 50, y + 120, x + 75, y + 170), fill=INK, width=5)
    if hats >= 1:
        draw_hat(draw, x + 8, y - 10, scale=0.8)
    if hats >= 2:
        draw_hat(draw, x + 5, y - 34, scale=0.55, color='#cf7b4d')


def mirror_mismatch() -> None:
    img = Image.new('RGB', (900, 640), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 900, 640), fill=BG)
    d.rounded_rectangle((480, 70, 830, 560), radius=18, fill=MIRROR, outline=INK, width=5)
    d.text((58, 34), 'SB-002 mirror mismatch', fill=INK, font=FONT)
    draw_person(d, 140, 210, hats=1)
    draw_person(d, 590, 210, hats=2)
    d.text((110, 530), 'real figure', fill=INK, font=FONT_SMALL)
    d.text((615, 530), 'mirror', fill=INK, font=FONT_SMALL)
    save(img, 'mirror-hat-mismatch.png')


def water_reflection_mismatch() -> None:
    img = Image.new('RGB', (900, 640), '#e9f4fb')
    d = ImageDraw.Draw(img)
    d.rectangle((0, 390, 900, 640), fill=WATER)
    d.text((58, 34), 'SB-003 water reflection mismatch', fill=INK, font=FONT)
    # real buoys
    for x in (180, 360, 540):
        d.line((x, 260, x, 392), fill=INK, width=5)
        d.ellipse((x - 35, 225, x + 35, 295), fill=ACCENT, outline=INK, width=4)
    # reflection only shows two
    for x in (180, 360):
        d.ellipse((x - 35, 470, x + 35, 540), fill='#c97551', outline=INK, width=4)
    d.text((120, 575), 'three buoys above water, two reflected below', fill=INK, font=FONT_SMALL)
    save(img, 'water-reflection-buoys.png')


def six_finger_hand() -> None:
    img = Image.new('RGB', (900, 640), BG)
    d = ImageDraw.Draw(img)
    d.text((58, 34), 'SB-004 six-finger hand', fill=INK, font=FONT)
    # palm
    d.rounded_rectangle((300, 260, 520, 470), radius=34, fill='#f0c7a4', outline=INK, width=5)
    # thumb
    d.rounded_rectangle((235, 345, 345, 415), radius=28, fill='#f0c7a4', outline=INK, width=5)
    # six fingers
    for i in range(6):
        x = 290 + i * 42
        d.rounded_rectangle((x, 120, x + 36, 285), radius=18, fill='#f0c7a4', outline=INK, width=5)
    d.text((250, 535), 'count the visible fingers on the raised hand', fill=INK, font=FONT_SMALL)
    save(img, 'six-finger-hand.png')


def garbled_sign() -> None:
    img = Image.new('RGB', (900, 640), '#f2ead7')
    d = ImageDraw.Draw(img)
    d.text((58, 34), 'SB-005 garbled sign text', fill=INK, font=FONT)
    d.rectangle((230, 210, 670, 400), fill='#f6d28f', outline=INK, width=6)
    d.text((310, 275), 'P1Z7A?', fill=ACCENT, font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 72) if Path('/System/Library/Fonts/Supplemental/Arial Bold.ttf').exists() else FONT)
    d.line((450, 400, 450, 560), fill=INK, width=8)
    d.text((230, 515), 'intentionally malformed storefront lettering', fill=INK, font=FONT_SMALL)
    save(img, 'garbled-sign-text.png')


def detached_glasses() -> None:
    img = Image.new('RGB', (900, 640), BG)
    d = ImageDraw.Draw(img)
    d.text((58, 34), 'SB-006 detached glasses arm', fill=INK, font=FONT)
    d.ellipse((250, 130, 650, 530), fill='#f0c7a4', outline=INK, width=5)
    # eyes + glasses
    d.ellipse((335, 280, 425, 350), outline=INK, width=6)
    d.ellipse((475, 280, 565, 350), outline=INK, width=6)
    d.line((425, 315, 475, 315), fill=INK, width=6)
    d.line((300, 310, 335, 315), fill=INK, width=6)  # left arm attached
    d.line((565, 270, 610, 250), fill=INK, width=6)  # right arm floating/detached high
    d.arc((415, 360, 485, 430), 10, 170, fill=INK, width=5)
    d.text((275, 555), 'one glasses arm floats above the face instead of attaching', fill=INK, font=FONT_SMALL)
    save(img, 'detached-glasses-arm.png')


def shadow_mismatch() -> None:
    img = Image.new('RGB', (900, 640), '#eef3dc')
    d = ImageDraw.Draw(img)
    d.rectangle((0, 470, 900, 640), fill='#d8c7a3')
    d.text((58, 34), 'SB-007 shadow direction mismatch', fill=INK, font=FONT)
    # posts
    for x in (280, 560):
        d.rectangle((x, 220, x + 40, 470), fill='#8c5a3c', outline=INK, width=4)
    # contradictory shadows
    d.polygon([(320,470),(470,520),(470,560),(320,500)], fill=SHADOW)
    d.polygon([(560,470),(410,520),(410,560),(560,500)], fill=SHADOW)
    d.text((205, 555), 'the two posts cast shadows in opposite directions', fill=INK, font=FONT_SMALL)
    save(img, 'shadow-direction-mismatch.png')




def repeated_chairs_count() -> None:
    img = Image.new('RGB', (900, 640), '#efe7da')
    d = ImageDraw.Draw(img)
    d.text((58, 34), 'SB-008 repeated chair count', fill=INK, font=FONT)
    d.ellipse((260, 250, 640, 430), fill='#d4b08a', outline=INK, width=5)
    chair_positions = [(220, 220), (620, 220), (230, 420), (610, 420), (425, 160)]
    for x, y in chair_positions:
        d.rectangle((x, y, x + 60, y + 70), fill='#8c5a3c', outline=INK, width=4)
        d.line((x + 10, y + 70, x + 5, y + 120), fill=INK, width=4)
        d.line((x + 50, y + 70, x + 55, y + 120), fill=INK, width=4)
    d.text((240, 555), 'count the chairs visible around the table', fill=INK, font=FONT_SMALL)
    save(img, 'repeated-chairs-count.png')


def detached_mug_handle() -> None:
    img = Image.new('RGB', (900, 640), BG)
    d = ImageDraw.Draw(img)
    d.text((58, 34), 'SB-009 detached mug handle', fill=INK, font=FONT)
    d.rounded_rectangle((280, 190, 560, 470), radius=24, fill='#d9e4ef', outline=INK, width=6)
    d.arc((585, 255, 690, 380), 35, 325, fill=INK, width=8)
    d.text((250, 525), 'the mug handle floats apart instead of attaching to the mug', fill=INK, font=FONT_SMALL)
    save(img, 'detached-mug-handle.png')


def transparent_glasses_count() -> None:
    img = Image.new('RGBA', (900, 640), '#edf4f7')
    d = ImageDraw.Draw(img, 'RGBA')
    d.text((58, 34), 'SB-010 transparent glasses count', fill=INK, font=FONT)
    for x in (220, 410, 600):
        d.rounded_rectangle((x, 210, x + 90, 430), radius=16, outline=INK, width=5, fill=(255,255,255,80))
        d.ellipse((x + 10, 380, x + 80, 445), outline=INK, width=4, fill=(255,255,255,40))
    d.text((245, 525), 'count the transparent drinking glasses on the shelf', fill=INK, font=FONT_SMALL)
    img.convert('RGB').save(OUT / 'transparent-glasses-count.png')


def main() -> None:
    mirror_mismatch()
    water_reflection_mismatch()
    six_finger_hand()
    garbled_sign()
    detached_glasses()
    shadow_mismatch()
    repeated_chairs_count()
    detached_mug_handle()
    transparent_glasses_count()


if __name__ == '__main__':
    main()
