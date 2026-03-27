from openai import OpenAI
import json
from config_reader import config

client = OpenAI(api_key=config.openai_api_key.get_secret_value())


def classify_queries(queries: list):
    full_result = []  # Сюда будем собирать все ответы от GPT
    batch_size = 30  # Размер одной порции данных

    # Разрезаем список queries на части по 30 элементов
    for i in range(0, len(queries), batch_size):
        batch = queries[i: i + batch_size]
        user_content = json.dumps(batch)

        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                response_format={"type": "json_object"},
                messages=[
                    {
                        "role": "system",
                        "content":
                            """
                                Classify a list of search queries.

                                Input is a JSON array of strings.
                                Process every query independently.
                                Return exactly one result per input query in the same order.
                                The number of output items must exactly match the number of input queries.
                                Do not skip items.
                                Do not merge items.
                                Do not guess.

                                Return only JSON in this exact format:
                                {"result":[{"status":"exact_brand|brand_with_extra|not_brand|uncertain","clean_brand":"string or null"}]}
                            """
                    },
                    {
                        "role": "user",
                        "content": user_content
                    }
                ]
            )

            # Парсим ответ для текущего батча
            batch_res = json.loads(response.choices[0].message.content)

            # Добавляем элементы из ключа "result" в наш общий список
            if "result" in batch_res:
                full_result.extend(batch_res["result"])

            print(f"Processed batch {i // batch_size + 1}")

        except Exception as e:
            print(f"Error in batch starting at index {i}: {e}")
            # В случае ошибки можно либо вернуть [], либо пропустить батч
            return {"result": []}

    # Возвращаем объект в том же формате, который ожидался изначально
    return {"result": full_result}