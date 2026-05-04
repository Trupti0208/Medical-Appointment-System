import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Badge, Button, Alert } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faCalendarAlt, faUserMd, faUsers, faClock,
  faCheckCircle, faTimesCircle, faStethoscope, faPlus
} from '@fortawesome/free-solid-svg-icons';
import { appointmentService, doctorService } from '../services/api';
import CreateDoctor from './CreateDoctor';
import QuickCreateDoctor from './QuickCreateDoctor';

function AdminDashboard({ user }) {
  const [dashboardData, setDashboardData] = useState({
    total_appointments: 0,
    upcoming_appointments: 0,
    completed_appointments: 0,
    today_appointments: 0,
    pending_appointments: 0,
    total_doctors: 0
  });
  const [recentAppointments, setRecentAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateDoctor, setShowCreateDoctor] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchRecentAppointments();
  }, [user]);

  const fetchDashboardData = async () => {
    try {
      const response = await appointmentService.getDashboard();
      setDashboardData(response);
    } catch (error) {
      setError('Failed to load dashboard data');
    }
  };

  const fetchRecentAppointments = async () => {
    try {
      const response = await appointmentService.getAppointments({ limit: 10 });
      setRecentAppointments(response.results || response);
    } catch (error) {
      console.error('Failed to fetch recent appointments:', error);
    } finally {
      setLoading(false);
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

  const handleDoctorCreated = () => {
    setShowCreateDoctor(false);
    fetchDashboardData(); // Refresh dashboard data to show new doctor count
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
          <h1 className="mb-1">Admin Dashboard</h1>
          <p className="text-muted mb-0">System overview and management</p>
        </div>
        <div className="d-flex align-items-center gap-3">
          <Button
            variant="primary"
            onClick={() => setShowCreateDoctor(true)}
            className="d-flex align-items-center"
          >
            <FontAwesomeIcon icon={faPlus} className="me-2" />
            Create Doctor
          </Button>
          <FontAwesomeIcon icon={faStethoscope} size="3x" className="text-primary" />
        </div>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {/* ULTRA VISIBLE CREATE DOCTOR BUTTON */}
      <div style={{ 
        backgroundColor: '#007bff', 
        padding: '20px', 
        margin: '20px 0', 
        borderRadius: '8px',
        textAlign: 'center',
        border: '3px solid #0056b3'
      }}>
        <h3 style={{ color: 'white', marginBottom: '15px', fontSize: '24px' }}>
          <FontAwesomeIcon icon={faPlus} style={{ marginRight: '10px' }} />
          CREATE NEW DOCTOR PROFILE
        </h3>
        <Button
          variant="light"
          size="lg"
          onClick={() => setShowCreateDoctor(true)}
          style={{ 
            fontSize: '18px', 
            padding: '15px 40px',
            fontWeight: 'bold',
            backgroundColor: '#28a745',
            borderColor: '#28a745',
            color: 'white'
          }}
        >
          <FontAwesomeIcon icon={faPlus} style={{ marginRight: '10px' }} />
          CLICK HERE TO CREATE DOCTOR
        </Button>
      </div>

      {showCreateDoctor && (
        <div style={{ margin: '20px 0' }}>
          <CreateDoctor
            onDoctorCreated={handleDoctorCreated}
            onCancel={() => setShowCreateDoctor(false)}
          />
        </div>
      )}

      {/* Quick Create Doctor - Backup Method */}
      <QuickCreateDoctor />

      {/* Dashboard Stats */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="dashboard-card">
            <Card.Body className="text-center">
              <FontAwesomeIcon icon={faCalendarAlt} size="2x" className="mb-3" />
              <h3>{dashboardData.total_appointments || 0}</h3>
              <p>Total Appointments</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="dashboard-card">
            <Card.Body className="text-center">
              <FontAwesomeIcon icon={faClock} size="2x" className="mb-3" />
              <h3>{dashboardData.today_appointments || 0}</h3>
              <p>Today's Appointments</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="dashboard-card">
            <Card.Body className="text-center">
              <FontAwesomeIcon icon={faUsers} size="2x" className="mb-3" />
              <h3>{dashboardData.total_patients || 0}</h3>
              <p>Total Patients</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="dashboard-card">
            <Card.Body className="text-center">
              <FontAwesomeIcon icon={faUserMd} size="2x" className="mb-3" />
              <h3>{dashboardData.total_doctors || 0}</h3>
              <p>Total Doctors</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Recent Appointments */}
      <Card>
        <Card.Header>
          <h5 className="mb-0">Recent Appointments</h5>
        </Card.Header>
        <Card.Body>
          {recentAppointments.length > 0 ? (
            <div className="table-responsive">
              <Table hover>
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Reason</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recentAppointments.map((appointment) => (
                    <tr key={appointment.id}>
                      <td>
                        <div>
                          <strong>{new Date(appointment.appointment_date).toLocaleDateString()}</strong>
                          <br />
                          <small className="text-muted">
                            {appointment.time_slot_info?.time_range || 'N/A'}
                          </small>
                        </div>
                      </td>
                      <td>
                        <div>
                          <strong>{appointment.patient_name || 'N/A'}</strong>
                          <br />
                          <small className="text-muted">{appointment.patient?.email || 'N/A'}</small>
                        </div>
                      </td>
                      <td>
                        <div>
                          <strong>Dr. {appointment.doctor_info?.name || 'N/A'}</strong>
                          <br />
                          <small className="text-muted">
                            {appointment.doctor_info?.specialization || 'N/A'}
                          </small>
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
                        <Button variant="outline-primary" size="sm">
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          ) : (
            <div className="text-center py-5">
              <FontAwesomeIcon icon={faCalendarAlt} size="3x" className="text-muted mb-3" />
              <h5>No recent appointments</h5>
              <p className="text-muted">No appointments have been scheduled yet.</p>
            </div>
          )}
        </Card.Body>
      </Card>

      {/* Create Doctor Modal/Form */}
      {showCreateDoctor && (
        <CreateDoctor
          onDoctorCreated={handleDoctorCreated}
          onCancel={() => setShowCreateDoctor(false)}
        />
      )}
    </div>
  );
}

export default AdminDashboard;
