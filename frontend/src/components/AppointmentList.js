import React, { useState, useEffect } from 'react';
import { Card, Table, Badge, Button, Alert, Modal } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faCalendarAlt, faTimes, faCheck, faClock, 
  faEye, faEdit, faTrash, faStethoscope
} from '@fortawesome/free-solid-svg-icons';
import { appointmentService } from '../services/api';

function AppointmentList({ user }) {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedAppointment, setSelectedAppointment] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);

  useEffect(() => {
    fetchAppointments();
  }, [user]);

  const fetchAppointments = async () => {
    try {
      const response = await appointmentService.getMyAppointments();
      setAppointments(response.results || response);
    } catch (error) {
      setError('Failed to load appointments');
    } finally {
      setLoading(false);
    }
  };

  const handleCancelAppointment = async () => {
    if (!selectedAppointment) return;

    try {
      await appointmentService.cancelAppointment(selectedAppointment.id);
      setShowCancelModal(false);
      setSelectedAppointment(null);
      fetchAppointments(); // Refresh the list
    } catch (error) {
      setError('Failed to cancel appointment');
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
      'RESCHEDULED': 'info',
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
          <h1 className="mb-1">My Appointments</h1>
          <p className="text-muted mb-0">View and manage your medical appointments</p>
        </div>
        {user.role === 'PATIENT' && (
          <Button variant="primary" href="/book-appointment">
            <FontAwesomeIcon icon={faCalendarAlt} className="me-2" />
            Book New Appointment
          </Button>
        )}
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card>
        <Card.Header>
          <h5 className="mb-0">Appointment History</h5>
        </Card.Header>
        <Card.Body>
          {appointments.length > 0 ? (
            <div className="table-responsive">
              <Table hover>
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Doctor</th>
                    <th>Reason</th>
                    <th>Status</th>
                    <th>Fee</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {appointments.map((appointment) => (
                    <tr key={appointment.id}>
                      <td>
                        <div>
                          <strong>{new Date(appointment.appointment_date).toLocaleDateString()}</strong>
                          <br />
                          <small className="text-muted">
                            {appointment.time_slot_start} - {appointment.time_slot_end}
                          </small>
                        </div>
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          <FontAwesomeIcon icon={faStethoscope} className="text-primary me-2" />
                          <div>
                            <strong>{appointment.doctor_name || 'N/A'}</strong>
                            <br />
                            <small className="text-muted">
                              {appointment.doctor_specialization || 'N/A'}
                            </small>
                          </div>
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
                      <td>${appointment.consultation_fee}</td>
                      <td>
                        <div className="btn-group" role="group">
                          <Button
                            variant="outline-primary"
                            size="sm"
                            title="View Details"
                          >
                            <FontAwesomeIcon icon={faEye} />
                          </Button>
                          {appointment.status === 'SCHEDULED' && appointment.can_cancel && (
                            <Button
                              variant="outline-danger"
                              size="sm"
                              title="Cancel Appointment"
                              onClick={() => {
                                setSelectedAppointment(appointment);
                                setShowCancelModal(true);
                              }}
                            >
                              <FontAwesomeIcon icon={faTimes} />
                            </Button>
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
              <h5>No appointments found</h5>
              <p className="text-muted">
                You haven't booked any appointments yet.
                {user.role === 'PATIENT' && (
                  <>
                    <br />
                    <Button variant="primary" href="/book-appointment" className="mt-2">
                      <FontAwesomeIcon icon={faCalendarAlt} className="me-2" />
                      Book Your First Appointment
                    </Button>
                  </>
                )}
              </p>
            </div>
          )}
        </Card.Body>
      </Card>

      {/* Cancel Appointment Modal */}
      <Modal show={showCancelModal} onHide={() => setShowCancelModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Cancel Appointment</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedAppointment && (
            <div>
              <p>Are you sure you want to cancel the following appointment?</p>
              <div className="bg-light p-3 rounded">
                <p className="mb-1">
                  <strong>Date:</strong> {new Date(selectedAppointment.appointment_date).toLocaleDateString()}
                </p>
                <p className="mb-1">
                  <strong>Time:</strong> {selectedAppointment.time_slot_info?.time_range || 'N/A'}
                </p>
                <p className="mb-1">
                  <strong>Doctor:</strong> Dr. {selectedAppointment.doctor_info?.name || 'N/A'}
                </p>
                <p className="mb-0">
                  <strong>Reason:</strong> {selectedAppointment.reason_for_visit}
                </p>
              </div>
              {selectedAppointment.can_cancel && (
                <Alert variant="info" className="mt-3">
                  <FontAwesomeIcon icon={faClock} className="me-2" />
                  You can cancel this appointment up to 24 hours before the scheduled time.
                </Alert>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowCancelModal(false)}>
            Close
          </Button>
          <Button variant="danger" onClick={handleCancelAppointment}>
            <FontAwesomeIcon icon={faTimes} className="me-2" />
            Cancel Appointment
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default AppointmentList;
