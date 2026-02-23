import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import useAuthStore from './store/authStore';
import useThemeStore from './store/themeStore';

// Auth Pages
import Login from './pages/auth/Login';
import ForgotPassword from './pages/auth/ForgotPassword';

// Onboarding
import Onboarding from './pages/onboarding/Onboarding';

// Dashboard
import Dashboard from './pages/dashboard/Dashboard';

// Profile
import MyProfile from './pages/profile/MyProfile';

// Users
import UserList from './pages/users/UserList';
import UserDetail from './pages/users/UserDetail';

// Requests
import RequestList from './pages/requests/RequestList';
import RequestDetail from './pages/requests/RequestDetail';

// Services
import ServiceList from './pages/services/ServiceList';
import NewServiceRequest from './pages/services/NewServiceRequest';

// Forms
import FormList from './pages/forms/FormList';
import FormBuilder from './pages/forms/FormBuilder';

// Companies
import CompanyList from './pages/companies/CompanyList';
import CompanyDetail from './pages/companies/CompanyDetail';

// Client Entities
import ClientEntityList from './pages/client-entities/ClientEntityList';
import ClientEntityDetail from './pages/client-entities/ClientEntityDetail';

// Letters
import LetterGenerator from './pages/letters/LetterGenerator';

// SMSF Data Sheet
import SMSFDataSheet from './pages/smsf-data-sheet/SMSFDataSheet';

// Blog & ATO Alerts (website content management)
import BlogManagement from './pages/settings/BlogManagement';
import AtoAlerts from './pages/settings/AtoAlerts';

// Settings
import InvoiceSettings from './pages/settings/InvoiceSettings';
import EmailTemplates from './pages/settings/EmailTemplates';
import BrandingSettings from './pages/settings/BrandingSettings';
import JobAnalytics from './pages/settings/JobAnalytics';
import AdminAnalytics from './pages/settings/AdminAnalytics';
import CompanySettings from './pages/settings/CompanySettings';
import EmailStorageSettings from './pages/settings/EmailStorageSettings';
import WorkflowList from './pages/settings/WorkflowList';
import WorkflowBuilder from './pages/settings/WorkflowBuilder';
import DataImport from './pages/settings/DataImport';
import StatusSettings from './pages/settings/StatusSettings';
import Leads from './pages/settings/Leads';

// Protected Route Wrapper
function ProtectedRoute({ children, allowedRoles = [] }) {
  const { isAuthenticated, user, isLoading, fetchUser } = useAuthStore();
  const { fetchTheme, isLoaded: themeLoaded } = useThemeStore();

  useEffect(() => {
    if (!user) {
      fetchUser();
    }
  }, []);

  // Fetch theme when user is authenticated
  useEffect(() => {
    if (isAuthenticated && user && !themeLoaded) {
      fetchTheme();
    }
  }, [isAuthenticated, user, themeLoaded]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Check if user needs to complete onboarding
  if (user?.is_first_login && !window.location.pathname.endsWith('/onboarding')) {
    return <Navigate to="/onboarding" replace />;
  }

  // Check role access
  if (allowedRoles.length > 0 && !allowedRoles.includes(user?.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

// Public Route Wrapper (redirects to dashboard if logged in)
function PublicRoute({ children }) {
  const { isAuthenticated, user } = useAuthStore();

  if (isAuthenticated && user) {
    if (user.is_first_login) {
      return <Navigate to="/onboarding" replace />;
    }
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}

export default function App() {
  return (
    <BrowserRouter basename="/crm">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            borderRadius: '8px',
            background: '#333',
            color: '#fff',
          },
        }}
      />

      <Routes>

        {/* Public Routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />
        <Route
          path="/forgot-password"
          element={
            <PublicRoute>
              <ForgotPassword />
            </PublicRoute>
          }
        />

        {/* Onboarding */}
        <Route
          path="/onboarding"
          element={
            <ProtectedRoute>
              <Onboarding />
            </ProtectedRoute>
          }
        />

        {/* Dashboard */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Profile */}
        <Route
          path="/profile"
          element={
            <ProtectedRoute>
              <MyProfile />
            </ProtectedRoute>
          }
        />

        {/* Companies - Super Admin Only */}
        <Route
          path="/companies"
          element={
            <ProtectedRoute allowedRoles={['super_admin']}>
              <CompanyList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/companies/:id"
          element={
            <ProtectedRoute allowedRoles={['super_admin']}>
              <CompanyDetail />
            </ProtectedRoute>
          }
        />

        {/* Client Entities - Admin, Senior Accountant and Accountants */}
        <Route
          path="/client-entities"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant', 'accountant']}>
              <ClientEntityList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/client-entities/:id"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant', 'accountant']}>
              <ClientEntityDetail />
            </ProtectedRoute>
          }
        />

        {/* Users - Admin and Senior Accountant */}
        <Route
          path="/users"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant']}>
              <UserList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/users/:id"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant', 'accountant']}>
              <UserDetail />
            </ProtectedRoute>
          }
        />

        {/* Requests */}
        <Route
          path="/requests"
          element={
            <ProtectedRoute>
              <RequestList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/requests/:id"
          element={
            <ProtectedRoute>
              <RequestDetail />
            </ProtectedRoute>
          }
        />

        {/* Services */}
        <Route
          path="/services"
          element={
            <ProtectedRoute>
              <ServiceList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/services/new"
          element={
            <ProtectedRoute allowedRoles={['user']}>
              <NewServiceRequest />
            </ProtectedRoute>
          }
        />

        {/* Forms - Admin, Senior Accountant and Super Admin */}
        <Route
          path="/forms"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant']}>
              <FormList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/forms/new"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant']}>
              <FormBuilder />
            </ProtectedRoute>
          }
        />
        <Route
          path="/forms/:id"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant']}>
              <FormBuilder />
            </ProtectedRoute>
          }
        />

        {/* Settings - Admin only (Company settings and Branding excluded for senior_accountant) */}
        <Route
          path="/settings/company"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin']}>
              <CompanySettings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/invoice"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin']}>
              <InvoiceSettings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/email-templates"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant']}>
              <EmailTemplates />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/branding"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin']}>
              <BrandingSettings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/analytics"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'accountant']}>
              <JobAnalytics />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/admin-analytics"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin']}>
              <AdminAnalytics />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/import"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin']}>
              <DataImport />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/email-storage"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin']}>
              <EmailStorageSettings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/workflows"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant']}>
              <WorkflowList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/workflows/:workflowId"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant']}>
              <WorkflowBuilder />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/statuses"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant']}>
              <StatusSettings />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leads"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin']}>
              <Leads />
            </ProtectedRoute>
          }
        />
        <Route
          path="/letters"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant', 'accountant']}>
              <LetterGenerator />
            </ProtectedRoute>
          }
        />
        <Route
          path="/smsf-data-sheet"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin', 'senior_accountant', 'accountant']}>
              <SMSFDataSheet />
            </ProtectedRoute>
          }
        />

        {/* Website Content Management */}
        <Route
          path="/settings/blogs"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin']}>
              <BlogManagement />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings/ato-alerts"
          element={
            <ProtectedRoute allowedRoles={['super_admin', 'admin']}>
              <AtoAlerts />
            </ProtectedRoute>
          }
        />

        {/* Default Redirect */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
