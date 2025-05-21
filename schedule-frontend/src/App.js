import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Feedback from './pages/Feedback';
import Navbar from './components/Navbar';
import TeacherSchedule from './pages/TeacherSchedule';
import GroupSchedule from './pages/GroupSchedule';
import ClassroomSchedule from './pages/ClassroomSchedule';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />,
        <Route path="/feedback/" element={<Feedback />} />
        <Route path="/schedule/teacher/:teacherName" element={<TeacherSchedule />} />
        <Route path="/schedule/group/:groupName" element={<GroupSchedule />} />
        <Route path="/schedule/classroom/:classroomName" element={<ClassroomSchedule />} />
      </Routes>
    </Router>
  );
}

export default App;