import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Container, Row, Col, Nav, Navbar, NavDropdown, Badge } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faUser, faCalendarAlt, faUserMd, faStethoscope, 
  faBell, faSignOutAlt, faHome, faBars, faTimes
} from '@fortawesome/free-solid-svg-icons';

// Components
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import DoctorList from './components/DoctorList';
import AppointmentList from './components/AppointmentList';
import BookAppointment from './components/BookAppointment';
import DoctorDashboard from './components/DoctorDashboard';
import AdminDashboard from './components/AdminDashboardMinimal';
import CreateDoctorPage from './components/CreateDoctorPage';
import Notifications from './components/Notifications';
import Profile from './components/Profile';

// Services
import { authService, notificationService } from './services/api';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    // Check if user is logged in on app load
    const token = localStorage.getItem('accessToken');
    if (token) {
      const userData = JSON.parse(localStorage.getItem('user') || '{}');
      setUser(userData);
      fetchNotifications();
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    if (user) {
      fetchNotifications();
      // Set up periodic notification refresh
      const interval = setInterval(fetchNotifications, 30000); // Every 30 seconds
      return () => clearInterval(interval);
    }
  }, [user]);

  const fetchNotifications = async () => {
    try {
      const response = await notificationService.getNotificationCount();
      setUnreadCount(response.unread || 0);
    } catch (error) {
      console.error('Error fetching notifications:', error);
      setUnreadCount(0);
    }
  };

  const handleLogin = (userData, tokens) => {
    setUser(userData);
    localStorage.setItem('accessToken', tokens.access);
    localStorage.setItem('refreshToken', tokens.refresh);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const handleLogout = () => {
    setUser(null);
    setNotifications([]);
    setUnreadCount(0);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  };

  const getSidebarItems = () => {
    if (!user) return [];

    const items = [
      { path: '/dashboard', label: 'Dashboard', icon: faHome },
    ];

    if (user.role === 'PATIENT') {
      items.push(
        { path: '/doctors', label: 'Find Doctors', icon: faUserMd },
        { path: '/appointments', label: 'My Appointments', icon: faCalendarAlt },
        { path: '/book-appointment', label: 'Book Appointment', icon: faStethoscope },
      );
    } else if (user.role === 'DOCTOR') {
      items.push(
        { path: '/doctor-dashboard', label: 'My Dashboard', icon: faUserMd },
        { path: '/appointments', label: 'Appointments', icon: faCalendarAlt },
      );
    } else if (user.role === 'ADMIN') {
      items.push(
        { path: '/admin-dashboard', label: 'Admin Dashboard', icon: faUserMd },
        { path: '/doctors', label: 'Doctors', icon: faUserMd },
        { path: '/appointments', label: 'Appointments', icon: faCalendarAlt },
      );
    }

    return items;
  };

  if (loading) {
    return (
      <div className="loading-spinner">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <Routes>
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    );
  }

  return (
    <div className="App">
      {/* Navigation */}
      <Navbar bg="dark" variant="dark" expand="lg" className="mb-0">
        <Container fluid>
          <Navbar.Brand href="/dashboard">
            <FontAwesomeIcon icon={faStethoscope} className="me-2" />
            Medical Appointment System
          </Navbar.Brand>
          
          <button
            className="btn btn-link text-white d-lg-none"
            onClick={() => setSidebarOpen(!sidebarOpen)}
          >
            <FontAwesomeIcon icon={sidebarOpen ? faTimes : faBars} />
          </button>

          <Nav className="ms-auto">
            <NavDropdown title={
              <span>
                <FontAwesomeIcon icon={faBell} className="me-1" />
                Notifications
                {unreadCount > 0 && (
                  <Badge bg="danger" className="ms-1">{unreadCount}</Badge>
                )}
              </span>
            } id="notification-dropdown">
              <NavDropdown.Item href="/notifications">
                View All Notifications
              </NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item onClick={fetchNotifications}>
                Refresh
              </NavDropdown.Item>
            </NavDropdown>

            <NavDropdown title={
              <span>
                <FontAwesomeIcon icon={faUser} className="me-1" />
                {user.first_name} {user.last_name}
              </span>
            } id="user-dropdown">
              <NavDropdown.Item href="/profile">
                <FontAwesomeIcon icon={faUser} className="me-2" />
                Profile
              </NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item onClick={handleLogout}>
                <FontAwesomeIcon icon={faSignOutAlt} className="me-2" />
                Logout
              </NavDropdown.Item>
            </NavDropdown>
          </Nav>
        </Container>
      </Navbar>

      <Container fluid className="p-0">
        <Row>
          {/* Sidebar */}
          <Col lg={2} className={`sidebar ${sidebarOpen ? 'd-block' : 'd-none d-lg-block'}`}>
            <Nav className="flex-column pt-3">
              {getSidebarItems().map((item, index) => (
                <Nav.Link
                  key={index}
                  href={item.path}
                  className={window.location.pathname === item.path ? 'active' : ''}
                >
                  <FontAwesomeIcon icon={item.icon} className="me-2" />
                  {item.label}
                </Nav.Link>
              ))}
            </Nav>
          </Col>

          {/* Main Content */}
          <Col lg={10} className="main-content">
            <Routes>
              <Route path="/dashboard" element={<Dashboard user={user} />} />
              <Route path="/doctors" element={<DoctorList />} />
              <Route path="/appointments" element={<AppointmentList user={user} />} />
              <Route path="/book-appointment" element={<BookAppointment user={user} />} />
              <Route path="/doctor-dashboard" element={<DoctorDashboard user={user} />} />
              <Route path="/admin-dashboard" element={<AdminDashboard user={user} />} />
              <Route path="/create-doctor" element={<CreateDoctorPage />} />
              <Route path="/notifications" element={<Notifications />} />
              <Route path="/profile" element={<Profile user={user} />} />
              <Route path="*" element={<Navigate to="/dashboard" />} />
            </Routes>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
