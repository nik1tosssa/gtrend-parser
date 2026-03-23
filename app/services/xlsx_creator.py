import app.services.scraper as scraper
import os
import pandas as pd


def get_new_xlsx_file_path(rows: list, id: str) -> str:
    file_path = os.path.join("readies", f"data_{id}.xlsx")
    all_pairs_data = []  # Список для накопления данных всех пар

    for row in rows:
        first_keyword = row[0]
        second_keyword = row[1]
        url = row[2]

        scraped_data = scraper.get_google_trends_data(url)
        if len(scraped_data) != 0:
            if len(scraped_data[0]) > 0:
                pair_of_values = scraped_data[0]
            else:
                pair_of_values = 'err'
            if len(scraped_data[1]) > 0:
                keywords = scraped_data[1]
            else:
                keywords = 'err'
        else:
            pair_of_values = 'err'
            keywords = 'err'

        all_pairs_data.append({
            "first_keyword": first_keyword,
            "second_keyword": second_keyword,
            "pair_of_values": pair_of_values,
            "keywords": keywords,
        })

    # Сохраняем всё сразу после цикла
    df = pd.DataFrame(all_pairs_data)
    # Вместо df.to_excel(file_path)
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    # В этой точке файл уже точно должен быть на диске

    return file_path
