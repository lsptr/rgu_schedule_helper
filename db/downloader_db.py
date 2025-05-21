import os
import requests
from datetime import datetime
from urllib.parse import urlparse
import psycopg2
from psycopg2 import sql


class DownloaderDatabase:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.storage_path = "C:\\Users\\cepsk\\PycharmProjects\\RguScheduleHelper\\downloaded_files"

    def ensure_storage_directory(self):
        """Создает директорию для хранения файлов если ее нет"""
        os.makedirs(self.storage_path, exist_ok=True)

    def get_files_to_download(self):
        """Получает список файлов для скачивания из schedules, которых нет в files"""
        files_to_download = []
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT s.schedule_id, s.link, s.change_date, s.title 
                    FROM schedules s
                    LEFT JOIN files f ON s.link = f.link AND 
                                       (s.change_date = f.change_date OR 
                                       (s.change_date IS NULL AND f.change_date IS NULL))
                    WHERE f.file_id IS NULL
                """)
                files_to_download = cursor.fetchall()
        except Exception as e:
            print(f"Error getting files to download: {e}")
        return files_to_download

    def download_new_files(self):
        """Скачивает все новые файлы из schedules, которых нет в files"""
        self.ensure_storage_directory()
        files = self.get_files_to_download()

        if not files:
            print("No new files to download")
            return False

        success_count = 0
        for file in files:
            schedule_id, link, change_date, title = file
            if self.download_single_file(schedule_id, link, change_date, title):
                success_count += 1

        print(f"Downloaded {success_count} of {len(files)} new files")
        return success_count > 0

    def download_single_file(self, schedule_id, link, change_date, title):
        """Скачивает один файл и сохраняет информацию в БД"""
        try:
            # Скачиваем файл
            response = requests.get(link, stream=True)
            response.raise_for_status()

            # Создаем имя файла в формате schedule_id_form_id_institute_id.расширение
            parsed_url = urlparse(link)
            # Получаем расширение файла из URL
            file_extension = os.path.splitext(parsed_url.path)[1].lower() or '.pdf'

            # Получаем form_id и institute_id для этого schedule_id
            with self.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT form_id, institute_id FROM schedules WHERE schedule_id = %s",
                    (schedule_id,)
                )
                form_id, institute_id = cursor.fetchone()

            # Формируем имя файла
            filename = f"schedule_{schedule_id}_form_{form_id}_institute_{institute_id}{file_extension}"
            local_path = os.path.join(self.storage_path, filename)

            # Сохраняем файл
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            # Добавляем запись в БД
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO files 
                       (schedule_id, link, local_path, change_date, download_date)
                       VALUES (%s, %s, %s, %s, %s)
                       ON CONFLICT (local_path) 
                       DO UPDATE SET
                           schedule_id = EXCLUDED.schedule_id,
                           link = EXCLUDED.link,
                           change_date = EXCLUDED.change_date,
                           download_date = EXCLUDED.download_date""",
                    (schedule_id, link, local_path, change_date, datetime.now())
                )
                self.conn.commit()

            print(f"Successfully downloaded and saved: {local_path}")
            return True

        except Exception as e:
            print(f"Error downloading file {link}: {e}")
            self.conn.rollback()
            return False