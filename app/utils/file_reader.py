import os
import logging
import pandas as pd

def get_keywords_from_file(file_path: str) -> list:
    extension = os.path.splitext(file_path)[1].lower()

    try:
        if extension == ".xlsx":
            df = pd.read_excel(file_path)
        elif extension == ".csv":
            df = pd.read_csv(file_path)
        else:
            return []
        keywords = df.iloc[:, 0].dropna().astype(str).tolist()
        keywords = [word.strip() for word in keywords if word.strip()]
        return keywords

    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return []
