from openai import OpenAI
import json
from config_reader import config

client = OpenAI(api_key=config.openai_api_key.get_secret_value())


def classify_queries(queries: list):
    # Убедитесь, что содержимое content — это строка (json.dumps для списка)
    user_content = json.dumps(queries)

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",  # или gpt-4-turbo-preview
            # Исправление для response_format:
            response_format={"type": "json_object"},
            # Исправление для messages:
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
        # Преобразование ответа из строки в объект Python
        res = json.loads(response.choices[0].message.content)
        print(res)
        return res

    except Exception as e:
        print(f"Error: {e}")

    return None
