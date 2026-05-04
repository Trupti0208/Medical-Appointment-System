import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Badge, Button, Alert } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faCalendarAlt, faUserMd, faClock, faCheckCircle,
  faTimesCircle, faStethoscope
} from '@fortawesome/free-solid-svg-icons';
import { appointmentService, doctorService } from '../services/api';

function DoctorDashboard({ user }) {
  const [dashboardData, setDashboardData] = useState({
    total_appointments: 0,
    today_appointments: 0,
    upcoming_appointments: 0,
    completed_appointments: 0
  });
  const [todayAppointments, setTodayAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
    fetchTodayAppointments();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const response = await appointmentService.getDashboard();
      if (response) {
        setDashboardData(response);
      }
    } catch (error) {
      setError('Failed to load dashboard data');
      console.error('Doctor Dashboard data fetch error:', error);
    }
  };

  const fetchTodayAppointments = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const response = await appointmentService.getMyAppointments({ date: today });
      setTodayAppointments(response.results || response);
    } catch (error) {
      console.error('Failed to fetch today appointments:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (appointmentId, newStatus) => {
    try {
      await appointmentService.updateAppointment(appointmentId, { status: newStatus });
      fetchTodayAppointments();
      fetchDashboardData();
    } catch (error) {
      setError('Failed to update appointment status');
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      'PENDING': 'warning',
      'SCHEDULED': 'info',
      'CONFIRMED': 'success',
      'CANCELLED': 'danger',
      'COMPLETED': 'primary',
      'NO_SHOW': 'secondary',
    };

    return (
      <Badge bg={variants[status] || 'secondary'} className="appointment-status">
        {status}
      </Badge>
    );
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
          <h1 className="mb-1">Doctor Dashboard</h1>
          <p className="text-muted mb-0">Manage your appointments and patient care</p>
        </div>
        <FontAwesomeIcon icon={faStethoscope} size="3x" className="text-primary" />
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {/* Dashboard Stats */}
      <Row className="mb-4">
        <Col md={4}>
          <Card className="dashboard-card">
            <Card.Body className="text-center">
              <FontAwesomeIcon icon={faCalendarAlt} size="2x" className="mb-3" />
              <h3>{dashboardData.today_appointments || 0}</h3>
              <p>Today's Appointments</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="dashboard-card">
            <Card.Body className="text-center">
              <FontAwesomeIcon icon={faClock} size="2x" className="mb-3" />
              <h3>{dashboardData.upcoming_appointments || 0}</h3>
              <p>Upcoming Appointments</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="dashboard-card">
            <Card.Body className="text-center">
              <FontAwesomeIcon icon={faUserMd} size="2x" className="mb-3" />
              <h3>{dashboardData.total_appointments || 0}</h3>
              <p>Total Appointments</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Today's Appointments */}
      <Card>
        <Card.Header>
          <h5 className="mb-0">Today's Appointments</h5>
        </Card.Header>
        <Card.Body>
          {todayAppointments.length > 0 ? (
            <div className="table-responsive">
              <Table hover>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Patient</th>
                    <th>Reason</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {todayAppointments.map((appointment) => (
                    <tr key={appointment.id}>
                      <td>
                        <strong>{appointment.time_slot_start} - {appointment.time_slot_end}</strong>
                      </td>
                      <td>
                        <div>
                          <strong>{appointment.patient_name || 'N/A'}</strong>
                          <br />
                          <small className="text-muted">{appointment.patient?.email || 'N/A'}</small>
                        </div>
                      </td>
                      <td>
                        <span title={appointment.reason_for_visit}>
                          {appointment.reason_for_visit.length > 30
                            ? `${appointment.reason_for_visit.substring(0, 30)}...`
                            : appointment.reason_for_visit}
                        </span>
                      </td>
                      <td>{getStatusBadge(appointment.status)}</td>
                      <td>
                        <div className="btn-group" role="group">
                          {appointment.status === 'PENDING' && (
                            <>
                              <Button
                                variant="outline-success"
                                size="sm"
                                onClick={() => handleStatusUpdate(appointment.id, 'CONFIRMED')}
                                title="Confirm Appointment"
                              >
                                <FontAwesomeIcon icon={faCheckCircle} /> Confirm
                              </Button>
                              <Button
                                variant="outline-danger"
                                size="sm"
                                onClick={() => handleStatusUpdate(appointment.id, 'CANCELLED')}
                                title="Cancel Appointment"
                              >
                                <FontAwesomeIcon icon={faTimesCircle} /> Cancel
                              </Button>
                            </>
                          )}
                          {appointment.status === 'SCHEDULED' && (
                            <Button
                              variant="outline-success"
                              size="sm"
                              onClick={() => handleStatusUpdate(appointment.id, 'CONFIRMED')}
                              title="Confirm Appointment"
                            >
                              <FontAwesomeIcon icon={faCheckCircle} /> Confirm
                            </Button>
                          )}
                          {appointment.status === 'CONFIRMED' && (
                            <>
                              <Button
                                variant="outline-success"
                                size="sm"
                                onClick={() => handleStatusUpdate(appointment.id, 'COMPLETED')}
                                title="Mark as Completed"
                              >
                                <FontAwesomeIcon icon={faCheckCircle} /> Complete
                              </Button>
                              <Button
                                variant="outline-danger"
                                size="sm"
                                onClick={() => handleStatusUpdate(appointment.id, 'NO_SHOW')}
                                title="Mark as No Show"
                              >
                                <FontAwesomeIcon icon={faTimesCircle} /> No Show
                              </Button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          ) : (
            <div className="text-center py-5">
              <FontAwesomeIcon icon={faCalendarAlt} size="3x" className="text-muted mb-3" />
              <h5>No appointments today</h5>
              <p className="text-muted">You don't have any appointments scheduled for today.</p>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}

export default DoctorDashboard;
