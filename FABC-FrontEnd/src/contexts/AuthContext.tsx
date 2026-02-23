import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useLocation } from "wouter";

// ── API base URL ────────────────────────────────────────────────────────────
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:9001/api";

// ── Token helpers ───────────────────────────────────────────────────────────
const getAccessToken  = () => localStorage.getItem("access_token");
const getRefreshToken = () => localStorage.getItem("refresh_token");
const setTokens = (access: string, refresh: string) => {
  localStorage.setItem("access_token",  access);
  localStorage.setItem("refresh_token", refresh);
};
const clearTokens = () => {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
};

// ── Authenticated fetch with auto-refresh ───────────────────────────────────
export async function authFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getAccessToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res = await fetch(url, { ...options, headers });

  // Try to refresh on 401
  if (res.status === 401) {
    const refresh = getRefreshToken();
    if (refresh) {
      try {
        const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
          method:  "POST",
          headers: { Authorization: `Bearer ${refresh}` },
        });
        if (refreshRes.ok) {
          const data = await refreshRes.json();
          const newAccess = data?.data?.access_token;
          if (newAccess) {
            localStorage.setItem("access_token", newAccess);
            headers["Authorization"] = `Bearer ${newAccess}`;
            res = await fetch(url, { ...options, headers });
          }
        } else {
          clearTokens();
        }
      } catch {
        clearTokens();
      }
    } else {
      clearTokens();
    }
  }

  return res;
}

// ── User type (matches CRM backend shape) ───────────────────────────────────
export interface User {
  id:             string;
  email:          string;
  first_name:     string;
  last_name:      string;
  full_name:      string;
  role:           "user" | "accountant" | "senior_accountant" | "admin" | "super_admin";
  is_active:      boolean;
  is_verified:    boolean;
  is_first_login: boolean;
}

interface AuthContextType {
  user:            User | null;
  isLoading:       boolean;
  isAuthenticated: boolean;
  pendingEmail:    string | null;
  login:     (email: string, password: string) => Promise<{ requires2FA: boolean; success: boolean; message?: string; role?: string }>;
  verifyOTP: (otp: string) => Promise<{ success: boolean; message?: string; role?: string }>;
  resendOTP: () => Promise<{ success: boolean; message?: string }>;
  logout:    () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

// ── Provider ─────────────────────────────────────────────────────────────────
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user,         setUser]         = useState<User | null>(null);
  const [isLoading,    setIsLoading]    = useState(true);
  const [pendingEmail, setPendingEmail] = useState<string | null>(null);
  const [, setLocation] = useLocation();

  // ── Restore session on mount ────────────────────────────────────────────
  const checkAuth = async () => {
    const token = getAccessToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }
    try {
      const res = await authFetch(`${API_BASE}/auth/me`);
      if (res.ok) {
        const data = await res.json();
        setUser(data?.data ?? null);
      } else {
        clearTokens();
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => { checkAuth(); }, []);

  // ── Step 1: Validate credentials ────────────────────────────────────────
  const login = async (email: string, password: string) => {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ email, password }),
      });

      const data = await res.json();

      if (!res.ok) {
        return { requires2FA: false, success: false, message: data?.error || "Login failed" };
      }

      const payload = data?.data ?? data;

      // 2FA required — store email for OTP step
      if (payload.requires_2fa) {
        setPendingEmail(email);
        return { requires2FA: true, success: true, message: payload.message };
      }

      // Direct login (2FA disabled) — tokens returned immediately
      if (payload.access_token) {
        setTokens(payload.access_token, payload.refresh_token || "");
        setUser(payload.user ?? null);
        return { requires2FA: false, success: true, role: payload.user?.role };
      }

      return { requires2FA: false, success: false, message: "Unexpected response from server" };
    } catch {
      return { requires2FA: false, success: false, message: "Network error. Please try again." };
    }
  };

  // ── Step 2: Verify OTP ──────────────────────────────────────────────────
  const verifyOTP = async (otp: string) => {
    if (!pendingEmail) {
      return { success: false, message: "Session expired. Please log in again." };
    }
    try {
      const res = await fetch(`${API_BASE}/auth/verify-otp`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ email: pendingEmail, otp }),
      });

      const data = await res.json();

      if (res.ok) {
        const payload = data?.data ?? data;
        setTokens(payload.access_token, payload.refresh_token || "");
        setUser(payload.user ?? null);
        setPendingEmail(null);
        return { success: true, role: payload.user?.role };
      }

      return { success: false, message: data?.error || "Invalid or expired code" };
    } catch {
      return { success: false, message: "Network error. Please try again." };
    }
  };

  // ── Resend OTP ───────────────────────────────────────────────────────────
  const resendOTP = async () => {
    if (!pendingEmail) {
      return { success: false, message: "No pending login session." };
    }
    try {
      const res = await fetch(`${API_BASE}/auth/resend-otp`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ email: pendingEmail }),
      });
      const data = await res.json();
      if (res.ok) return { success: true, message: data?.data?.message || "Code resent" };
      return { success: false, message: data?.error || "Failed to resend code" };
    } catch {
      return { success: false, message: "Network error." };
    }
  };

  // ── Logout ───────────────────────────────────────────────────────────────
  const logout = () => {
    clearTokens();
    setUser(null);
    setPendingEmail(null);
    setLocation("/login");
  };

  return (
    <AuthContext.Provider value={{
      user, isLoading, isAuthenticated: !!user,
      pendingEmail,
      login, verifyOTP, resendOTP, logout, checkAuth,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
