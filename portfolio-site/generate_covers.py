#!/usr/bin/env python3
"""Генерирует обложки для кворков Kwork (мин. 30КБ, мин. 660x440)."""

from PIL import Image, ImageDraw, ImageFont
import os, math

OUTPUT = os.path.dirname(os.path.abspath(__file__))
W, H = 1000, 625  # больше пикселей = больше КБ

try:
    FONT_BOLD = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 54)
    FONT_REG = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 26)
    FONT_PRICE = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 42)
    FONT_SMALL = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 20)
    FONT_TINY = ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", 14)
except:
    FONT_BOLD = FONT_REG = FONT_PRICE = FONT_SMALL = FONT_TINY = ImageFont.load_default()

THEME = [
    {
        "bg1": "#0f0c29", "bg2": "#302b63", "accent": "#667eea",
        "emoji": "🤖", "title": "Telegram-боты",
        "desc": "Разработка ботов под ключ на Python",
        "price": "от 1 000 ₽",
        "tags": ["Python", "aiogram", "API"],
    },
    {
        "bg1": "#1a0028", "bg2": "#3a1b5e", "accent": "#f093fb",
        "emoji": "📊", "title": "Парсинг данных",
        "desc": "Сбор информации с любых сайтов",
        "price": "от 1 500 ₽",
        "tags": ["Python", "BS4", "Pandas"],
    },
    {
        "bg1": "#0a1628", "bg2": "#1a3a5c", "accent": "#4facfe",
        "emoji": "⚡", "title": "Автоматизация",
        "desc": "Скрипты для любых рутинных задач",
        "price": "от 1 000 ₽",
        "tags": ["Python", "Скрипты", "Excel"],
    },
    {
        "bg1": "#0a1a10", "bg2": "#1a3a28", "accent": "#43e97b",
        "emoji": "🌐", "title": "Сайты / Лендинги",
        "desc": "Визитка, портфолио, лендинг",
        "price": "от 2 000 ₽",
        "tags": ["HTML", "CSS", "JS"],
    },
]

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

for i, t in enumerate(THEME):
    img = Image.new("RGB", (W, H), (20, 20, 30))
    draw = ImageDraw.Draw(img)

    c1 = hex_to_rgb(t["bg1"])
    c2 = hex_to_rgb(t["bg2"])
    accent = hex_to_rgb(t["accent"])

    # градиент
    for y in range(H):
        r = int(c1[0] + (c2[0] - c1[0]) * y / H)
        g = int(c1[1] + (c2[1] - c1[1]) * y / H)
        b = int(c1[2] + (c2[2] - c1[2]) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # --------------------------------------------------
    # много декоративных элементов для увеличения КБ
    # --------------------------------------------------

    # большие круги (glow-эффект)
    glow_circles = [
        (750, 100, 280), (200, 500, 220), (850, 450, 180), (100, 120, 150)
    ]
    for cx, cy, cr in glow_circles:
        for step in range(5):
            r2 = cr - step * 15
            if r2 < 10: break
            a = 20 - step * 3
            if a < 3: a = 3
            draw.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], fill=(*accent, a))

    # сетка из точек
    for gx in range(0, W, 25):
        for gy in range(0, H, 25):
            draw.ellipse([gx-1, gy-1, gx+1, gy+1], fill=(*accent, 8))

    # волнистые линии
    for wy in range(0, H, 40):
        pts = []
        for wx in range(0, W, 10):
            pts.append((wx, wy + 10 * math.sin(wx / 50)))
        for idx in range(len(pts) - 1):
            draw.line([pts[idx], pts[idx+1]], fill=(*accent, 10), width=1)

    # треугольники для геометрии
    for _ in range(15):
        tx1 = (_ * 73) % W
        ty1 = (_ * 97) % H
        tx2 = (tx1 + 40) % W
        ty2 = (ty1 + 20) % H
        tx3 = (tx1 + 10) % W
        ty3 = (ty1 + 60) % H
        draw.polygon([(tx1, ty1), (tx2, ty2), (tx3, ty3)], fill=(*accent, 6))

    # --------------------------------------------------
    # контент
    # --------------------------------------------------

    # эмодзи
    draw.text((60, 50), t["emoji"], fill=(255, 255, 255), font=ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", 80))

    # заголовок
    draw.text((60, 165), t["title"], fill=(255, 255, 255), font=FONT_BOLD)

    # описание
    draw.text((60, 240), t["desc"], fill=(220, 220, 220), font=FONT_REG)

    # плашка с ценой
    price_text = t["price"]
    pb = draw.textbbox((0, 0), price_text, font=FONT_PRICE)
    pw = pb[2] - pb[0]
    ph = pb[3] - pb[1]
    draw.rounded_rectangle([52, 320, 52 + pw + 24, 320 + ph + 18], radius=16, fill=(*accent, 190))
    draw.rounded_rectangle([52, 320, 52 + pw + 24, 320 + ph + 18], radius=16, outline=(255, 255, 255, 40), width=2)
    draw.text((64, 327), price_text, fill=(255, 255, 255), font=FONT_PRICE)

    # теги
    tag_x = 60
    for tag in t["tags"]:
        tb = draw.textbbox((0, 0), tag, font=FONT_SMALL)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
        draw.rounded_rectangle([tag_x - 8, 400, tag_x + tw + 14, 400 + th + 12], radius=10, fill=(255, 255, 255, 20))
        draw.rounded_rectangle([tag_x - 8, 400, tag_x + tw + 14, 400 + th + 12], radius=10, outline=(255, 255, 255, 20), width=1)
        draw.text((tag_x + 3, 405), tag, fill=(220, 220, 220), font=FONT_SMALL)
        tag_x += tw + 30

    # блок "Примеры работ"
    draw.text((60, 470), "Примеры:", fill=(180, 180, 180), font=FONT_TINY)
    examples = {
        0: "• Telegram-калькулятор с кнопками",
        1: "• Парсер Lenta.ru → Excel/PDF",
        2: "• Скрипты автоматизации отчётов",
        3: "• Адаптивный сайт-портфолио",
    }[i]
    draw.text((60, 493), examples, fill=(160, 160, 160), font=FONT_TINY)

    # нижняя плашка
    draw.rounded_rectangle([0, H - 6, W, H], radius=3, fill=(*accent, 70))

    # водяной знак
    draw.text((W - 230, H - 35), "@kall1shnik0vv", fill=(255, 255, 255, 45), font=FONT_TINY)

    safe_title = t['title'].lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = f"cover_{i+1}_{safe_title}.png"
    filepath = os.path.join(OUTPUT, filename)
    img.save(filepath, optimize=False)
    size_kb = os.path.getsize(filepath) / 1024
    print(f"✅ {filename} — {size_kb:.1f} КБ, {img.size[0]}x{img.size[1]}")

print(f"\nВсе обложки сохранены")
