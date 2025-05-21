from datetime import datetime
import psycopg2
from psycopg2 import errors, sql


class ExelDatabase:
    def __init__(self, db_connection):
        self.conn = db_connection

    def _get_or_create_id(self, table_name, field_name, value, additional_fields=None):
        """Вспомогательный метод для получения или создания записи в справочной таблице"""
        with self.conn.cursor() as cursor:
            # Пытаемся найти существующую запись
            query = sql.SQL("SELECT id FROM {} WHERE {} = %s").format(
                sql.Identifier(table_name),
                sql.Identifier(field_name)
            )
            cursor.execute(query, (value,))
            result = cursor.fetchone()

            if result:
                return result[0]

            # Если запись не найдена, создаем новую
            columns = [field_name]
            values = [value]

            if additional_fields:
                columns.extend(additional_fields.keys())
                values.extend(additional_fields.values())

            insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id").format(
                sql.Identifier(table_name),
                sql.SQL(', ').join(map(sql.Identifier, columns)),
                sql.SQL(', ').join([sql.Placeholder()] * len(values)))

            cursor.execute(insert_query, values)
            self.conn.commit()
            return cursor.fetchone()[0]

    def insert_data(self, data):
        try:
            # Получаем или создаем группу
            group_id = self._get_or_create_id('groups', 'name', data['group_name'])

            for lesson in data['lessons']:
                day_of_week_id = self._get_or_create_id('days_of_week', 'name', lesson['day_of_week'])

                # Разбираем время на start и end
                time_parts = lesson['time'].split('-')
                time_start = time_parts[0].strip()
                time_end = time_parts[1].strip() if len(time_parts) > 1 else None

                # Обрабатываем данные для нечетной недели
                if lesson['odd_week']['lesson_name']:
                    self._insert_lesson(
                        group_id=group_id,
                        week_type='НЧ',
                        day_of_week_id=day_of_week_id,
                        pair_number=lesson['pair_number'],
                        time_start=time_start,
                        time_end=time_end,
                        classroom=lesson['odd_week']['classroom'],
                        lesson_type=lesson['odd_week']['lesson_type'],
                        teacher=lesson['odd_week']['teacher'],
                        subject=lesson['odd_week']['lesson_name']
                    )

                # Обрабатываем данные для четной недели
                if lesson['even_week']['lesson_name']:
                    self._insert_lesson(
                        group_id=group_id,
                        week_type='Ч',
                        day_of_week_id=day_of_week_id,
                        pair_number=lesson['pair_number'],
                        time_start=time_start,
                        time_end=time_end,
                        classroom=lesson['even_week']['classroom'],
                        lesson_type=lesson['even_week']['lesson_type'],
                        teacher=lesson['even_week']['teacher'],
                        subject=lesson['even_week']['lesson_name']
                    )

            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при сохранении данных: {e}")
            return False

    def _insert_lesson(self, group_id, week_type, day_of_week_id, pair_number,
                       time_start, time_end, classroom, lesson_type, teacher, subject):
        """Вспомогательный метод для вставки одного занятия"""
        with self.conn.cursor() as cursor:
            # Получаем ID для всех справочных данных
            week_type_id = self._get_or_create_id('week_types', 'name', week_type)

            classroom_id = None
            if classroom:
                classroom_id = self._get_or_create_id('classrooms', 'name', classroom)

            lesson_type_id = None
            if lesson_type:
                lesson_type_id = self._get_or_create_id('lesson_types', 'name', lesson_type)

            teacher_id = None
            if teacher:
                teacher_id = self._get_or_create_id('teachers', 'full_name', teacher)

            subject_id = None
            if subject:
                subject_id = self._get_or_create_id('subjects', 'name', subject)

            # Вставляем запись в расписание
            insert_query = """
            INSERT INTO schedule (
                group_id, week_type_id, day_of_week_id, pair_number,
                time_start, time_end, classroom_id, lesson_type_id,
                teacher_id, subject_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (group_id, week_type_id, day_of_week_id, pair_number, time_start) 
            DO NOTHING
            """

            cursor.execute(insert_query, (
                group_id, week_type_id, day_of_week_id, pair_number,
                time_start, time_end, classroom_id, lesson_type_id,
                teacher_id, subject_id
            ))

    def save_parse_date(self, filepath):
        """Сохраняет дату парсинга файла в таблицу files"""
        try:
            with self.conn.cursor() as cursor:
                # Проверяем, существует ли уже запись для этого файла
                cursor.execute("""
                    SELECT file_id FROM files 
                    WHERE local_path = %s
                """, (filepath,))
                existing_file = cursor.fetchone()

                if existing_file:
                    # Обновляем существующую запись
                    cursor.execute("""
                        UPDATE files 
                        SET parse_date = %s,
                        is_schedule = TRUE
                        WHERE file_id = %s
                    """, (datetime.now(), existing_file[0],))
                else:
                    print("1_Файл " + filepath + " не найден")

                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при сохранении даты парсинга: {e}")

    def not_schedule(self, filepath):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                        SELECT file_id FROM files 
                        WHERE local_path = %s
                    """, (filepath,))
                existing_file = cursor.fetchone()

                if existing_file:
                    # Обновляем существующую запись
                    cursor.execute("""
                            UPDATE files 
                            SET is_schedule = FALSE 
                            WHERE file_id = %s
                        """, (existing_file[0],))
                else:
                    print("Файл " + filepath + " не найден")

                self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка при установке is_schedule=False: {e}")

    def is_schedule(self, filepath):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT parse_date, download_date, is_schedule 
                    FROM files 
                    WHERE local_path = %s
                """, (filepath,))
                result = cursor.fetchone()

                if result:
                    parse_date, download_date, is_schedule_value = result

                    if parse_date is not None:
                        # Если есть parse_date, сравниваем с download_date
                        if download_date and download_date > parse_date:
                            return True
                        else:
                            return False
                    else:
                        # Если parse_date нет, возвращаем значение is_schedule
                        return is_schedule_value if is_schedule_value is not None else True
                else:
                    print(f"2_Файл {filepath} не найден в базе данных")
                    return False

        except Exception as e:
            print(f"Ошибка при проверке is_schedule: {e}")
            return False


    def check_parse_date(self, filepath):
        try:
            with self.conn.cursor() as cursor:
                # Получаем parse_date для указанного файла
                cursor.execute("""
                        SELECT parse_date FROM files 
                        WHERE local_path = %s
                    """, (filepath,))
                result = cursor.fetchone()

                if result:
                    parse_date = result[0]
                    return parse_date is not None
                else:
                    print(f"3_Файл {filepath} не найден в базе данных")
                    return False

        except Exception as e:
            print(f"Ошибка при проверке parse_date: {e}")
            return False

