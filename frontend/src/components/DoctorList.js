import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Form, Button, Badge, Alert } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faUserMd, faSearch, faMapMarkerAlt, faStar, 
  faPhone, faEnvelope, faCalendarAlt
} from '@fortawesome/free-solid-svg-icons';
import { doctorService } from '../services/api';

function DoctorList() {
  const [doctors, setDoctors] = useState([]);
  const [specializations, setSpecializations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSpecialization, setSelectedSpecialization] = useState('');

  useEffect(() => {
    fetchDoctors();
    fetchSpecializations();
  }, []);

  const fetchDoctors = async () => {
    try {
      const response = await doctorService.getDoctors();
      setDoctors(response.results || response);
    } catch (error) {
      setError('Failed to load doctors');
      console.error('Failed to load doctors:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSpecializations = async () => {
    try {
      const response = await doctorService.getSpecializations();
      setSpecializations(response.specializations || []);
    } catch (error) {
      console.error('Failed to load specializations:', error);
    }
  };

  const filteredDoctors = doctors.filter(doctor => {
    const matchesSearch = doctor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doctor.specialization.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSpecialization = !selectedSpecialization || 
                                 doctor.specialization === selectedSpecialization;
    return matchesSearch && matchesSpecialization;
  });

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
          <h1 className="mb-1">Find a Doctor</h1>
          <p className="text-muted mb-0">Browse and book appointments with qualified doctors</p>
        </div>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {/* Search and Filter */}
      <Card className="mb-4">
        <Card.Body>
          <Row>
            <Col md={6}>
              <Form.Group className="mb-3 mb-md-0">
                <Form.Label>
                  <FontAwesomeIcon icon={faSearch} className="me-2" />
                  Search Doctors
                </Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Search by name or specialization..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-0">
                <Form.Label>Filter by Specialization</Form.Label>
                <Form.Select
                  value={selectedSpecialization}
                  onChange={(e) => setSelectedSpecialization(e.target.value)}
                >
                  <option value="">All Specializations</option>
                  {specializations.map((spec, index) => (
                    <option key={index} value={spec}>{spec}</option>
                  ))}
                </Form.Select>
              </Form.Group>
            </Col>
          </Row>
        </Card.Body>
      </Card>

      {/* Doctor Cards */}
      {filteredDoctors.length > 0 ? (
        <Row>
          {filteredDoctors.map((doctor) => (
            <Col md={6} lg={4} key={doctor.id} className="mb-4">
              <Card className="doctor-card h-100">
                <Card.Body>
                  <div className="text-center mb-3">
                    {doctor.profile_picture ? (
                      <img
                        src={doctor.profile_picture}
                        alt={doctor.name}
                        className="rounded-circle mb-3"
                        style={{ width: '80px', height: '80px', objectFit: 'cover' }}
                      />
                    ) : (
                      <FontAwesomeIcon icon={faUserMd} size="3x" className="text-primary mb-3" />
                    )}
                    <h5 className="mb-1">Dr. {doctor.name}</h5>
                    <Badge bg="primary" className="mb-2">
                      {doctor.specialization}
                    </Badge>
                  </div>

                  <div className="doctor-info">
                    <div className="mb-2">
                      <FontAwesomeIcon icon={faStar} className="text-warning me-1" />
                      <span className="small">
                        {doctor.average_rating ? `${doctor.average_rating.toFixed(1)} (${doctor.total_reviews} reviews)` : 'No reviews yet'}
                      </span>
                    </div>

                    {doctor.clinic_name && (
                      <div className="mb-2">
                        <FontAwesomeIcon icon={faMapMarkerAlt} className="text-muted me-2" />
                        <span className="small">{doctor.clinic_name}</span>
                      </div>
                    )}

                    {doctor.phone && (
                      <div className="mb-2">
                        <FontAwesomeIcon icon={faPhone} className="text-muted me-2" />
                        <span className="small">{doctor.phone}</span>
                      </div>
                    )}

                    <div className="mb-2">
                      <FontAwesomeIcon icon={faEnvelope} className="text-muted me-2" />
                      <span className="small">{doctor.email}</span>
                    </div>

                    <div className="mb-3">
                      <FontAwesomeIcon icon={faUserMd} className="text-muted me-2" />
                      <span className="small">{doctor.experience_years} years experience</span>
                    </div>

                    {doctor.consultation_fee > 0 && (
                      <div className="mb-3">
                        <strong>Consultation Fee: ${doctor.consultation_fee}</strong>
                      </div>
                    )}

                    {doctor.is_available ? (
                      <Badge bg="success">Available</Badge>
                    ) : (
                      <Badge bg="secondary">Not Available</Badge>
                    )}
                  </div>

                  <div className="mt-3">
                    <Button
                      variant="primary"
                      className="w-100"
                      href={`/book-appointment?doctor=${doctor.id}`}
                      disabled={!doctor.is_available}
                    >
                      <FontAwesomeIcon icon={faCalendarAlt} className="me-2" />
                      Book Appointment
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      ) : (
        <Card>
          <Card.Body className="text-center py-5">
            <FontAwesomeIcon icon={faUserMd} size="3x" className="text-muted mb-3" />
            <h5>No doctors found</h5>
            <p className="text-muted">
              {searchTerm || selectedSpecialization
                ? 'Try adjusting your search criteria'
                : 'No doctors are currently available'}
            </p>
          </Card.Body>
        </Card>
      )}
    </div>
  );
}

export default DoctorList;
