import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Table, Badge, Button, Alert } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faCalendarAlt, faUserMd, faUsers, faClock,
  faPlus, faStethoscope
} from '@fortawesome/free-solid-svg-icons';
import { appointmentService } from '../services/api';
import CreateDoctor from './CreateDoctor';

function AdminDashboardMinimal({ user }) {
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
    fetchDashboardData();
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
      {/* CREATE DOCTOR BUTTON - ABSOLUTELY VISIBLE */}
      <div style={{ 
        backgroundColor: '#007bff', 
        padding: '30px', 
        margin: '20px 0', 
        borderRadius: '10px',
        textAlign: 'center',
        border: '4px solid #0056b3',
        boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
      }}>
        <h2 style={{ 
          color: 'white', 
          marginBottom: '20px', 
          fontSize: '32px',
          fontWeight: 'bold'
        }}>
          <FontAwesomeIcon icon={faPlus} style={{ marginRight: '15px' }} />
          CREATE NEW DOCTOR PROFILE
        </h2>
        <Button
          variant="success"
          size="lg"
          onClick={() => setShowCreateDoctor(true)}
          style={{ 
            fontSize: '20px', 
            padding: '15px 50px',
            fontWeight: 'bold',
            backgroundColor: '#28a745',
            borderColor: '#28a745',
            color: 'white',
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
          }}
        >
          <FontAwesomeIcon icon={faPlus} style={{ marginRight: '10px' }} />
          CLICK TO CREATE DOCTOR
        </Button>
      </div>

      {showCreateDoctor && (
        <div style={{ 
          margin: '20px 0',
          padding: '20px',
          backgroundColor: '#f8f9fa',
          border: '2px solid #dee2e6',
          borderRadius: '8px'
        }}>
          <CreateDoctor
            onDoctorCreated={handleDoctorCreated}
            onCancel={() => setShowCreateDoctor(false)}
          />
        </div>
      )}

      {/* ORIGINAL ADMIN DASHBOARD */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="mb-1">Admin Dashboard</h1>
          <p className="text-muted mb-0">System overview and management</p>
        </div>
        <FontAwesomeIcon icon={faStethoscope} size="3x" className="text-primary" />
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

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
              <FontAwesomeIcon icon={faUserMd} size="2x" className="mb-3" />
              <h3>{dashboardData.total_doctors || 0}</h3>
              <p>Total Doctors</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="dashboard-card">
            <Card.Body className="text-center">
              <FontAwesomeIcon icon={faUsers} size="2x" className="mb-3" />
              <h3>{dashboardData.pending_appointments || 0}</h3>
              <p>Pending Appointments</p>
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
              <Table striped hover>
                <thead>
                  <tr>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {recentAppointments.slice(0, 5).map((appointment, index) => (
                    <tr key={appointment.id || index}>
                      <td>{appointment.patient_name || 'N/A'}</td>
                      <td>{appointment.doctor_name || 'N/A'}</td>
                      <td>{new Date(appointment.appointment_date).toLocaleDateString()}</td>
                      <td>{appointment.time_slot_start} - {appointment.time_slot_end}</td>
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
    </div>
  );
}

export default AdminDashboardMinimal;
