import React, { useState, useEffect } from 'react';
import WeekIndicator from '../components/WeekIndicator';
import {
  Box,
  Typography,
  Container,
  Autocomplete,
  TextField,
  Button,
  Stack
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { getGroups, getClassrooms, getTeachers } from '../api';

function Home() {
  const navigate = useNavigate();
  const [groups, setGroups] = useState([]);
  const [classrooms, setClassrooms] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [selectedClassroom, setSelectedClassroom] = useState(null);
  const [selectedTeacher, setSelectedTeacher] = useState(null);
  const [loading, setLoading] = useState({
    groups: true,
    classrooms: true,
    teachers: true
  });

  useEffect(() => {
    // Загрузка данных для дропдаунов
    const fetchData = async () => {
      try {
        const [groupsData, classroomsData, teachersData] = await Promise.all([
          getGroups(),
          getClassrooms(),
          getTeachers()
        ]);

        setGroups(groupsData);
        setClassrooms(classroomsData);
        setTeachers(teachersData);

        setLoading({
          groups: false,
          classrooms: false,
          teachers: false
        });
      } catch (error) {
        console.error('Ошибка загрузки данных:', error);
      }
    };

    fetchData();
  }, []);

  const handleGenerateSchedule = () => {
    if (selectedGroup) {
      navigate(`/schedule/group/${selectedGroup.name}`);
    } else if (selectedTeacher) {
      navigate(`/schedule/teacher/${selectedTeacher.name}`);
    } else if (selectedClassroom) {
      navigate(`/schedule/classroom/${selectedClassroom.name}`);
    }
  };

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          mt: 8,
          mb: 4,
          textAlign: 'center'
        }}
      >
        <Typography
          variant="h3"
          component="h1"
          gutterBottom
          sx={{
            fontWeight: 'bold',
            mb: 2,
            color: 'primary.main'
          }}
        >
          Система отслеживания изменений в расписании РГУ Косыгина
        </Typography>

        <Typography
          variant="h5"  
          sx={{ 
            mb: 4,
            mt: 8,
            color: '#353535'
          }}
        >
          Найдите расписание по группе, преподавателю или аудитории
        </Typography>
      </Box>

      <Box sx={{
        width: { xs: '100%', sm: '90%', md: '80%', lg: '80%' }, // Адаптивная ширина
        maxWidth: 1200,                                          
        margin: '0 auto',
        p: 4,
        borderRadius: 2,
        boxShadow: 3,
        backgroundColor: 'background.paper',
        border: '1px solid',               
        borderColor: 'divider'
      }}>
        <Stack spacing={5}>
          <Autocomplete
            options={groups}
            getOptionLabel={(option) => option.name}
            loading={loading.groups}
            value={selectedGroup}
            onChange={(_, newValue) => {
              setSelectedGroup(newValue);
              setSelectedTeacher(null);
              setSelectedClassroom(null);
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Выберите группу"
                variant="outlined"
                placeholder="Начните вводить название группы"
              />
            )}
          />

          <Autocomplete
            options={teachers}
            getOptionLabel={(option) => option.name}
            loading={loading.teachers}
            value={selectedTeacher}
            onChange={(_, newValue) => {
              setSelectedTeacher(newValue);
              setSelectedGroup(null);
              setSelectedClassroom(null);
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Выберите преподавателя"
                variant="outlined"
                placeholder="Начните вводить ФИО преподавателя"
              />
            )}
          />

          <Autocomplete
            options={classrooms}
            getOptionLabel={(option) => option.name}
            loading={loading.classrooms}
            value={selectedClassroom}
            onChange={(_, newValue) => {
              setSelectedClassroom(newValue);
              setSelectedGroup(null);
              setSelectedTeacher(null);
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Выберите аудиторию"
                variant="outlined"
                placeholder="Начните вводить номер аудитории"
              />
            )}
          />

          <Button
            variant="contained"
            size="large"
            onClick={handleGenerateSchedule}
            disabled={!selectedGroup && !selectedTeacher && !selectedClassroom}
            sx={{ py: 2, mt: 2 }}
          >
            Сформировать расписание
          </Button>
        </Stack>
      </Box>
    </Container>
  );
}

export default Home;