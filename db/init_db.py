import psycopg2


def initialize_database():
    """Инициализация структуры базы данных"""
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="schedule_user",
            password="schedule_pass",
            host="postgres",
            port="5432"
        )
        conn.autocommit = True

        with conn.cursor() as cursor:
            # Создаем БД если она не существует
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'schedule_db'")
            if not cursor.fetchone():
                cursor.execute("CREATE DATABASE schedule_db")
                print("Database created")

        # Подключаемся к нашей БД
        cursor.close()
        conn.close()
        conn = psycopg2.connect(
            dbname="schedule_db",
            user="schedule_user",
            password="schedule_pass",
            host="postgres",
            port="5432"
        )

        with conn.cursor() as cursor:
            # Создаем таблицу институтов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS institutes (
                    institute_id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Создаем таблицу форм обучения
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS forms (
                    form_id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Создаем таблицу расписаний
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    schedule_id SERIAL PRIMARY KEY,
                    form_id INTEGER REFERENCES forms(form_id),
                    institute_id INTEGER REFERENCES institutes(institute_id),
                    title VARCHAR(255) NOT NULL,
                    link TEXT NOT NULL,
                    change_date VARCHAR(100),
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(form_id, institute_id, title)
                );
            """)

            # Создаем индекс для ускорения поиска
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_schedules_form_institute
                ON schedules(form_id, institute_id);
            """)

        conn.commit()
        print("Database tables created successfully")

    except psycopg2.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    initialize_database()