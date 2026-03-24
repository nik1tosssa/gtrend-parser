import app.services.scraper as scraper
import os
import pandas as pd
from app.services.openai_srv import classify_queries


def get_new_xlsx_file_path(rows: list, id: str) -> str:
    file_path = os.path.join("output", f"data_{id}.csv")
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
                gpt_result = classify_queries(keywords)
                print(gpt_result)
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
    df.to_csv(file_path, index=False, encoding='utf-8-sig', sep=';')
    # Вместо df.to_excel(file_path)
    # with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
    #     df.to_excel(writer, index=False)
    # В этой точке файл уже точно должен быть на диске

    return file_path
