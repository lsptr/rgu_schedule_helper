import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import WeekIndicator from '../components/WeekIndicator';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import { getClassroomSchedule } from '../api';

const columns = [
  { id: 'time', label: 'Время', width: '15%' },
  { id: 'group', label: 'Группа', width: '15%' },
  { id: 'subject', label: 'Предмет', width: '30%' },
  { id: 'type', label: 'Тип занятия', width: '15%' },
  { id: 'teacher', label: 'Преподаватель', width: '15%' },
];

const mergePairs = (schedule) => {
  const groups = {};

  // Группируем по всем параметрам кроме времени
  schedule.forEach(item => {
    const key = `${item.week_type}_${item.day_of_week}_${item.pair_number}_${item.group_name}_${item.teacher}_${item.lesson_type}_${item.subject}`;

    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
  });

  // Склеиваем пары в каждой группе
  const result = [];
  Object.values(groups).forEach(group => {
    group.sort((a, b) => a.time_start.localeCompare(b.time_start));

    let current = { ...group[0] };

    for (let i = 1; i < group.length; i++) {
      const item = group[i];

      if (current.time_end === item.time_start) {
        current.time_end = item.time_end;
      } else {
        result.push(current);
        current = { ...item };
      }
    }

    result.push(current);
  });

  return result;
};

const groupByDayAndWeek = (schedule) => {
  const result = {};

  schedule.forEach(item => {
    const key = `${item.week_type}_${item.day_of_week}`;
    if (!result[key]) {
      result[key] = [];
    }
    result[key].push(item);
  });

  return result;
};

function ClassroomSchedule() {
  const { classroomName } = useParams();
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        const data = await getClassroomSchedule(classroomName);
        const mergedData = mergePairs(data);
        setSchedule(mergedData);
      } catch (err) {
        setError('Не удалось загрузить расписание аудитории');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchSchedule();
  }, [classroomName]);

  if (loading) return <Typography>Загрузка расписания...</Typography>;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!schedule.length) return <Typography>Расписание для аудитории не найдено</Typography>;

  const groupedSchedule = groupByDayAndWeek(schedule);

  return (
    <Box sx={{ p: 3 }}>
      <WeekIndicator />
      <Typography variant="h4" gutterBottom>
        Расписание аудитории: {decodeURIComponent(classroomName)}
      </Typography>

      {Object.entries(groupedSchedule).map(([key, daySchedule]) => {
        const [weekType, dayOfWeek] = key.split('_');
        return (
          <Box key={key} sx={{ mb: 4 }}>
            <Typography variant="h5" sx={{ mb: 2 }}>
              {getDayName(dayOfWeek)} ({dayOfWeek}), {weekType === 'Ч' ? 'Чётная неделя' : 'Нечётная неделя'}
            </Typography>

            <TableContainer component={Paper} sx={{ overflowX: 'auto' }}>
              <Table sx={{
                tableLayout: 'fixed',
                minWidth: 800 // Минимальная ширина таблицы
              }}>
                <TableHead>
                  <TableRow>
                    {columns.map((column) => (
                      <TableCell
                        key={column.id}
                        sx={{
                          width: column.width,
                          fontWeight: 'bold',
                          backgroundColor: '#f5f5f5',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {column.label}
                      </TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {daySchedule.map((item, index) => (
                    <TableRow key={`${key}_${index}`} hover>
                      <TableCell sx={{
                        width: columns[0].width,
                        whiteSpace: 'nowrap'
                      }}>
                        {formatTime(item.time_start)} - {formatTime(item.time_end)}
                      </TableCell>
                      <TableCell sx={{
                        width: columns[1].width,
                        whiteSpace: 'nowrap'
                      }}>
                        {item.group_name}
                      </TableCell>
                      <TableCell sx={{ width: columns[2].width }}>
                        {item.subject}
                      </TableCell>
                      <TableCell sx={{
                        width: columns[3].width,
                        whiteSpace: 'nowrap'
                      }}>
                        <Chip
                          label={getLessonType(item.lesson_type)}
                          color={getLessonTypeColor(item.lesson_type)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{
                        width: columns[4].width,
                        whiteSpace: 'nowrap'
                      }}>
                        {item.teacher}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        );
      })}
    </Box>
  );
}

// Вспомогательные функции
const getDayName = (day) => {
  const days = {
    'ПН': 'Понедельник',
    'ВТ': 'Вторник',
    'СР': 'Среда',
    'ЧТ': 'Четверг',
    'ПТ': 'Пятница',
    'СБ': 'Суббота'
  };
  return days[day] || day;
};

const formatTime = (time) => {
  return time.slice(0, 5);
};

const getLessonType = (type) => {
  const types = {
    'Пр': 'Практика',
    'Лк': 'Лекция',
    'Лб': 'Лабораторная'
  };
  return types[type] || type;
};

const getLessonTypeColor = (type) => {
  const colors = {
    'Пр': 'primary',
    'Лк': 'secondary',
    'Лб': 'success'
  };
  return colors[type] || 'default';
};

export default ClassroomSchedule;