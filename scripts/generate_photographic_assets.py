#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'dataset' / 'sources'
OUT = ROOT / 'dataset' / 'images'
OUT.mkdir(parents=True, exist_ok=True)

try:
    FONT_BIG = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 70)
    FONT_MED = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf', 32)
except Exception:
    FONT_BIG = ImageFont.load_default()
    FONT_MED = ImageFont.load_default()


def save(img: Image.Image, name: str) -> None:
    img.save(OUT / name, quality=95)


def garbled_library_sign() -> None:
    img = Image.open(SRC / 'library-road-sign-source.jpg').convert('RGB')
    d = ImageDraw.Draw(img)
    # cover central text zone with fresh sign-blue patch, then add garbled text
    d.rounded_rectangle((160, 280, 705, 545), radius=20, fill=(27, 76, 155))
    d.text((240, 355), 'L1BRXRY?', fill='white', font=FONT_BIG)
    d.text((258, 435), 'WAYF1ND', fill='white', font=FONT_MED)
    save(img, 'photo-garbled-library-sign.jpg')


def duplicated_hat_portrait() -> None:
    img = Image.open(SRC / 'portrait-hat-man-source.jpg').convert('RGB')
    # crop original hat area, resize smaller, and paste above original hat for a realistic-ish duplication
    hat = img.crop((820, 120, 1820, 980)).resize((700, 600))
    hat = hat.filter(ImageFilter.GaussianBlur(radius=0.4))
    canvas = img.copy()
    canvas.paste(hat, (950, 0))
    save(canvas, 'photo-duplicated-hat-portrait.jpg')


def five_chairs_photo() -> None:
    img = Image.open(SRC / 'table-and-chairs-source.jpg').convert('RGB')
    chair = img.crop((215, 35, 285, 155)).resize((58, 94))
    canvas = img.resize((885, 663))
    chair = chair.resize((175, 282))
    # add a fifth chair on the near-right side
    canvas.paste(chair, (640, 245))
    save(canvas, 'photo-five-chairs-table.jpg')


def three_wheel_bicycle() -> None:
    img = Image.open(SRC / 'bicycle-park-source.jpg').convert('RGB')
    canvas = img.copy()
    wheel = img.crop((760, 360, 1285, 885)).resize((340, 340)).convert('RGBA')
    mask = Image.new('L', wheel.size, 0)
    md = ImageDraw.Draw(mask)
    md.ellipse((8, 8, wheel.size[0] - 8, wheel.size[1] - 8), fill=255)
    wheel.putalpha(mask)
    wheel = wheel.filter(ImageFilter.GaussianBlur(radius=0.2))
    canvas = canvas.convert('RGBA')
    canvas.alpha_composite(wheel, (520, 505))
    canvas = canvas.convert('RGB')
    save(canvas, 'photo-three-wheel-bicycle.jpg')


def main() -> None:
    garbled_library_sign()
    duplicated_hat_portrait()
    five_chairs_photo()
    three_wheel_bicycle()


if __name__ == '__main__':
    main()
