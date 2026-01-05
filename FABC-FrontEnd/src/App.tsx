import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/AuthContext";
import { ProtectedRoute } from "@/components/auth/ProtectedRoute";
import { PublicRoute } from "@/components/auth/PublicRoute";

// Public pages
import Home from "@/pages/Home";
import About from "@/pages/About";
import Services from "@/pages/Services";
import Team from "@/pages/Team";
import Blog from "@/pages/Blog";
import Accountants from "@/pages/Accountants";
import Trustees from "@/pages/Trustees";
import Contact from "@/pages/Contact";
import Privacy from "@/pages/Privacy";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import NotFound from "@/pages/not-found";

// Protected pages
import Dashboard from "@/pages/Dashboard";
import Documents from "@/pages/Documents";
import AdminDashboard from "@/pages/admin/AdminDashboard";

function Router() {
  return (
    <Switch>
      {/* Public routes - redirect to dashboard if logged in */}
      <Route path="/">
        <PublicRoute>
          <Home />
        </PublicRoute>
      </Route>
      <Route path="/about">
        <PublicRoute>
          <About />
        </PublicRoute>
      </Route>
      <Route path="/services">
        <PublicRoute>
          <Services />
        </PublicRoute>
      </Route>
      <Route path="/team">
        <PublicRoute>
          <Team />
        </PublicRoute>
      </Route>
      <Route path="/blog">
        <PublicRoute>
          <Blog />
        </PublicRoute>
      </Route>
      <Route path="/accountants">
        <PublicRoute>
          <Accountants />
        </PublicRoute>
      </Route>
      <Route path="/trustees">
        <PublicRoute>
          <Trustees />
        </PublicRoute>
      </Route>
      <Route path="/contact">
        <PublicRoute>
          <Contact />
        </PublicRoute>
      </Route>
      <Route path="/privacy">
        <PublicRoute>
          <Privacy />
        </PublicRoute>
      </Route>
      <Route path="/login">
        <PublicRoute>
          <Login />
        </PublicRoute>
      </Route>
      <Route path="/register">
        <PublicRoute>
          <Register />
        </PublicRoute>
      </Route>
      <Route path="/register/:token">
        <PublicRoute>
          <Register />
        </PublicRoute>
      </Route>

      {/* Protected routes - all authenticated users */}
      <Route path="/dashboard">
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      </Route>

      <Route path="/documents">
        <ProtectedRoute>
          <Documents />
        </ProtectedRoute>
      </Route>

      {/* Admin only routes */}
      <Route path="/admin">
        <ProtectedRoute roles={["admin"]}>
          <AdminDashboard />
        </ProtectedRoute>
      </Route>

      <Route path="/admin/users">
        <ProtectedRoute roles={["admin"]}>
          <AdminDashboard />
        </ProtectedRoute>
      </Route>

      {/* 404 */}
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
