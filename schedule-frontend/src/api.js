import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const getClassrooms = async () => {
  const response = await axios.get(`${API_BASE_URL}/classrooms`);
  return response.data;
};

export const getGroups = async () => {
  const response = await axios.get(`${API_BASE_URL}/groups`);
  return response.data;
};

export const getTeachers = async () => {
  const response = await axios.get(`${API_BASE_URL}/teachers`);
  return response.data;
};

export const getGroupSchedule = async (groupName) => {
  const response = await axios.get(`${API_BASE_URL}/schedule/group/${encodeURIComponent(groupName)}`);
  return response.data;
};

export const getTeacherSchedule = async (teacherName) => {
  const response = await axios.get(`${API_BASE_URL}/schedule/teacher/${encodeURIComponent(teacherName)}`);
  return response.data;
};

export const getClassroomSchedule = async (classroomName) => {
  const response = await axios.get(`${API_BASE_URL}/schedule/classroom/${encodeURIComponent(classroomName)}`);
  return response.data;
};