// API Configuration and utilities

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export interface ContactFormData {
  name: string;
  email: string;
  phone?: string;
  state?: string;
  subject: string;
  message: string;
}

export interface ApiResponse<T = any> {
  status: 'success' | 'error';
  message: string;
  data?: T;
  errors?: string[];
}

/**
 * Submit contact form to backend API
 */
export const submitContactForm = async (
  formData: ContactFormData
): Promise<ApiResponse> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/contact`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formData),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || 'Failed to send message');
    }

    return data;
  } catch (error) {
    console.error('Contact form submission error:', error);

    if (error instanceof Error) {
      return {
        status: 'error',
        message: error.message,
      };
    }

    return {
      status: 'error',
      message: 'An unexpected error occurred. Please try again later.',
    };
  }
};

/**
 * Check API health
 */
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    const data = await response.json();
    return data.status === 'healthy';
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
};
