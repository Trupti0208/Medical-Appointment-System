import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, Form, Button, Alert, Row, Col, Badge } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faCalendarAlt, faUserMd, faClock, faCheck,
  faArrowLeft, faStethoscope
} from '@fortawesome/free-solid-svg-icons';
import { doctorService, appointmentService } from '../services/api';

function BookAppointment({ user }) {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [doctors, setDoctors] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [selectedDate, setSelectedDate] = useState('');
  
  const [formData, setFormData] = useState({
    doctor: '',
    appointment_date: '',
    time_slot: '',
    reason_for_visit: '',
    symptoms: '',
    medical_history: '',
    is_first_visit: false,
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [step, setStep] = useState(1); // 1: Select Doctor, 2: Select Date/Time, 3: Confirm

  useEffect(() => {
    const doctorId = searchParams.get('doctor');
    fetchDoctors();
    if (doctorId) {
      setFormData(prev => ({ ...prev, doctor: doctorId }));
    }
  }, [searchParams]);

  const fetchDoctors = async () => {
    try {
      const response = await doctorService.getDoctors({ is_available: true });
      setDoctors(response.results || response);
    } catch (error) {
      setError('Failed to load doctors');
      console.error('Failed to load doctors:', error);
    }
  };

  const handleDoctorSelect = async (doctorId) => {
    const doctor = doctors.find(d => d.id === parseInt(doctorId));
    setSelectedDoctor(doctor);
    setFormData(prev => ({ ...prev, doctor: doctorId }));
    setStep(2);
  };

  const handleDateSelect = async (date) => {
    if (!selectedDoctor) return;
    
    setSelectedDate(date);
    setFormData(prev => ({ ...prev, appointment_date: date }));
    
    try {
      const response = await doctorService.getDoctorSlots(selectedDoctor.id, date);
      setAvailableSlots(response.available_slots || []);
    } catch (error) {
      setError('Failed to load available slots');
    }
  };

  const handleSlotSelect = (slot) => {
    setSelectedSlot(slot);
    setFormData(prev => ({ ...prev, time_slot: slot.id }));
    setStep(3);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await appointmentService.createAppointment(formData);
      navigate('/appointments');
    } catch (error) {
      setError(error.response?.data?.message || 'Failed to book appointment');
    } finally {
      setLoading(false);
    }
  };

  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 30); // Allow booking up to 30 days in advance
    return maxDate.toISOString().split('T')[0];
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="mb-1">Book Appointment</h1>
          <p className="text-muted mb-0">Schedule your medical appointment</p>
        </div>
        <Button variant="outline-secondary" href="/appointments">
          <FontAwesomeIcon icon={faArrowLeft} className="me-2" />
          Back to Appointments
        </Button>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card>
        <Card.Body>
          {/* Progress Steps */}
          <div className="d-flex justify-content-between mb-4">
            <div className={`text-center ${step >= 1 ? 'text-primary' : 'text-muted'}`}>
              <FontAwesomeIcon icon={faUserMd} className="mb-2" size="2x" />
              <div>1. Select Doctor</div>
            </div>
            <div className={`text-center ${step >= 2 ? 'text-primary' : 'text-muted'}`}>
              <FontAwesomeIcon icon={faCalendarAlt} className="mb-2" size="2x" />
              <div>2. Select Date & Time</div>
            </div>
            <div className={`text-center ${step >= 3 ? 'text-primary' : 'text-muted'}`}>
              <FontAwesomeIcon icon={faCheck} className="mb-2" size="2x" />
              <div>3. Confirm Details</div>
            </div>
          </div>

          {/* Step 1: Select Doctor */}
          {step === 1 && (
            <div>
              <h4 className="mb-3">Select a Doctor</h4>
              <Row>
                {doctors.map((doctor) => (
                  <Col md={6} lg={4} key={doctor.id} className="mb-3">
                    <Card 
                      className={`doctor-card h-100 ${selectedDoctor?.id === doctor.id ? 'border-primary' : ''}`}
                      onClick={() => handleDoctorSelect(doctor.id)}
                      style={{ cursor: 'pointer' }}
                    >
                      <Card.Body>
                        <div className="text-center mb-3">
                          <FontAwesomeIcon icon={faStethoscope} size="2x" className="text-primary mb-2" />
                          <h6 className="mb-1">Dr. {doctor.name}</h6>
                          <Badge bg="primary" className="mb-2">
                            {doctor.specialization}
                          </Badge>
                        </div>
                        <div className="small">
                          <div className="mb-1">
                            <strong>Experience:</strong> {doctor.experience_years} years
                          </div>
                          <div className="mb-1">
                            <strong>Fee:</strong> ${doctor.consultation_fee}
                          </div>
                          {doctor.clinic_name && (
                            <div className="mb-1">
                              <strong>Clinic:</strong> {doctor.clinic_name}
                            </div>
                          )}
                        </div>
                        <div className="text-center mt-2">
                          {doctor.is_available ? (
                            <Badge bg="success">Available</Badge>
                          ) : (
                            <Badge bg="secondary">Not Available</Badge>
                          )}
                        </div>
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>
            </div>
          )}

          {/* Step 2: Select Date & Time */}
          {step === 2 && selectedDoctor && (
            <div>
              <h4 className="mb-3">Select Date & Time</h4>
              
              <div className="mb-4">
                <h5>Dr. {selectedDoctor.name} - {selectedDoctor.specialization}</h5>
                <p className="text-muted">Consultation Fee: ${selectedDoctor.consultation_fee}</p>
              </div>

              <Form.Group className="mb-4">
                <Form.Label>Select Date</Form.Label>
                <Form.Control
                  type="date"
                  value={selectedDate}
                  onChange={(e) => handleDateSelect(e.target.value)}
                  min={getMinDate()}
                  max={getMaxDate()}
                  required
                />
              </Form.Group>

              {selectedDate && (
                <div>
                  <h5 className="mb-3">Available Time Slots</h5>
                  {availableSlots.length > 0 ? (
                    <div className="d-flex flex-wrap">
                      {availableSlots.map((slot) => (
                        <div
                          key={slot.id}
                          className="time-slot"
                          onClick={() => handleSlotSelect(slot)}
                        >
                          <FontAwesomeIcon icon={faClock} className="me-2" />
                          {slot.time_range}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <Alert variant="info">
                      No available slots for the selected date. Please choose another date.
                    </Alert>
                  )}
                </div>
              )}

              <div className="mt-4">
                <Button variant="outline-secondary" onClick={() => setStep(1)} className="me-2">
                  <FontAwesomeIcon icon={faArrowLeft} className="me-2" />
                  Back
                </Button>
              </div>
            </div>
          )}

          {/* Step 3: Confirm Details */}
          {step === 3 && selectedDoctor && selectedSlot && (
            <div>
              <h4 className="mb-3">Confirm Appointment Details</h4>
              
              <div className="form-section mb-4">
                <h5>Appointment Information</h5>
                <Row>
                  <Col md={6}>
                    <p><strong>Doctor:</strong> Dr. {selectedDoctor.name}</p>
                    <p><strong>Specialization:</strong> {selectedDoctor.specialization}</p>
                    <p><strong>Date:</strong> {new Date(selectedDate).toLocaleDateString()}</p>
                    <p><strong>Time:</strong> {selectedSlot.time_range}</p>
                  </Col>
                  <Col md={6}>
                    <p><strong>Consultation Fee:</strong> ${selectedDoctor.consultation_fee}</p>
                    <p><strong>Clinic:</strong> {selectedDoctor.clinic_name || 'N/A'}</p>
                  </Col>
                </Row>
              </div>

              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Reason for Visit *</Form.Label>
                  <Form.Control
                    as="textarea"
                    name="reason_for_visit"
                    value={formData.reason_for_visit}
                    onChange={(e) => setFormData(prev => ({ ...prev, reason_for_visit: e.target.value }))}
                    placeholder="Please describe the reason for your visit"
                    rows={3}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Symptoms (Optional)</Form.Label>
                  <Form.Control
                    as="textarea"
                    name="symptoms"
                    value={formData.symptoms}
                    onChange={(e) => setFormData(prev => ({ ...prev, symptoms: e.target.value }))}
                    placeholder="Describe your symptoms or concerns"
                    rows={3}
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Medical History (Optional)</Form.Label>
                  <Form.Control
                    as="textarea"
                    name="medical_history"
                    value={formData.medical_history}
                    onChange={(e) => setFormData(prev => ({ ...prev, medical_history: e.target.value }))}
                    placeholder="Any relevant medical history"
                    rows={2}
                  />
                </Form.Group>

                <Form.Group className="mb-4">
                  <Form.Check
                    type="checkbox"
                    name="is_first_visit"
                    checked={formData.is_first_visit}
                    onChange={(e) => setFormData(prev => ({ ...prev, is_first_visit: e.target.checked }))}
                    label="This is my first visit to this doctor"
                  />
                </Form.Group>

                <div className="d-flex">
                  <Button variant="outline-secondary" onClick={() => setStep(2)} className="me-2">
                    <FontAwesomeIcon icon={faArrowLeft} className="me-2" />
                    Back
                  </Button>
                  <Button
                    variant="primary"
                    type="submit"
                    disabled={loading || !formData.reason_for_visit}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" />
                        Booking...
                      </>
                    ) : (
                      <>
                        <FontAwesomeIcon icon={faCheck} className="me-2" />
                        Confirm Booking
                      </>
                    )}
                  </Button>
                </div>
              </Form>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}

export default BookAppointment;
