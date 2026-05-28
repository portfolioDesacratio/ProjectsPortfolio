# парсер новостей с lenta.ru
# собирает заголовки, выводит в консоль и сохраняет
# форматы: html (красивый), pdf, xlsx, csv

import os
import sys
import csv
import logging
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import pandas as pd

# логи
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# чтоб нас не заблочили
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def parse_news(max_pages=3):
    """парсим новости с ленты"""
    all_news = []
    base = "https://lenta.ru"

    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{base}/parts/news/"
        else:
            url = f"{base}/parts/news/{page}/"

        logger.info(f"качаю стр {page}: {url}")
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"не загрузилось {url}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        items = soup.select("a._topnews, div.item, a.card-mini")
        if not items:
            items = soup.find_all("a", class_=True)

        for item in items:
            title = ""
            link = ""

            if item.name == "a":
                title = item.get_text(strip=True)
                link = item.get("href", "")
            else:
                a_tag = item.find("a")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    link = a_tag.get("href", "")
                else:
                    title = item.get_text(strip=True)

            if not title or len(title) < 5:
                continue

            if link and not link.startswith("http"):
                if link.startswith("/"):
                    link = base + link
                else:
                    link = base + "/" + link

            time_text = ""
            time_tag = item.find("time")
            if time_tag:
                time_text = time_tag.get_text(strip=True)
            if not time_text:
                t = item.find("span", class_=lambda c: c and "time" in c.lower()) if hasattr(item, 'find') else None
                if t:
                    time_text = t.get_text(strip=True)
            if not time_text:
                time_text = datetime.now().strftime("%H:%M")

            category = ""
            cat_tag = item.find("span", class_=lambda c: c and ("rubric" in c.lower() or "category" in c.lower())) if hasattr(item, 'find') else None
            if cat_tag:
                category = cat_tag.get_text(strip=True)
            if not category:
                category = "новости"

            all_news.append({
                "title": title,
                "link": link,
                "time": time_text,
                "category": category,
            })

        logger.info(f"после стр {page}: всего {len(all_news)}")

    # убираем дубликаты
    seen = set()
    unique = []
    for n in all_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            unique.append(n)

    logger.info(f"уникальных: {len(unique)}")
    return unique


def to_excel(news, filename=None):
    """сохраняем в эксель"""
    if not filename:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"news_lenta_{now}.xlsx"

    df = pd.DataFrame(news)
    df.columns = ["Заголовок", "Ссылка", "Время", "Категория"]
    df.to_excel(filename, index=False, engine="openpyxl")
    print(f"💾 сохранено: {filename}")
    return filename


def to_csv(news, filename=None):
    """сохраняем в csv"""
    if not filename:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"news_lenta_{now}.csv"

    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["title", "link", "time", "category"])
        w.writeheader()
        w.writerows(news)

    print(f"💾 сохранено: {filename}")
    return filename


def to_html(news, filename=None):
    """сохраняем в красивый html файл"""
    if not filename:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"news_lenta_{now}.html"

    # собираем строки новостей
    rows_html = ""
    for i, item in enumerate(news, 1):
        rows_html += f"""
        <tr>
            <td class="num">{i}</td>
            <td class="time">{item['time']}</td>
            <td class="cat"><span class="tag">{item['category']}</span></td>
            <td class="title"><a href="{item['link']}" target="_blank">{item['title']}</a></td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Новости Lenta.ru — {datetime.now().strftime('%d.%m.%Y')}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0f0f1a;
    color: #e0e0e0;
    padding: 40px 20px;
    min-height: 100vh;
}}
.container {{ max-width: 900px; margin: 0 auto; }}
.header {{
    text-align: center;
    margin-bottom: 40px;
    padding: 30px;
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border-radius: 20px;
    border: 1px solid rgba(255,255,255,0.05);
}}
.header h1 {{
    font-size: 2rem;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}}
.header p {{ color: #888; font-size: 0.95rem; }}
.header .count {{
    display: inline-block;
    margin-top: 12px;
    padding: 6px 18px;
    background: rgba(102,126,234,0.15);
    color: #667eea;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}}
table {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 6px;
}}
thead th {{
    text-align: left;
    padding: 12px 16px;
    color: #666;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}}
tbody tr {{
    background: #1a1a2e;
    border-radius: 12px;
    transition: all 0.2s;
    cursor: pointer;
}}
tbody tr:hover {{
    background: #1e1e36;
    transform: translateX(4px);
}}
tbody td {{
    padding: 14px 16px;
    border: none;
}}
td.num {{
    color: #444;
    font-size: 0.85rem;
    width: 40px;
    font-weight: 600;
}}
td.time {{
    color: #888;
    font-size: 0.85rem;
    width: 60px;
    white-space: nowrap;
}}
td.cat {{ width: 100px; }}
.tag {{
    display: inline-block;
    padding: 3px 10px;
    border-radius: 6px;
    background: rgba(102,126,234,0.1);
    color: #667eea;
    font-size: 0.75rem;
    font-weight: 600;
}}
td.title a {{
    color: #e0e0e0;
    text-decoration: none;
    font-size: 0.95rem;
    line-height: 1.4;
}}
td.title a:hover {{ color: #667eea; }}
.footer {{
    text-align: center;
    margin-top: 40px;
    padding: 20px;
    color: #444;
    font-size: 0.8rem;
    border-top: 1px solid rgba(255,255,255,0.05);
}}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>📰 Новости Lenta.ru</h1>
        <p>Собрано {datetime.now().strftime('%d.%m.%Y в %H:%M')}</p>
        <div class="count">Найдено {len(news)} новостей</div>
    </div>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Время</th>
                <th>Категория</th>
                <th>Заголовок</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
    <div class="footer">
        Сгенерировано парсером новостей • lenta.ru
    </div>
</div>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"💾 сохранено: {filename}")
    return filename


def to_pdf(news, filename=None):
    """сохраняем в pdf (сначала html, потом конвертим)"""
    if not filename:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"news_lenta_{now}.pdf"

    # сначала создаём html
    html_file = filename.replace(".pdf", ".html")
    to_html(news, html_file)

    try:
        from weasyprint import HTML
        HTML(filename=html_file).write_pdf(filename)
        print(f"📄 сохранил PDF: {filename}")
        # удаляем временный html
        os.remove(html_file)
        return filename
    except Exception as e:
        print(f"❌ не смог сделать PDF: {e}")
        print(f"   но HTML остался: {html_file}")
        return None


def main():
    print("📰 ПАРСЕР НОВОСТЕЙ LENTA.RU")
    print("=" * 30)

    try:
        pages = input("сколько страниц? (1-5, enter = 3): ")
        pages = int(pages) if pages.strip() else 3
        pages = max(1, min(pages, 5))
    except:
        pages = 3

    print(f"парсю {pages} стр...")
    news = parse_news(max_pages=pages)

    if not news:
        print("ничего не нашел :(")
        return

    # показываем первые 5
    print(f"\nнашел {len(news)} новостей. первые 5:")
    print("-" * 60)
    for i, item in enumerate(news[:5], 1):
        print(f"{i}. {item['title']}")
        print(f"   🕒 {item['time']} | 📂 {item['category']}")
        print()

    # выбор формата
    print("куда сохраняем?")
    print("  1 — HTML (красивая страница)")
    print("  2 — PDF")
    print("  3 — Excel (xlsx)")
    print("  4 — CSV")
    print("  enter — ничего")
    choice = input("выбери (1-4): ").strip()

    if choice == "1":
        to_html(news)
    elif choice == "2":
        to_pdf(news)
    elif choice == "3":
        to_excel(news)
    elif choice == "4":
        to_csv(news)
    else:
        print("ок, ничего не сохраняем")


if __name__ == "__main__":
    main()
