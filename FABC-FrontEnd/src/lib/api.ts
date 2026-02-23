// API Configuration and utilities

// Always use relative paths — Vite proxy (dev) and Nginx (prod) route /api/* to the backend
const API_BASE_URL = '';

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

export interface Blog {
  id: string;
  title: string;
  slug: string;
  excerpt: string;
  content: string | null;
  category: string;
  author: string;
  readTime: string;
  image: string | null;
  featured: boolean | null;
  published: boolean | null;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface AtoAlert {
  id: string;
  title: string;
  type: 'update' | 'alert' | 'reminder';
  link: string;
  active: boolean | null;
  priority: number | null;
  createdAt: string | null;
  expiresAt: string | null;
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
 * Fetch all published blogs
 */
export const fetchBlogs = async (): Promise<Blog[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/blogs`);
    if (!response.ok) {
      throw new Error('Failed to fetch blogs');
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch blogs:', error);
    return [];
  }
};

/**
 * Fetch a single blog by slug
 */
export const fetchBlogBySlug = async (slug: string): Promise<Blog | null> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/blogs/slug/${slug}`);
    if (!response.ok) {
      throw new Error('Blog not found');
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch blog:', error);
    return null;
  }
};

/**
 * Fetch active ATO alerts
 */
export const fetchAtoAlerts = async (): Promise<AtoAlert[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ato-alerts`);
    if (!response.ok) {
      throw new Error('Failed to fetch ATO alerts');
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch ATO alerts:', error);
    return [];
  }
};

/**
 * Check API health
 */
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    const data = await response.json();
    return data.status === 'ok';
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
};
