from datetime import datetime
import psycopg2
from psycopg2 import errors

class HtmlDatabase:
    def __init__(self, db_connection):
        self.conn = db_connection

    def save_schedule_data(self, data):
        """Сохранение данных расписания в БД"""
        if not data:
            print("No data to save")
            return False

        try:
            with self.conn.cursor() as cursor:
                # Сохраняем институты и получаем их ID
                institute_ids = self._save_institutes(cursor, data)
                if not institute_ids:
                    print("No institutes found or saved")
                    return False

                # Сохраняем формы обучения и получаем их ID
                form_ids = self._save_forms(cursor, data)
                if not form_ids:
                    print("No forms found or saved")
                    return False

                # Сохраняем расписания
                schedule_result = self._save_schedules(cursor, data, institute_ids, form_ids)
                if not schedule_result:
                    print("No schedules found or saved")
                    return False

            self.conn.commit()
            print("All data saved successfully")
            return True
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            self.conn.rollback()
            return False
        except Exception as e:
            print(f"Error saving data: {e}")
            self.conn.rollback()
            return False

    def _save_institutes(self, cursor, institutes_data):
        """Сохранение институтов в БД"""
        institute_ids = {}

        if not institutes_data:
            return institute_ids

        for institute in institutes_data:
            if not institute or not isinstance(institute, dict) or 'name' not in institute:
                print("Invalid institute data format")
                continue

            try:
                # Проверяем, существует ли институт
                cursor.execute(
                    "SELECT institute_id FROM institutes WHERE name = %s",
                    (institute['name'],)
                )
                existing = cursor.fetchone()

                if existing:
                    institute_ids[institute['name']] = existing[0]
                    print(f"Institute already exists: {institute['name']}")
                else:
                    # Добавляем новый институт
                    cursor.execute(
                        "INSERT INTO institutes (name) VALUES (%s) RETURNING institute_id",
                        (institute['name'],)
                    )
                    new_id = cursor.fetchone()[0]
                    institute_ids[institute['name']] = new_id
                    print(f"Added new institute: {institute['name']}")

            except errors.UniqueViolation:
                self.conn.rollback()
                cursor.execute(
                    "SELECT institute_id FROM institutes WHERE name = %s",
                    (institute['name'],)
                )
                existing = cursor.fetchone()
                if existing:
                    institute_ids[institute['name']] = existing[0]
            except Exception as e:
                print(f"Error saving institute {institute.get('name', 'unknown')}: {e}")
                continue

        return institute_ids

    def _save_forms(self, cursor, institutes_data):
        """Сохранение форм обучения в БД"""
        form_ids = {}
        unique_forms = set()

        if not institutes_data:
            return form_ids

        # Собираем все уникальные формы обучения
        for institute in institutes_data:
            if 'forms' not in institute or not isinstance(institute['forms'], list):
                continue

            for form in institute['forms']:
                if form and isinstance(form, dict) and 'name' in form:
                    unique_forms.add(form['name'])

        # Сохраняем формы
        for form_name in unique_forms:
            try:
                cursor.execute(
                    "SELECT form_id FROM forms WHERE name = %s",
                    (form_name,)
                )
                existing = cursor.fetchone()

                if existing:
                    form_ids[form_name] = existing[0]
                    print(f"Form already exists: {form_name}")
                else:
                    cursor.execute(
                        "INSERT INTO forms (name) VALUES (%s) RETURNING form_id",
                        (form_name,)
                    )
                    new_id = cursor.fetchone()[0]
                    form_ids[form_name] = new_id
                    print(f"Added new form: {form_name}")

            except errors.UniqueViolation:
                self.conn.rollback()
                cursor.execute(
                    "SELECT form_id FROM forms WHERE name = %s",
                    (form_name,)
                )
                existing = cursor.fetchone()
                if existing:
                    form_ids[form_name] = existing[0]
            except Exception as e:
                print(f"Error saving form {form_name}: {e}")
                continue

        return form_ids

    def _save_schedules(self, cursor, institutes_data, institute_ids, form_ids):
        """Сохранение расписаний в БД"""
        if not institutes_data or not institute_ids or not form_ids:
            return False

        saved_count = 0
        for institute in institutes_data:
            if not institute or 'name' not in institute or 'forms' not in institute:
                continue

            institute_name = institute['name']
            if institute_name not in institute_ids:
                continue

            institute_id = institute_ids[institute_name]

            for form in institute['forms']:
                if not form or 'name' not in form or 'files' not in form:
                    continue

                form_name = form['name']
                if form_name not in form_ids:
                    continue

                form_id = form_ids[form_name]

                for file in form['files']:
                    if not file or 'title' not in file or 'link' not in file:
                        continue

                    try:
                        # Проверяем существование расписания
                        cursor.execute(
                            """SELECT schedule_id, link, change_date FROM schedules 
                               WHERE form_id = %s AND institute_id = %s AND title = %s""",
                            (form_id, institute_id, file['title'])
                        )
                        existing = cursor.fetchone()

                        if existing:
                            # Проверяем, нужно ли обновить
                            existing_id, existing_link, existing_date = existing
                            if (existing_link != file['link'] or
                                    (file.get('date') and existing_date != file['date'])):
                                # Обновляем существующее расписание
                                cursor.execute(
                                    """UPDATE schedules SET 
                                       link = %s, 
                                       change_date = %s,
                                       last_updated = %s
                                       WHERE schedule_id = %s""",
                                    (file['link'], file.get('date'), datetime.now(), existing_id)
                                )
                                print(f"Updated schedule: {file['title']}")

                                saved_count += 1
                            else:
                                print(f"Schedule already up-to-date: {file['title']}")
                        else:
                            # Добавляем новое расписание
                            cursor.execute(
                                """INSERT INTO schedules 
                                   (form_id, institute_id, title, link, change_date)
                                   VALUES (%s, %s, %s, %s, %s)""",
                                (form_id, institute_id, file['title'],
                                 file['link'], file.get('date'))
                            )
                            print(f"Added new schedule: {file['title']}")
                            saved_count += 1

                    except errors.UniqueViolation:
                        self.conn.rollback()
                        print(f"Duplicate schedule found: {file['title']}")
                    except Exception as e:
                        print(f"Error saving schedule {file.get('title', 'unknown')}: {e}")
                        continue

        return saved_count > 0