import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../services/api';

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Login step 1: Validate credentials and request OTP (or get tokens if 2FA disabled)
      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.login(email, password);
          const data = response.data.data || response.data;

          // If 2FA is disabled, tokens are returned directly
          if (!data.requires_2fa && data.access_token) {
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);

            set({
              user: data.user,
              isAuthenticated: true,
              isLoading: false,
            });
          } else {
            set({ isLoading: false });
          }

          return response;
        } catch (error) {
          set({
            isLoading: false,
            error: error.response?.data?.error || 'Login failed',
          });
          throw error;
        }
      },

      // Login step 2: Verify OTP and get tokens
      verifyOTP: async (email, otp) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authAPI.verifyOTP(email, otp);
          const { access_token, refresh_token, user, is_first_login } = response.data.data;

          localStorage.setItem('access_token', access_token);
          localStorage.setItem('refresh_token', refresh_token);

          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });

          return { user, is_first_login };
        } catch (error) {
          set({
            isLoading: false,
            error: error.response?.data?.error || 'OTP verification failed',
          });
          throw error;
        }
      },

      // Fetch current user
      fetchUser: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }

        set({ isLoading: true });
        try {
          const response = await authAPI.getCurrentUser();
          set({
            user: response.data.data,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error) {
          set({
            isAuthenticated: false,
            user: null,
            isLoading: false,
          });
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      },

      // Update user in store
      updateUser: (userData) => {
        set({ user: { ...get().user, ...userData } });
      },

      // Logout
      logout: () => {
        localStorage.clear();
        set({
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },

      // Clear error
      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;
