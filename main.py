import time

import requests
from db import db
from rguParser import html_parser
from rguParser import exel_parser

def run_parser():
    try:

        # Адрес сайта
        url = 'https://rguk.ru/students/schedule/'
        base_url = "https://rguk.ru"

        # Парсинг сайта
        result = html_parser.parse_html(url, base_url)
        if result['success']:
            if parser_db.save_schedule_data(result['data']):
                print("Data successfully saved to database")
            else:
                print("No data to save")
        else:
            print(f"Error: {result['error']}")

        parser_db.download_new_files()

        excel = exel_parser.ExcelParser(parser_db)
        excel.parse_all_excel_files()


    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к сайту: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    parser_db = db.Database()
    while True:
        run_parser()
        time.sleep(6 * 60 * 60)  # 6 часов