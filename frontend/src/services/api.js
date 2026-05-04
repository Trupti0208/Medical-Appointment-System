import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          const response = await axios.post('http://127.0.0.1:8000/api/auth/refresh/', {
            refresh: refreshToken,
          });

          const { access } = response.data;
          localStorage.setItem('accessToken', access);

          // Retry the original request
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Authentication Services
export const authService = {
  login: async (email, password) => {
    const response = await api.post('/auth/login/', { email, password });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  logout: async () => {
    const refreshToken = localStorage.getItem('refreshToken');
    const response = await api.post('/auth/logout/', { refresh: refreshToken });
    return response.data;
  },

  getProfile: async () => {
    const response = await api.get('/auth/profile/');
    return response.data;
  },

  updateProfile: async (userData) => {
    const response = await api.put('/auth/profile/', userData);
    return response.data;
  },
};

// Doctor Services
export const doctorService = {
  getDoctors: async (params = {}) => {
    const response = await api.get('/doctors/', { params });
    return response.data;
  },

  getDoctor: async (id) => {
    const response = await api.get(`/doctors/${id}/`);
    return response.data;
  },

  getDoctorSlots: async (id, date) => {
    const response = await api.get(`/doctors/${id}/available-slots/`, {
      params: { date },
    });
    return response.data;
  },

  getSpecializations: async () => {
    const response = await api.get('/doctors/specializations/');
    return response.data;
  },

  getMyDoctorProfile: async () => {
    const response = await api.get('/doctors/my-profile/');
    return response.data;
  },

  updateDoctorProfile: async (id, data) => {
    const response = await api.put(`/doctors/${id}/update/`, data);
    return response.data;
  },

  createDoctor: async (doctorData) => {
    const response = await api.post('/doctors/', doctorData);
    return response.data;
  },
};

// Appointment Services
export const appointmentService = {
  getAppointments: async (params = {}) => {
    const response = await api.get('/appointments/', { params });
    return response.data;
  },

  getAppointment: async (id) => {
    const response = await api.get(`/appointments/${id}/`);
    return response.data;
  },

  createAppointment: async (data) => {
    const response = await api.post('/appointments/', data);
    return response.data;
  },

  updateAppointment: async (id, data) => {
    const response = await api.put(`/appointments/${id}/`, data);
    return response.data;
  },

  cancelAppointment: async (id) => {
    const response = await api.post(`/appointments/${id}/cancel/`);
    return response.data;
  },

  rescheduleAppointment: async (id, data) => {
    const response = await api.post(`/appointments/${id}/reschedule/`, data);
    return response.data;
  },

  getMyAppointments: async (params = {}) => {
    const response = await api.get('/appointments/my-appointments/', { params });
    return response.data;
  },

  getDashboard: async () => {
    const response = await api.get('/appointments/dashboard/');
    return response.data;
  },

  getRescheduleRequests: async () => {
    const response = await api.get('/appointments/reschedule-requests/');
    return response.data;
  },

  approveReschedule: async (id) => {
    const response = await api.post(`/appointments/reschedule-requests/${id}/approve/`);
    return response.data;
  },

  rejectReschedule: async (id, reason) => {
    const response = await api.post(`/appointments/reschedule-requests/${id}/reject/`, {
      rejection_reason: reason,
    });
    return response.data;
  },
};

// Notification Services
export const notificationService = {
  getNotifications: async (params = {}) => {
    const response = await api.get('/notifications/', { params });
    return response.data;
  },

  getNotification: async (id) => {
    const response = await api.get(`/notifications/${id}/`);
    return response.data;
  },

  markAsRead: async (id) => {
    const response = await api.post(`/notifications/${id}/mark-read/`);
    return response.data;
  },

  markAsUnread: async (id) => {
    const response = await api.post(`/notifications/${id}/mark-unread/`);
    return response.data;
  },

  markAllAsRead: async () => {
    const response = await api.post('/notifications/mark-all-read/');
    return response.data;
  },

  getNotificationCount: async () => {
    const response = await api.get('/notifications/count/');
    return response.data;
  },

  getPreferences: async () => {
    const response = await api.get('/notifications/preferences/');
    return response.data;
  },

  updatePreferences: async (data) => {
    const response = await api.put('/notifications/preferences/', data);
    return response.data;
  },
};

export default api;
