import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Alert, Form } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faBell, faCheck, faEnvelope, faCalendarAlt,
  faUserMd, faTimes, faRefresh
} from '@fortawesome/free-solid-svg-icons';
import { notificationService } from '../services/api';

function Notifications() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    try {
      const response = await notificationService.getNotifications();
      setNotifications(response.results || response);
    } catch (error) {
      setError('Failed to load notifications');
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationService.markAsRead(notificationId);
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
    } catch (error) {
      setError('Failed to mark notification as read');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (error) {
      setError('Failed to mark all notifications as read');
    }
  };

  const getNotificationIcon = (type) => {
    const icons = {
      'APPOINTMENT_BOOKED': faCalendarAlt,
      'APPOINTMENT_CANCELLED': faTimes,
      'APPOINTMENT_CONFIRMED': faCheck,
      'APPOINTMENT_RESCHEDULED': faCalendarAlt,
      'APPOINTMENT_REMINDER': faBell,
      'PAYMENT_RECEIVED': faCheck,
      'PAYMENT_FAILED': faTimes,
      'MEDICAL_RECORD_UPDATED': faUserMd,
      'DOCTOR_AVAILABLE': faUserMd,
      'SYSTEM_ANNOUNCEMENT': faBell,
    };
    return icons[type] || faBell;
  };

  const getNotificationColor = (type) => {
    const colors = {
      'APPOINTMENT_BOOKED': 'primary',
      'APPOINTMENT_CANCELLED': 'danger',
      'APPOINTMENT_CONFIRMED': 'success',
      'APPOINTMENT_RESCHEDULED': 'warning',
      'APPOINTMENT_REMINDER': 'info',
      'PAYMENT_RECEIVED': 'success',
      'PAYMENT_FAILED': 'danger',
      'MEDICAL_RECORD_UPDATED': 'primary',
      'DOCTOR_AVAILABLE': 'success',
      'SYSTEM_ANNOUNCEMENT': 'warning',
    };
    return colors[type] || 'secondary';
  };

  const filteredNotifications = notifications.filter(notification => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !notification.is_read;
    if (filter === 'important') return notification.is_important;
    return true;
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
          <h1 className="mb-1">Notifications</h1>
          <p className="text-muted mb-0">View and manage your notifications</p>
        </div>
        <div>
          <Button variant="outline-secondary" onClick={fetchNotifications} className="me-2">
            <FontAwesomeIcon icon={faRefresh} className="me-2" />
            Refresh
          </Button>
          <Button variant="primary" onClick={handleMarkAllAsRead}>
            <FontAwesomeIcon icon={faCheck} className="me-2" />
            Mark All as Read
          </Button>
        </div>
      </div>

      {error && <Alert variant="danger">{error}</Alert>}

      {/* Filter */}
      <Card className="mb-4">
        <Card.Body>
          <div className="d-flex align-items-center">
            <FontAwesomeIcon icon={faBell} className="me-2" />
            <span className="me-3">Filter:</span>
            <Form.Check
              type="radio"
              label="All"
              name="filter"
              value="all"
              checked={filter === 'all'}
              onChange={(e) => setFilter(e.target.value)}
              className="me-3"
            />
            <Form.Check
              type="radio"
              label="Unread"
              name="filter"
              value="unread"
              checked={filter === 'unread'}
              onChange={(e) => setFilter(e.target.value)}
              className="me-3"
            />
            <Form.Check
              type="radio"
              label="Important"
              name="filter"
              value="important"
              checked={filter === 'important'}
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
        </Card.Body>
      </Card>

      {/* Notifications List */}
      <Card>
        <Card.Header>
          <h5 className="mb-0">
            Notifications ({filteredNotifications.length})
          </h5>
        </Card.Header>
        <Card.Body>
          {filteredNotifications.length > 0 ? (
            <div>
              {filteredNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className={`notification-item p-3 border-bottom ${notification.is_read ? 'bg-light' : 'bg-white'}`}
                >
                  <div className="d-flex justify-content-between align-items-start">
                    <div className="d-flex align-items-start">
                      <div className="me-3">
                        <FontAwesomeIcon
                          icon={getNotificationIcon(notification.notification_type)}
                          className={`text-${getNotificationColor(notification.notification_type)}`}
                          size="lg"
                        />
                      </div>
                      <div className="flex-grow-1">
                        <div className="d-flex align-items-center mb-1">
                          <h6 className="mb-0 me-2">{notification.title}</h6>
                          {!notification.is_read && (
                            <Badge bg="primary" className="me-2">New</Badge>
                          )}
                          {notification.is_important && (
                            <Badge bg="danger">Important</Badge>
                          )}
                        </div>
                        <p className="text-muted mb-2">{notification.message}</p>
                        <div className="d-flex align-items-center">
                          <small className="text-muted me-3">
                            {new Date(notification.created_at).toLocaleString()}
                          </small>
                          {notification.action_url && (
                            <Button
                              variant="outline-primary"
                              size="sm"
                              href={notification.action_url}
                              className="me-2"
                            >
                              {notification.action_text || 'View Details'}
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                    <div>
                      {!notification.is_read && (
                        <Button
                          variant="outline-secondary"
                          size="sm"
                          onClick={() => handleMarkAsRead(notification.id)}
                        >
                          <FontAwesomeIcon icon={faCheck} />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-5">
              <FontAwesomeIcon icon={faBell} size="3x" className="text-muted mb-3" />
              <h5>No notifications</h5>
              <p className="text-muted">
                {filter === 'all' 
                  ? "You don't have any notifications yet."
                  : `No ${filter} notifications found.`}
              </p>
            </div>
          )}
        </Card.Body>
      </Card>
    </div>
  );
}

export default Notifications;
