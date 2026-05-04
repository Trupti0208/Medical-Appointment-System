# Medical Appointment Scheduling System

A comprehensive real-time medical appointment scheduling system built with Django + Django REST Framework backend and React frontend.

## Features

### Backend (Django + DRF)
- **User Management**: Multi-role authentication (Patient, Doctor, Admin)
- **JWT Authentication**: Secure token-based authentication
- **Doctor Management**: Complete doctor profiles with specializations and availability
- **Appointment System**: Book, reschedule, cancel appointments
- **Real-time Features**: WebSocket support for instant updates
- **Notification System**: Automated notifications for appointments
- **Admin Interface**: Django admin for system management

### Frontend (React)
- **Modern UI**: Clean, responsive design with Bootstrap
- **Role-based Dashboards**: Different interfaces for patients, doctors, and admins
- **Real-time Updates**: Live notification system
- **Appointment Booking**: Interactive booking flow
- **Profile Management**: User profile editing

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Environment Setup**
```bash
# Copy .env file and update if needed
cp .env.example .env
```

3. **Database Setup**
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create sample data
python manage.py setup_sample_data
```

4. **Start Backend Server**
```bash
python manage.py runserver
```

The backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to Frontend Directory**
```bash
cd frontend
```

2. **Install Dependencies**
```bash
npm install
```

3. **Start Frontend Server**
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Default Login Credentials

### Admin User
- **Email**: admin@medical.com
- **Password**: password123

### Patient Users
- **Email**: john.patient@email.com
- **Password**: password123

- **Email**: jane.patient@email.com
- **Password**: password123

### Doctor Users
- **Email**: bob.doctor@medical.com
- **Password**: password123

- **Email**: alice.doctor@medical.com
- **Password**: password123

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile

### Doctors
- `GET /api/doctors/` - List all doctors
- `GET /api/doctors/{id}/` - Get doctor details
- `GET /api/doctors/{id}/available-slots/` - Get available time slots
- `GET /api/doctors/specializations/` - Get all specializations

### Appointments
- `GET /api/appointments/` - List appointments
- `POST /api/appointments/` - Create appointment
- `PUT /api/appointments/{id}/` - Update appointment
- `POST /api/appointments/{id}/cancel/` - Cancel appointment
- `POST /api/appointments/{id}/reschedule/` - Request reschedule

### Notifications
- `GET /api/notifications/` - List notifications
- `POST /api/notifications/{id}/mark-read/` - Mark as read
- `GET /api/notifications/count/` - Get notification count

## Project Structure

```
medical-appointment-system/
├── medical_project/          # Django project settings
├── accounts/                 # User management app
├── doctors/                  # Doctor management app
├── appointments/             # Appointment system app
├── notifications/            # Notification system app
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API services
│   │   └── App.js           # Main App component
│   └── package.json
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
└── README.md                 # This file
```

## Features by Role

### Patients
- Browse and search doctors
- Book appointments
- View appointment history
- Cancel/reschedule appointments
- Receive notifications

### Doctors
- View appointment schedule
- Approve/reject appointments
- Manage availability
- View patient information
- Update profile

### Administrators
- Manage all users
- View system statistics
- Manage doctor profiles
- Monitor appointments
- Send announcements

## Technology Stack

### Backend
- **Django 4.2** - Web framework
- **Django REST Framework** - API framework
- **Simple JWT** - Authentication
- **Django Channels** - WebSocket support
- **SQLite** - Database (development)

### Frontend
- **React 18** - UI framework
- **React Router** - Navigation
- **Bootstrap 5** - UI components
- **Axios** - HTTP client
- **Font Awesome** - Icons

## Development

### Running Tests
```bash
# Backend tests
python manage.py test

# Frontend tests
cd frontend
npm test
```

### Database Migrations
```bash
# Create new migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Creating Sample Data
```bash
python manage.py setup_sample_data
```

## Production Deployment

### Backend
1. Set `DEBUG=False` in production
2. Configure production database (PostgreSQL recommended)
3. Set up proper `SECRET_KEY`
4. Configure `ALLOWED_HOSTS`
5. Set up static files serving
6. Configure HTTPS

### Frontend
1. Build the production bundle
```bash
cd frontend
npm run build
```
2. Serve the build files with a web server (Nginx, Apache)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For any questions or issues, please contact the development team.
