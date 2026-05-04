import React from 'react';
import { Button, Alert } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus } from '@fortawesome/free-solid-svg-icons';
import CreateDoctor from './CreateDoctor';

function QuickCreateDoctor() {
  const [showForm, setShowForm] = React.useState(false);

  return (
    <div className="mb-4">
      {!showForm ? (
        <Button
          variant="primary"
          size="lg"
          onClick={() => setShowForm(true)}
          className="w-100"
        >
          <FontAwesomeIcon icon={faPlus} className="me-2" />
          CREATE NEW DOCTOR PROFILE
        </Button>
      ) : (
        <CreateDoctor
          onDoctorCreated={() => setShowForm(false)}
          onCancel={() => setShowForm(false)}
        />
      )}
    </div>
  );
}

export default QuickCreateDoctor;
