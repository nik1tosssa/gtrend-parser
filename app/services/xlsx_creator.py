import app.services.scraper as scraper
import os
import pandas as pd


def get_new_xlsx_file_path(rows: list, id: str) -> str:
    file_name = f"data_{id}.xlsx"
    all_pairs_data = []  # Список для накопления данных всех пар

    for row in rows:
        first_keyword = row[0]
        second_keyword = row[1]
        url = row[2]

        # Передаем и URL, и список ключей для корректной работы скрапера
        current_keywords = [first_keyword, second_keyword]
        scraped_data = scraper.get_google_trends_data(url)

        # Извлекаем данные из словаря results, который возвращает scraper.py
        # Формируем строку значений, например "45, 100"
        pair_of_values = scraped_data[0]

        # ВАЖНО: scraper.py пока не возвращает список связанных ключевых слов в results.
        # Если вы добавите их в результаты скрапера, доставайте их здесь.
        # Пока поставим заглушку или пустой список.
        keywords = scraped_data[1]

        all_pairs_data.append({
            "fist_keyword": first_keyword,
            "second_keyword": second_keyword,
            "pair_of_values": pair_of_values,
            "keywords": keywords,
        })

    # Сохраняем всё сразу после цикла
    df = pd.DataFrame(all_pairs_data)
    df.to_excel(file_name, index=False)

    return file_name



