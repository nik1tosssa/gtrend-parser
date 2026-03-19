from urllib.parse import urlencode, quote

PERIODS = {
    "1 месяц": "today 1-m",
    "3 месяца": "today 3-m",
    "1 год": "today-y",
}


def generate_url(first_keyword: str, second_keyword: str, period: str, geo: str) -> str:
    base_url = "https://trends.google.com/explore"
    params ={
        "q": f"{first_keyword},{second_keyword}",
        "date": PERIODS.get(period, "today"),
        "geo": geo,
    }

    query_string = urlencode(params, quote_via=quote)
    url = f"{base_url}?{query_string}"

    return url

print(generate_url(first_keyword="iphone", second_keyword="samsung", period="3 месяца",geo="BY"))