import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useLocation } from "wouter";

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: "user" | "accountant" | "admin";
  status: "pending" | "approved" | "rejected" | "suspended";
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ requires2FA: boolean; message?: string }>;
  verify2FA: (code: string) => Promise<{ success: boolean; message?: string }>;
  resend2FA: () => Promise<{ success: boolean; message?: string }>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [, setLocation] = useLocation();

  const checkAuth = async () => {
    try {
      const response = await fetch("/api/auth/me", { credentials: "include" });
      if (response.ok) {
        const data = await response.json();
        setUser(data.user);
      } else {
        setUser(null);
      }
    } catch {
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        return { requires2FA: false, success: false, message: data.error || data.message || "Login failed" };
      }

      // Check if 2FA was skipped (direct login for test accounts)
      if (data.requires2FA === false && data.user) {
        setUser(data.user);
        return { requires2FA: false, success: true, message: data.message };
      }

      return { requires2FA: true, success: true, message: data.message };
    } catch (error) {
      return { requires2FA: false, success: false, message: "Network error. Please try again." };
    }
  };

  const verify2FA = async (code: string) => {
    try {
      const response = await fetch("/api/auth/verify-2fa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ code }),
      });

      const data = await response.json();

      if (response.ok) {
        setUser(data.user);
        return { success: true };
      }

      return { success: false, message: data.error || "Invalid verification code" };
    } catch (error) {
      return { success: false, message: "Network error. Please try again." };
    }
  };

  const resend2FA = async () => {
    try {
      const response = await fetch("/api/auth/resend-2fa", {
        method: "POST",
        credentials: "include",
      });

      const data = await response.json();

      if (response.ok) {
        return { success: true, message: data.message };
      }

      return { success: false, message: data.error || "Failed to resend code" };
    } catch (error) {
      return { success: false, message: "Network error. Please try again." };
    }
  };

  const logout = async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setUser(null);
      setLocation("/login");
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        verify2FA,
        resend2FA,
        logout,
        checkAuth,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}
