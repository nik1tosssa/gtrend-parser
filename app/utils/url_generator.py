from urllib.parse import urlencode, quote
from app.utils.file_reader import get_keywords_from_file
from typing import Any

# Словарь периодов для классического отображения (используются другие ключи)
OLD_PERIODS = {
    "1 месяц": "today 1-m",
    "3 месяца": "today 3-m",
    "1 год": "today 12-m",  # В старой версии часто требовалось явное указание месяцев
}


def generate_url(first_keyword: str, second_keyword: str, period: str, geo: str) -> str:

    params = {
        "date": OLD_PERIODS.get(period, "today 3-m"),
        "geo": geo.upper(),
        "q": f"{first_keyword},{second_keyword}",
        #"cmpt": "q",  # Параметр "Compare Type" — часто использовался в старых версиях
        "hl": "ru"  # Явная установка языка интерфейса
    }
    base_url = "https://trends.google.com/trends/explore"
    #https://trends.google.com/trends/explore?date=today%203-m&geo=IT&q=sisal,betflag&hl=ru
    query_string = urlencode(params, quote_via=quote)
    url = f"{base_url}?{query_string}"
    print(f"Generated URL: {url}")
    return url

def generate_all_urls(session) -> list:
    urls = []
    keywords = session.start_keywords
    for i in range(len(keywords)):
        for j in range(i + 1, len(keywords)):
            urls.append(generate_url(first_keyword=keywords[i], second_keyword=keywords[j], period=session.period,
                                      geo=session.geo.upper()))
    return urls

# Пример работы:
#print(generate_url(first_keyword="iphone", second_keyword="samsung", period="3 месяца", geo="by"))
