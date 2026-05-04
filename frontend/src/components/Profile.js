import React, { useState, useEffect } from 'react';
import { Card, Form, Button, Alert, Row, Col } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faUser, faEnvelope, faPhone, faCalendar,
  faMapMarkerAlt, faEdit, faSave
} from '@fortawesome/free-solid-svg-icons';
import { authService } from '../services/api';

function Profile({ user }) {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    date_of_birth: '',
    address: '',
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [editMode, setEditMode] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        date_of_birth: user.date_of_birth || '',
        address: user.address || '',
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      await authService.updateProfile(formData);
      setSuccess('Profile updated successfully!');
      setEditMode(false);
    } catch (error) {
      setError('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setEditMode(false);
    // Reset form data
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        date_of_birth: user.date_of_birth || '',
        address: user.address || '',
      });
    }
  };

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="mb-1">My Profile</h1>
          <p className="text-muted mb-0">Manage your personal information</p>
        </div>
        {!editMode && (
          <Button variant="primary" onClick={() => setEditMode(true)}>
            <FontAwesomeIcon icon={faEdit} className="me-2" />
            Edit Profile
          </Button>
        )}
      </div>

      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}

      <Card>
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    <FontAwesomeIcon icon={faUser} className="me-2" />
                    First Name
                  </Form.Label>
                  <Form.Control
                    type="text"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    disabled={!editMode}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Last Name</Form.Label>
                  <Form.Control
                    type="text"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    disabled={!editMode}
                    required
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>
                <FontAwesomeIcon icon={faEnvelope} className="me-2" />
                Email Address
              </Form.Label>
              <Form.Control
                type="email"
                value={user?.email || ''}
                disabled
                className="bg-light"
              />
              <Form.Text className="text-muted">
                Email address cannot be changed
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>
                <FontAwesomeIcon icon={faPhone} className="me-2" />
                Phone Number
              </Form.Label>
              <Form.Control
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                disabled={!editMode}
                placeholder="Enter your phone number"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>
                <FontAwesomeIcon icon={faCalendar} className="me-2" />
                Date of Birth
              </Form.Label>
              <Form.Control
                type="date"
                name="date_of_birth"
                value={formData.date_of_birth}
                onChange={handleChange}
                disabled={!editMode}
              />
            </Form.Group>

            <Form.Group className="mb-4">
              <Form.Label>
                <FontAwesomeIcon icon={faMapMarkerAlt} className="me-2" />
                Address
              </Form.Label>
              <Form.Control
                as="textarea"
                name="address"
                value={formData.address}
                onChange={handleChange}
                disabled={!editMode}
                placeholder="Enter your address"
                rows={3}
              />
            </Form.Group>

            <div className="d-flex">
              <Form.Group className="mb-3">
                <Form.Label>Account Type</Form.Label>
                <Form.Control
                  type="text"
                  value={user?.role || ''}
                  disabled
                  className="bg-light"
                />
              </Form.Group>
              <Form.Group className="mb-3 ms-3">
                <Form.Label>Username</Form.Label>
                <Form.Control
                  type="text"
                  value={user?.username || ''}
                  disabled
                  className="bg-light"
                />
              </Form.Group>
            </div>

            {editMode && (
              <div className="d-flex">
                <Button
                  variant="primary"
                  type="submit"
                  disabled={loading}
                  className="me-2"
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <FontAwesomeIcon icon={faSave} className="me-2" />
                      Save Changes
                    </>
                  )}
                </Button>
                <Button variant="outline-secondary" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
            )}
          </Form>
        </Card.Body>
      </Card>
    </div>
  );
}

export default Profile;
