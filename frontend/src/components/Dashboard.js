import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Alert } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faCalendarAlt, faUserMd, faClock, faCheckCircle, 
  faTimesCircle, faBell, faStethoscope
} from '@fortawesome/free-solid-svg-icons';
import { appointmentService, notificationService } from '../services/api';

function Dashboard({ user }) {
  const [dashboardData, setDashboardData] = useState({
    total_appointments: 0,
    upcoming_appointments: 0,
    completed_appointments: 0,
    today_appointments: 0,
    pending_appointments: 0,
    total_doctors: 0
  });
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
    fetchRecentNotifications();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const response = await appointmentService.getDashboard();
      if (response) {
        setDashboardData(response);
      }
    } catch (error) {
      setError('Failed to load dashboard data');
      console.error('Dashboard data fetch error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentNotifications = async () => {
    try {
      const response = await notificationService.getNotifications({ limit: 5 });
      setNotifications(response.results || response);
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    }
  };

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getRoleSpecificContent = () => {
    // Ensure dashboardData is defined with default values
    const safeDashboardData = dashboardData || {
      upcoming_appointments: 0,
      completed_appointments: 0,
      total_appointments: 0,
      today_appointments: 0,
      pending_appointments: 0,
      total_doctors: 0
    };

    if (user.role === 'PATIENT') {
      return (
        <>
          <Col md={3}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faCalendarAlt} size="2x" className="mb-3" />
                <h3>{safeDashboardData.upcoming_appointments || 0}</h3>
                <p>Upcoming Appointments</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faCheckCircle} size="2x" className="mb-3" />
                <h3>{safeDashboardData.completed_appointments || 0}</h3>
                <p>Completed Appointments</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faUserMd} size="2x" className="mb-3" />
                <h3>{safeDashboardData.total_appointments || 0}</h3>
                <p>Total Appointments</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faBell} size="2x" className="mb-3" />
                <h3>{notifications.filter(n => !n.is_read).length}</h3>
                <p>Unread Notifications</p>
              </Card.Body>
            </Card>
          </Col>
        </>
      );
    } else if (user.role === 'DOCTOR') {
      return (
        <>
          <Col md={4}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faCalendarAlt} size="2x" className="mb-3" />
                <h3>{safeDashboardData.today_appointments || 0}</h3>
                <p>Today's Appointments</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faClock} size="2x" className="mb-3" />
                <h3>{safeDashboardData.upcoming_appointments || 0}</h3>
                <p>Upcoming Appointments</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faUserMd} size="2x" className="mb-3" />
                <h3>{safeDashboardData.total_appointments || 0}</h3>
                <p>Total Appointments</p>
              </Card.Body>
            </Card>
          </Col>
        </>
      );
    } else {
      return (
        <>
          <Col md={3}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faCalendarAlt} size="2x" className="mb-3" />
                <h3>{safeDashboardData.total_appointments || 0}</h3>
                <p>Total Appointments</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faClock} size="2x" className="mb-3" />
                <h3>{safeDashboardData.today_appointments || 0}</h3>
                <p>Today's Appointments</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faCheckCircle} size="2x" className="mb-3" />
                <h3>{safeDashboardData.pending_appointments || 0}</h3>
                <p>Pending Appointments</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="dashboard-card">
              <Card.Body className="text-center">
                <FontAwesomeIcon icon={faUserMd} size="2x" className="mb-3" />
                <h3>{safeDashboardData.total_doctors || 0}</h3>
                <p>Total Doctors</p>
              </Card.Body>
            </Card>
          </Col>
        </>
      );
    }
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

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="mb-1">
            {getWelcomeMessage()}, {user.first_name}!
          </h1>
          <p className="text-muted mb-0">
            Welcome to your medical appointment dashboard
          </p>
        </div>
        <FontAwesomeIcon icon={faStethoscope} size="3x" className="text-primary" />
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Row className="mb-4">
        {getRoleSpecificContent()}
      </Row>

      <Row>
        <Col lg={8}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Recent Activity</h5>
            </Card.Header>
            <Card.Body>
              <p className="text-muted">Your recent appointments and activities will appear here.</p>
              <div className="text-center py-4">
                <FontAwesomeIcon icon={faCalendarAlt} size="3x" className="text-muted mb-3" />
                <p className="text-muted">No recent activity to display</p>
              </div>
            </Card.Body>
          </Card>
        </Col>
        <Col lg={4}>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Recent Notifications</h5>
            </Card.Header>
            <Card.Body>
              {notifications.length > 0 ? (
                notifications.slice(0, 3).map((notification) => (
                  <div key={notification.id} className="mb-3 pb-3 border-bottom">
                    <div className="d-flex justify-content-between align-items-start">
                      <div>
                        <h6 className="mb-1">{notification.title}</h6>
                        <p className="text-muted small mb-1">{notification.message}</p>
                        <small className="text-muted">
                          {new Date(notification.created_at).toLocaleString()}
                        </small>
                      </div>
                      {!notification.is_read && (
                        <span className="badge bg-primary">New</span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4">
                  <FontAwesomeIcon icon={faBell} size="2x" className="text-muted mb-3" />
                  <p className="text-muted">No notifications</p>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default Dashboard;
