from cmath import inf
from dataclasses import dataclass, field
from typing import Optional

import os
import logging
from app.services import scraper
from app.services.openai_srv import classify_queries
from app.utils.url_generator import generate_url
import pandas as pd


@dataclass
class Session:
    # Для строк всё просто — пишем ""
    start_keywords_file_path: str = ""
    geo: str = "IT"
    period: str = "today 3-m"
    most_popular_keyword: str = ""
    second_popular_keyword: str = ""

    # Для списков используем default_factory
    urls: list[str] = field(default_factory=list)
    start_keywords: list[str] = field(default_factory=list)
    full_scraped_keywords: list[str] = field(default_factory=list)
    brand_keywords: list[str] = field(default_factory=list)
    pairs_of_values: list[list[str]] = field(default_factory=list)

    csv_data: list[dict] = field(default_factory=list)

    def collect_keywords_and_value_pairs(self):
        count = len(self.start_keywords)
        counter = 0
        for key in self.start_keywords:
            url = generate_url(first_keyword=self.most_popular_keyword, second_keyword=self.key,
                               geo=self.geo.upper(), period=self.period)

            trends_data = scraper.get_google_trends_data(url=url)
            try:
                keys = trends_data[1]
            except IndexError:
                keys = []

            self.full_scraped_keywords = list(set(keys + self.full_scraped_keywords))
            coef = 0
            coef_1 = 0
            coef_2 = 0
            try:
                self.pairs_of_values.append(trends_data[0])
            except IndexError:
                self.pairs_of_values.append(["0", "0"])
            try:
                first_value = int(self.pairs_of_values[i][0])
                if first_value != 0:
                    coef = 100 / first_value
                else:
                    coef = 9999999
                coef_1 = 100
            except IndexError:
                first_value = "0"

            try:
                second_value = int(self.pairs_of_values[i][1])
                coef_2 = second_value * coef
            except IndexError:
                second_value = "0"

            self.csv_data.append({
                "first_keyword": self.start_keywords[i],
                "brand_keyword": self.start_keywords[j],
                "first_value": first_value,
                "second_value": second_value,
                "coef_1": coef_1,
                "coef_2": coef_2,
            })
            counter += 1
            logging.info(f"Progress: {counter}/{count}")

        # for url in self.urls:
        #     keys = scraper.get_new_keywords(url=url)
        #     self.full_scraped_keywords = list(set(keys + self.full_scraped_keywords))

    def collect_brand_keywords(self):
        resp = classify_queries(self.full_scraped_keywords)
        self.brand_keywords = list(set(
            item['clean_brand'] for item in resp['result'] if item['clean_brand']
        ))
        # self.brand_keywords
        print(self.brand_keywords)

    def compare_brands(self):
        for brand in self.brand_keywords:
            url = generate_url(first_keyword=self.most_popular_keyword, second_keyword=brand, geo=self.geo.upper(),
                               period=self.period)
            print(f"Brand: {brand}, URL: {url}")
            pair = scraper.get_only_first_pair_values(url)
            print(pair)
            self.pairs_of_values.append(pair)

    def create_csv(self, doc_id: Optional[str] = "None"):
        file_path = os.path.join("./output", f"output_{doc_id}.csv")

        self.csv_data.append({
            "first_keyword": "---",
            "brand_keyword": "---",
            "first_value": "---",
            "second_value": "---",
            "coef_1": "---",
            "coef_2": "---",
        })

        coef = 0
        coef_1 = 0
        coef_2 = 0

        for i in range(len(self.brand_keywords)):
            try:
                first_value = int(self.pairs_of_values[i][0])
                if first_value != 0:
                    coef = 100 / first_value
                else:
                    coef = 9999999
                coef_1 = 100
            except IndexError:
                print(f"IndexError: {i}")
                first_value = "no value"
            try:
                second_value = int(self.pairs_of_values[i][1])
                coef_2 = second_value * coef
            except IndexError:
                print(f"IndexError: {i}")
                second_value = "no value"

            self.csv_data.append({
                "first_keyword": self.most_popular_keyword,
                "brand_keyword": self.brand_keywords[i],
                "first_value": first_value,
                "second_value": second_value,
                "coef_1": coef_1,
                "coef_2": coef_2,
            })
        df = pd.DataFrame(self.csv_data, columns=["first_keyword", "brand_keyword", "first_value", "second_value"])
        df.to_csv(file_path, index=False, encoding='utf-8-sig', sep=';')

        return file_path
