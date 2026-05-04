import React, { useState } from 'react';
import { Card, Form, Button, Alert, Row, Col } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUserMd, faPlus, faTimes } from '@fortawesome/free-solid-svg-icons';
import { doctorService, authService } from '../services/api';

function CreateDoctor({ onDoctorCreated, onCancel }) {
  const [formData, setFormData] = useState({
    // User Information
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    
    // Doctor Profile Information
    name: '',
    specialization: '',
    phone: '',
    qualifications: '',
    experience_years: '',
    license_number: '',
    clinic_name: '',
    clinic_address: '',
    consultation_fee: '',
    is_available: true,
    max_appointments_per_day: 10,
    bio: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      // Step 1: Create user account with DOCTOR role
      const userResponse = await authService.register({
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        role: 'DOCTOR'
      });

      // Step 2: Create doctor profile using the created user's ID
      const doctorData = {
        user_id: userResponse.id,
        name: formData.name,
        email: formData.email,
        phone: formData.phone || null,
        specialization: formData.specialization,
        qualifications: formData.qualifications || '',
        experience_years: parseInt(formData.experience_years) || 0,
        license_number: formData.license_number,
        clinic_name: formData.clinic_name || '',
        clinic_address: formData.clinic_address || '',
        consultation_fee: parseFloat(formData.consultation_fee) || 0,
        is_available: formData.is_available,
        max_appointments_per_day: parseInt(formData.max_appointments_per_day) || 10,
        bio: formData.bio || ''
      };

      await doctorService.createDoctor(doctorData);
      
      setSuccess('Doctor created successfully!');
      
      // Reset form
      setFormData({
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        name: '',
        specialization: '',
        phone: '',
        qualifications: '',
        experience_years: '',
        license_number: '',
        clinic_name: '',
        clinic_address: '',
        consultation_fee: '',
        is_available: true,
        max_appointments_per_day: 10,
        bio: '',
      });

      // Notify parent component
      if (onDoctorCreated) {
        onDoctorCreated();
      }

    } catch (error) {
      console.error('Error creating doctor:', error);
      setError(error.response?.data?.detail || 'Failed to create doctor. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="mb-4">
      <Card.Header className="d-flex justify-content-between align-items-center">
        <h5 className="mb-0">
          <FontAwesomeIcon icon={faUserMd} className="me-2" />
          Create New Doctor
        </h5>
        {onCancel && (
          <Button variant="outline-secondary" size="sm" onClick={onCancel}>
            <FontAwesomeIcon icon={faTimes} />
          </Button>
        )}
      </Card.Header>
      <Card.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        {success && <Alert variant="success">{success}</Alert>}

        <Form onSubmit={handleSubmit}>
          {/* User Information Section */}
          <h6 className="text-primary mb-3">User Account Information</h6>
          <Row className="mb-3">
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Email Address *</Form.Label>
                <Form.Control
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  placeholder="doctor@medical.com"
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Password *</Form.Label>
                <Form.Control
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  placeholder="Enter secure password"
                />
              </Form.Group>
            </Col>
          </Row>
          <Row className="mb-3">
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>First Name *</Form.Label>
                <Form.Control
                  type="text"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  required
                  placeholder="John"
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Last Name *</Form.Label>
                <Form.Control
                  type="text"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  required
                  placeholder="Doe"
                />
              </Form.Group>
            </Col>
          </Row>

          {/* Doctor Profile Section */}
          <h6 className="text-primary mb-3 mt-4">Doctor Profile Information</h6>
          <Row className="mb-3">
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Display Name *</Form.Label>
                <Form.Control
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  placeholder="Dr. John Doe"
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Specialization *</Form.Label>
                <Form.Control
                  type="text"
                  name="specialization"
                  value={formData.specialization}
                  onChange={handleChange}
                  required
                  placeholder="Cardiology"
                />
              </Form.Group>
            </Col>
          </Row>

          <Row className="mb-3">
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Phone Number</Form.Label>
                <Form.Control
                  type="tel"
                  name="phone"
                  value={formData.phone}
                  onChange={handleChange}
                  placeholder="+1-555-123-4567"
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>License Number *</Form.Label>
                <Form.Control
                  type="text"
                  name="license_number"
                  value={formData.license_number}
                  onChange={handleChange}
                  required
                  placeholder="DOC123456"
                />
              </Form.Group>
            </Col>
          </Row>

          <Row className="mb-3">
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Qualifications</Form.Label>
                <Form.Control
                  type="text"
                  name="qualifications"
                  value={formData.qualifications}
                  onChange={handleChange}
                  placeholder="MD, PhD"
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Experience (Years)</Form.Label>
                <Form.Control
                  type="number"
                  name="experience_years"
                  value={formData.experience_years}
                  onChange={handleChange}
                  placeholder="10"
                />
              </Form.Group>
            </Col>
          </Row>

          <Row className="mb-3">
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Clinic Name</Form.Label>
                <Form.Control
                  type="text"
                  name="clinic_name"
                  value={formData.clinic_name}
                  onChange={handleChange}
                  placeholder="City Medical Center"
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Consultation Fee ($)</Form.Label>
                <Form.Control
                  type="number"
                  step="0.01"
                  name="consultation_fee"
                  value={formData.consultation_fee}
                  onChange={handleChange}
                  placeholder="150.00"
                />
              </Form.Group>
            </Col>
          </Row>

          <Form.Group className="mb-3">
            <Form.Label>Clinic Address</Form.Label>
            <Form.Control
              as="textarea"
              name="clinic_address"
              value={formData.clinic_address}
              onChange={handleChange}
              rows={2}
              placeholder="123 Medical St, City, State 12345"
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Bio</Form.Label>
            <Form.Control
              as="textarea"
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              rows={3}
              placeholder="Brief description of doctor's background and expertise..."
            />
          </Form.Group>

          <Row className="mb-4">
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  name="is_available"
                  checked={formData.is_available}
                  onChange={handleChange}
                  label="Available for appointments"
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Max Appointments per Day</Form.Label>
                <Form.Control
                  type="number"
                  name="max_appointments_per_day"
                  value={formData.max_appointments_per_day}
                  onChange={handleChange}
                  placeholder="10"
                />
              </Form.Group>
            </Col>
          </Row>

          <div className="d-flex gap-2">
            <Button
              type="submit"
              variant="primary"
              disabled={loading}
              className="px-4"
            >
              <FontAwesomeIcon icon={faPlus} className="me-2" />
              {loading ? 'Creating...' : 'Create Doctor'}
            </Button>
            {onCancel && (
              <Button
                variant="outline-secondary"
                onClick={onCancel}
                disabled={loading}
              >
                Cancel
              </Button>
            )}
          </div>
        </Form>
      </Card.Body>
    </Card>
  );
}

export default CreateDoctor;
