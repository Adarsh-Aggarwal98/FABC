// Example: How to integrate the Flask Contact API with your React frontend

// ============================================
// Option 1: Basic fetch implementation
// ============================================

const handleContactSubmit = async (formData) => {
  try {
    const response = await fetch('http://localhost:5000/api/contact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        subject: formData.subject,
        message: formData.message,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      // Success - show success message to user
      alert(data.message);
      // Reset form or redirect
    } else {
      // Error - show error message
      alert(data.message);
      console.error('Errors:', data.errors);
    }
  } catch (error) {
    // Network error
    console.error('Network error:', error);
    alert('Failed to send message. Please try again later.');
  }
};

// ============================================
// Option 2: React component example
// ============================================

import { useState } from 'react';

const ContactForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: '',
  });
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState({ type: '', message: '' });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setStatus({ type: '', message: '' });

    try {
      const response = await fetch('http://localhost:5000/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        setStatus({
          type: 'success',
          message: data.message,
        });
        // Reset form
        setFormData({
          name: '',
          email: '',
          phone: '',
          subject: '',
          message: '',
        });
      } else {
        setStatus({
          type: 'error',
          message: data.message,
        });
      }
    } catch (error) {
      setStatus({
        type: 'error',
        message: 'Failed to send message. Please try again later.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="name"
        value={formData.name}
        onChange={handleChange}
        placeholder="Your Name"
        required
      />
      <input
        type="email"
        name="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="Your Email"
        required
      />
      <input
        type="tel"
        name="phone"
        value={formData.phone}
        onChange={handleChange}
        placeholder="Your Phone (optional)"
      />
      <input
        type="text"
        name="subject"
        value={formData.subject}
        onChange={handleChange}
        placeholder="Subject"
      />
      <textarea
        name="message"
        value={formData.message}
        onChange={handleChange}
        placeholder="Your Message"
        required
      />

      <button type="submit" disabled={loading}>
        {loading ? 'Sending...' : 'Send Message'}
      </button>

      {status.message && (
        <div className={`alert alert-${status.type}`}>
          {status.message}
        </div>
      )}
    </form>
  );
};

export default ContactForm;

// ============================================
// Option 3: Using environment variables
// ============================================

// Create a .env.local file in your React app:
// VITE_API_URL=http://localhost:5000

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const submitContact = async (formData) => {
  const response = await fetch(`${API_URL}/api/contact`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(formData),
  });
  return response.json();
};

// ============================================
// Option 4: Using axios (if you prefer)
// ============================================

import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

const submitContactForm = async (formData) => {
  try {
    const { data } = await api.post('/contact', formData);
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      message: error.response?.data?.message || 'Failed to send message',
    };
  }
};
