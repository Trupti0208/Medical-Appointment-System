import React, { useState } from 'react';
import { Card, Button, Alert, Container } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus, faArrowLeft } from '@fortawesome/free-solid-svg-icons';
import CreateDoctor from './CreateDoctor';

function CreateDoctorPage() {
  const [showForm, setShowForm] = useState(false);

  return (
    <Container className="py-4">
      <div className="text-center mb-4">
        <h1 className="mb-4">
          <FontAwesomeIcon icon={faPlus} className="me-3" />
          Create New Doctor
        </h1>
        <p className="text-muted">
          Add a new doctor profile to the medical appointment system
        </p>
      </div>

      {/* MASSIVE CREATE DOCTOR BUTTON */}
      <div style={{ 
        backgroundColor: '#007bff', 
        padding: '40px', 
        margin: '30px 0', 
        borderRadius: '15px',
        textAlign: 'center',
        border: '5px solid #0056b3',
        boxShadow: '0 8px 16px rgba(0,0,0,0.3)'
      }}>
        <h2 style={{ 
          color: 'white', 
          marginBottom: '25px', 
          fontSize: '36px',
          fontWeight: 'bold'
        }}>
          <FontAwesomeIcon icon={faPlus} style={{ marginRight: '15px' }} />
          CREATE NEW DOCTOR PROFILE
        </h2>
        <p style={{ 
          color: 'white', 
          fontSize: '18px', 
          marginBottom: '30px' 
        }}>
          Click the button below to add a new doctor to the system
        </p>
        <Button
          variant="light"
          size="lg"
          onClick={() => setShowForm(true)}
          style={{ 
            fontSize: '24px', 
            padding: '20px 60px',
            fontWeight: 'bold',
            backgroundColor: '#28a745',
            borderColor: '#28a745',
            color: 'white',
            boxShadow: '0 4px 8px rgba(0,0,0,0.2)'
          }}
        >
          <FontAwesomeIcon icon={faPlus} style={{ marginRight: '15px' }} />
          CLICK HERE TO CREATE DOCTOR
        </Button>
      </div>

      {showForm && (
        <div style={{ 
          margin: '30px 0',
          padding: '20px',
          backgroundColor: '#f8f9fa',
          border: '2px solid #dee2e6',
          borderRadius: '10px'
        }}>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h3>
              <FontAwesomeIcon icon={faPlus} className="me-2" />
              Doctor Creation Form
            </h3>
            <Button
              variant="outline-secondary"
              onClick={() => setShowForm(false)}
            >
              <FontAwesomeIcon icon={faArrowLeft} className="me-2" />
              Back to Dashboard
            </Button>
          </div>
          
          <CreateDoctor
            onDoctorCreated={() => {
              setShowForm(false);
              alert('Doctor created successfully!');
            }}
            onCancel={() => setShowForm(false)}
          />
        </div>
      )}

      {!showForm && (
        <Card className="mt-4">
          <Card.Header>
            <h5 className="mb-0">
              <FontAwesomeIcon icon={faPlus} className="me-2" />
              Alternative Options
            </h5>
          </Card.Header>
          <Card.Body>
            <div className="text-center">
              <p className="mb-3">
                If the button above doesn't work, you can try:
              </p>
              <div className="d-flex justify-content-center gap-3">
                <Button variant="outline-primary" size="lg">
                  <FontAwesomeIcon icon={faPlus} className="me-2" />
                  Alternative Create Button
                </Button>
                <Button variant="outline-success" size="lg">
                  <FontAwesomeIcon icon={faPlus} className="me-2" />
                  Backup Create Option
                </Button>
              </div>
            </div>
          </Card.Body>
        </Card>
      )}
    </Container>
  );
}

export default CreateDoctorPage;
