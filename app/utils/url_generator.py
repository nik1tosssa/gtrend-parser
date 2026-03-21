import logging
from urllib.parse import urlencode, quote
from app.utils.file_reader import get_keywords_from_file
from app.constants import COUNTRIES

PERIODS = {
    "1 месяц": "today 1-m",
    "3 месяца": "today 3-m",
    "1 год": "today-y",
}

def generate_url(first_keyword: str, second_keyword: str, period: str, geo: str) -> str:
    base_url = "https://trends.google.com/explore"
    params = {
        "q": f"{first_keyword},{second_keyword}",
        "date": PERIODS.get(period, "today"),
        "geo": geo,
    }

    query_string = urlencode(params, quote_via=quote)
    url = f"{base_url}?{query_string}"

    return url

def generate_all_rows(file_path: str, user_data) -> list:
    keywords = get_keywords_from_file(file_path=file_path)
    logging.info(f"Keywords: {keywords}")
    rows = []

    for i in range(len(keywords)):
        for j in range(i + 1, len(keywords)):
            url = generate_url(first_keyword=keywords[i], second_keyword=keywords[j], period=user_data["period"],
                         geo=COUNTRIES.get(user_data.get("country").lower(), "RU"))
            logging.info(f"Generated: {url}")
            rows.append([keywords[i], keywords[j], url])
    return rows


print(generate_url(first_keyword="iphone", second_keyword="samsung", period="3 месяца", geo="BY"))
