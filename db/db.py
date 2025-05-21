import psycopg2
from .html_db import HtmlDatabase
from .downloader_db import DownloaderDatabase
from .exel_db import ExelDatabase
from .api_db import ApiDatabase

class Database:
    def __init__(self):
        self.conn = None
        self.html_db = None
        self.downloader = None
        self.exel_db = None
        self.api_db = None
        self.connect()

    def connect(self):
        """Установка соединения с БД"""
        try:
            self.conn = psycopg2.connect(
                dbname="schedule_db",
                user="schedule_user",
                password="schedule_pass",
                host="postgres",
                port="5432",
                connect_timeout=5
            )
            self.html_db = HtmlDatabase(self.conn)
            self.downloader = DownloaderDatabase(self.conn)
            self.exel_db = ExelDatabase(self.conn)
            self.api_db = ApiDatabase(self.conn)
            print("Successfully connected to database")
        except psycopg2.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        """Закрытие соединения с БД"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")

    def save_schedule_data(self, data):
        return self.html_db.save_schedule_data(data)

    def download_new_files(self):
        return self.downloader.download_new_files()

    def insert_data(self, data):
        return self.exel_db.insert_data(data)

    def save_parse_date(self, filepath):
        return self.exel_db.save_parse_date(filepath)

    def not_schedule(self, filepath):
        return self.exel_db.not_schedule(filepath)

    def is_schedule(self, filepath):
        return self.exel_db.is_schedule(filepath)

    def check_parse_date(self, filepath):
        return self.exel_db.check_parse_date(filepath)

    def get_classrooms(self):
        return self.api_db.get_classrooms()

    def get_groups(self):
        return self.api_db.get_groups()

    def get_forms(self):
        return self.api_db.get_forms()

    def get_institutes(self):
        return self.api_db.get_institutes()

    def get_teachers(self):
        return self.api_db.get_teachers()

    def get_schedule_from_group(self, group_name):
        return self.api_db.get_schedule_from_group(group_name)

    def get_schedule_from_classroom(self, classroom_name):
        return self.api_db.get_schedule_from_classroom(classroom_name)

    def get_schedule_from_teacher(self, teacher_name):
        return self.api_db.get_schedule_from_teacher(teacher_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
