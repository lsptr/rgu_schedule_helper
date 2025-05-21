class ApiDatabase:
    def __init__(self, db_connection):
        self.conn = db_connection

    def get_classrooms(self):
        """Получает список всех аудиторий"""
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM classrooms ORDER BY name")
            return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

    def get_groups(self):
        """Получает список всех учебных групп"""
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM groups ORDER BY name")
            return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

    def get_forms(self):
        """Получает список форм обучения"""
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT form_id, name FROM forms ORDER BY name")
            return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

    def get_institutes(self):
        """Получает список институтов"""
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT institute_id, name FROM institutes ORDER BY name")
            return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

    def get_teachers(self):
        """Получает список преподавателей"""
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT id, full_name FROM teachers ORDER BY full_name")
            return [{'id': row[0], 'name': row[1]} for row in cursor.fetchall()]

    def get_schedule_from_group(self, group_name):
        """Получает расписание для указанной группы по имени"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, wt.name as week_type, dow.name as day_of_week, 
                       s.pair_number, s.time_start, s.time_end,
                       c.name as classroom, lt.name as lesson_type,
                       t.full_name as teacher, sub.name as subject
                FROM schedule s
                JOIN groups g ON s.group_id = g.id
                JOIN week_types wt ON s.week_type_id = wt.id
                JOIN days_of_week dow ON s.day_of_week_id = dow.id
                LEFT JOIN classrooms c ON s.classroom_id = c.id
                LEFT JOIN lesson_types lt ON s.lesson_type_id = lt.id
                LEFT JOIN teachers t ON s.teacher_id = t.id
                LEFT JOIN subjects sub ON s.subject_id = sub.id
                WHERE g.name = %s
                ORDER BY s.day_of_week_id, s.pair_number
            """, (group_name,))

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_schedule_from_classroom(self, classroom_name):
        """Получает расписание для указанной аудитории по имени"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, g.name as group_name, wt.name as week_type, 
                       dow.name as day_of_week, s.pair_number, 
                       s.time_start, s.time_end, lt.name as lesson_type,
                       t.full_name as teacher, sub.name as subject
                FROM schedule s
                JOIN groups g ON s.group_id = g.id
                JOIN week_types wt ON s.week_type_id = wt.id
                JOIN days_of_week dow ON s.day_of_week_id = dow.id
                LEFT JOIN classrooms c ON s.classroom_id = c.id
                LEFT JOIN lesson_types lt ON s.lesson_type_id = lt.id
                LEFT JOIN teachers t ON s.teacher_id = t.id
                LEFT JOIN subjects sub ON s.subject_id = sub.id
                WHERE c.name = %s
                ORDER BY s.day_of_week_id, s.pair_number
            """, (classroom_name,))

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_schedule_from_teacher(self, teacher_name):
        """Получает расписание для указанного преподавателя по имени"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                SELECT s.id, g.name as group_name, wt.name as week_type, 
                       dow.name as day_of_week, s.pair_number, 
                       s.time_start, s.time_end, c.name as classroom,
                       lt.name as lesson_type, sub.name as subject
                FROM schedule s
                JOIN groups g ON s.group_id = g.id
                JOIN week_types wt ON s.week_type_id = wt.id
                JOIN days_of_week dow ON s.day_of_week_id = dow.id
                LEFT JOIN classrooms c ON s.classroom_id = c.id
                LEFT JOIN lesson_types lt ON s.lesson_type_id = lt.id
                LEFT JOIN teachers t ON s.teacher_id = t.id
                LEFT JOIN subjects sub ON s.subject_id = sub.id
                WHERE t.full_name = %s
                ORDER BY s.day_of_week_id, s.pair_number
            """, (teacher_name,))

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]