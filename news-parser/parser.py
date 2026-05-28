# скрипт который собирает новости с ленты.ру
# потом сохраняет в excel или csv
# юзаю requests и bs4

import os
import sys
import csv
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd

# логи чтоб видеть процесс
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# юзер-агент чтоб нас не заблокировали
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def parse_news(max_pages=3):
    """
    парсит новости с ленты
    max_pages - сколько страниц листать (1-5 норм)
    возвращает список словарей с новостями
    """
    all_news = []
    base = "https://lenta.ru"

    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{base}/parts/news/"
        else:
            url = f"{base}/parts/news/{page}/"

        logger.info(f"качаю страницу {page}: {url}")

        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            logger.error(f"не удалось загрузить {url}: {e}")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # ищем все ссылки с новостями
        # селекторы пришлось подбирать, лента неудобная
        items = soup.select("a._topnews, div.item, a.card-mini")
        if not items:
            # если не нашел - пробуем другие варианты
            items = soup.find_all("a", class_=True)

        for item in items:
            # вытаскиваем заголовок
            title = ""
            link = ""

            if item.name == "a":
                title = item.get_text(strip=True)
                link = item.get("href", "")
            else:
                # внутри div ищем ссылку
                a_tag = item.find("a")
                if a_tag:
                    title = a_tag.get_text(strip=True)
                    link = a_tag.get("href", "")
                else:
                    title = item.get_text(strip=True)

            # пропускаем пустые или слишком короткие
            if not title or len(title) < 5:
                continue

            # делаем полную ссылку если относительная
            if link and not link.startswith("http"):
                if link.startswith("/"):
                    link = base + link
                else:
                    link = base + "/" + link

            # пробуем найти время
            time_text = ""
            time_tag = item.find("time")
            if time_tag:
                time_text = time_tag.get_text(strip=True)
            if not time_text:
                time_tag = item.find("span", class_=lambda c: c and "time" in c.lower()) if hasattr(item, 'find') else None
                if time_tag:
                    time_text = time_tag.get_text(strip=True)
            if not time_text:
                time_text = datetime.now().strftime("%H:%M")

            # категория
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

        logger.info(f"после страницы {page} всего новостей: {len(all_news)}")

    # убираем дубликаты
    seen = set()
    unique = []
    for n in all_news:
        if n["title"] not in seen:
            seen.add(n["title"])
            unique.append(n)

    logger.info(f"уникальных новостей: {len(unique)}")
    return unique


def to_excel(news, filename=None):
    """сохраняем в эксель"""
    if not filename:
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"news_lenta_{now}.xlsx"

    df = pd.DataFrame(news)
    df.columns = ["Заголовок", "Ссылка", "Время", "Категория"]
    df.to_excel(filename, index=False, engine="openpyxl")
    print(f"сохранено в {filename}")
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

    print(f"сохранено в {filename}")
    return filename


def main():
    print("парсер новостей lenta.ru v1.0")
    print("=" * 35)

    try:
        pages = input("сколько страниц парсить? (1-5, нажми enter = 3): ")
        if pages.strip() == "":
            pages = 3
        else:
            pages = int(pages)
            if pages < 1:
                pages = 1
            if pages > 5:
                pages = 5
    except:
        pages = 3
        print("ну ок, будет 3 страницы")

    print(f"парсю {pages} стр...")
    news = parse_news(max_pages=pages)

    if not news:
        print("ничего не нашел. может лента лежит или структуру поменяли")
        return

    # показываем первые 5
    print(f"\nнашел {len(news)} новостей. первые 5:")
    print("-" * 55)
    for i, item in enumerate(news[:5], 1):
        print(f"{i}. {item['title']}")
        print(f"   время: {item['time']} | категория: {item['category']}")
        print()

    # сохраняем
    choice = input("в каком формате сохранить? (xlsx/csv/enter = пропустить): ").strip().lower()
    if choice == "xlsx":
        to_excel(news)
    elif choice == "csv":
        to_csv(news)
    else:
        print("ок, ничего не сохраняем")


if __name__ == "__main__":
    main()
