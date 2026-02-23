import axios from 'axios';

// Use environment variable for API URL, fallback to localhost:9001
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:9001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Handle 401 errors (token expired)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, null, {
            headers: { Authorization: `Bearer ${refreshToken}` },
          });

          const { access_token } = response.data.data;
          localStorage.setItem('access_token', access_token);

          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        } catch (refreshError) {
          // Refresh failed, logout user
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (email, password) => api.post('/auth/login', { email, password }),
  verifyOTP: (email, otp) => api.post('/auth/verify-otp', { email, otp }),
  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
  resetPassword: (data) => api.post('/auth/reset-password', data),
  getCurrentUser: () => api.get('/auth/me'),
  refresh: () => api.post('/auth/refresh'),
};

// User API
export const userAPI = {
  invite: (data) => api.post('/users/invite', data),
  list: (params) => api.get('/users', { params }),
  get: (id) => api.get(`/users/${id}`),
  update: (id, data) => api.patch(`/users/${id}`, data),
  updateProfile: (data) => api.patch('/users/profile', data),
  changePassword: (data) => api.post('/users/change-password', data),
  completeOnboarding: (data) => api.post('/users/complete-onboarding', data),
  uploadDocument: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/users/upload-document', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  toggleStatus: (id, isActive) => api.post(`/users/${id}/toggle-status`, { is_active: isActive }),
  getAccountants: () => api.get('/users/accountants'),
  getSeniorAccountants: () => api.get('/users/senior-accountants'),
  getMyTeam: () => api.get('/users/my-team'),
  // Notes
  getNotes: (userId, params) => api.get(`/users/${userId}/notes`, { params }),
  createNote: (userId, content, isPinned) => api.post(`/users/${userId}/notes`, { content, is_pinned: isPinned }),
  updateNote: (noteId, data) => api.patch(`/users/notes/${noteId}`, data),
  deleteNote: (noteId) => api.delete(`/users/notes/${noteId}`),
  toggleNotePin: (noteId) => api.patch(`/users/notes/${noteId}/pin`),
  // Duplicate check
  checkDuplicates: (data) => api.post('/users/check-duplicates', data),
  // Export
  exportUsers: (params) => api.get('/users/export', { params, responseType: 'blob' }),
  // Import
  downloadImportTemplate: () => api.get('/users/import/template', { responseType: 'blob' }),
  importClients: (file, companyId) => {
    const formData = new FormData();
    formData.append('file', file);
    if (companyId) formData.append('company_id', companyId);
    return api.post('/users/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
};

// Data Import API
export const importsAPI = {
  // Get available import types
  getTypes: () => api.get('/imports/available-types'),

  // Download templates
  downloadTemplate: (dataType) => api.get(`/imports/templates/${dataType}`, { responseType: 'blob' }),

  // Import data
  importClients: (file, companyId) => {
    const formData = new FormData();
    formData.append('file', file);
    if (companyId) formData.append('company_id', companyId);
    return api.post('/imports/clients', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  importServiceRequests: (file, companyId) => {
    const formData = new FormData();
    formData.append('file', file);
    if (companyId) formData.append('company_id', companyId);
    return api.post('/imports/service-requests', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  importServices: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/imports/services', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  importCompanies: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/imports/companies', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },
};

// Services API
export const servicesAPI = {
  list: (params) => api.get('/services', { params }),
  getAll: (params) => api.get('/services', { params }),
  get: (id) => api.get(`/services/${id}`),
  create: (data) => api.post('/services', data),
  update: (id, data) => api.patch(`/services/${id}`, data),
};

// Requests API
export const requestsAPI = {
  list: (params) => api.get('/requests', { params }),
  get: (id) => api.get(`/requests/${id}`),
  create: (serviceIds, userId = null, clientEntityId = null) => {
    const data = { service_ids: serviceIds };
    if (userId) data.user_id = userId;
    if (clientEntityId) data.client_entity_id = clientEntityId;
    return api.post('/requests', data);
  },
  createForUser: (serviceIds, userId, clientEntityId = null) => {
    const data = { service_ids: serviceIds, user_id: userId };
    if (clientEntityId) data.client_entity_id = clientEntityId;
    return api.post('/requests', data);
  },
  assign: (id, accountantId, deadlineDate = null, priority = null) => api.post(`/requests/${id}/assign`, {
    accountant_id: accountantId,
    deadline_date: deadlineDate,
    priority: priority,
  }),
  update: (id, data) => api.patch(`/requests/${id}`, data),
  updateStatus: (id, status) => api.patch(`/requests/${id}/status`, { status }),
  updateInvoice: (id, data) => api.patch(`/requests/${id}/invoice`, data),
  updateCost: (id, data) => api.patch(`/requests/${id}/cost`, data),
  addNote: (id, note) => api.post(`/requests/${id}/notes`, { note }),
  getAuditLog: (id, params) => api.get(`/requests/${id}/audit-log`, { params }),
  getQueries: (id) => api.get(`/requests/${id}/queries`),
  addQuery: (id, message, isInternal = false) => api.post(`/requests/${id}/queries`, { message, is_internal: isInternal }),
  // Reassignment
  reassign: (id, accountantId, reason = '') => api.post(`/requests/${id}/reassign`, { accountant_id: accountantId, reason }),
  // Assignment History
  getAssignmentHistory: (id) => api.get(`/requests/${id}/assignment-history`),
  // State History
  getStateHistory: (id) => api.get(`/requests/${id}/state-history`),
  getDashboardMetrics: (params) => api.get('/requests/dashboard/metrics', { params }),
  // Form Responses
  getFormResponses: (requestId) => api.get(`/requests/${requestId}/form-responses`),
  // Job Notes
  getJobNotes: (requestId, params) => api.get(`/requests/${requestId}/job-notes`, { params }),
  createJobNote: (requestId, data) => api.post(`/requests/${requestId}/job-notes`, data),
  // Drafts
  saveDraft: (data) => api.post('/requests/draft', data),
  getDrafts: () => api.get('/requests/drafts'),
  submitDraft: (requestId) => api.post(`/requests/${requestId}/submit-draft`),
  // Export
  exportRequests: (params) => api.get('/requests/export', { params, responseType: 'blob' }),
  // Invoice PDF
  getInvoicePdf: (requestId) => api.get(`/requests/${requestId}/invoice/pdf`, { responseType: 'blob' }),
  previewInvoicePdf: (requestId) => api.get(`/requests/${requestId}/invoice/preview`, { responseType: 'blob' }),
  previewSampleInvoice: () => api.get('/requests/invoice/sample-preview', { responseType: 'blob' }),
};

// Forms API
export const formsAPI = {
  list: (params) => api.get('/forms', { params }),
  listCompanyForms: (params) => api.get('/forms/company', { params }),
  listDefaultForms: (params) => api.get('/forms/defaults', { params }),
  get: (id) => api.get(`/forms/${id}`),
  create: (data) => api.post('/forms/company', data),  // Use company endpoint for admin
  createSystem: (data) => api.post('/forms', data),  // Super admin only - system forms
  update: (id, data) => api.patch(`/forms/${id}`, data),
  updateStatus: (id, status) => api.patch(`/forms/${id}/status`, { status }),
  delete: (id) => api.delete(`/forms/${id}`),
  clone: (id, data) => api.post(`/forms/${id}/clone`, data),
  addQuestion: (formId, data) => api.post(`/forms/${formId}/questions`, data),
  updateQuestion: (questionId, data) => api.patch(`/forms/questions/${questionId}`, data),
  deleteQuestion: (questionId) => api.delete(`/forms/questions/${questionId}`),
  reorderQuestions: (formId, orders) => api.post(`/forms/${formId}/reorder`, { question_orders: orders }),
  submit: (formId, responses, serviceRequestId, { partial = false } = {}) =>
    api.post(`/forms/${formId}/submit`, { responses, service_request_id: serviceRequestId, partial }),
  getResponses: (formId, params) => api.get(`/forms/${formId}/responses`, { params }),
  updateResponse: (responseId, responses, responsesDict) => api.patch(`/forms/responses/${responseId}`, { responses, responses_dict: responsesDict }),
};

// Notifications API
export const notificationsAPI = {
  list: (params) => api.get('/notifications', { params }),
  getUnreadCount: () => api.get('/notifications/unread-count'),
  markRead: (id) => api.patch(`/notifications/${id}/read`),
  markAllRead: () => api.post('/notifications/mark-all-read'),
  // Email Templates
  getEmailTemplates: (params) => api.get('/notifications/email-templates', { params }),
  getEmailTemplate: (id) => api.get(`/notifications/email-templates/${id}`),
  createEmailTemplate: (data) => api.post('/notifications/email-templates', data),
  updateEmailTemplate: (id, data) => api.patch(`/notifications/email-templates/${id}`, data),
  deleteEmailTemplate: (id) => api.delete(`/notifications/email-templates/${id}`),
  previewEmailTemplate: (id, context) => api.post(`/notifications/email-templates/${id}/preview`, { context }),
  // Bulk Email
  sendBulkEmail: (data) => api.post('/notifications/bulk-email', data),
};

// Companies API
export const companiesAPI = {
  create: (data) => api.post('/companies', data),
  list: (params) => api.get('/companies', { params }),
  get: (id) => api.get(`/companies/${id}`),
  update: (id, data) => api.put(`/companies/${id}`, data),
  delete: (id) => api.delete(`/companies/${id}`),
  getUsers: (id, params) => api.get(`/companies/${id}/users`, { params }),
  addUser: (id, data) => api.post(`/companies/${id}/users`, data),
  transferOwnership: (id, newOwnerId) => api.post(`/companies/${id}/transfer-ownership`, { new_owner_id: newOwnerId }),
  getMyCompany: () => api.get('/companies/my-company'),
  updateInvoiceSettings: (id, data) => api.put(`/companies/${id}`, data),
  uploadLogo: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/companies/my-company/logo', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  deleteLogo: () => api.delete('/companies/my-company/logo'),
  // Super admin logo management for specific companies
  uploadLogoForCompany: (companyId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/companies/${companyId}/logo`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  deleteLogoForCompany: (companyId) => api.delete(`/companies/${companyId}/logo`),
  // Currency and tax settings
  getCurrencies: () => api.get('/companies/currencies'),
  getTaxTypes: () => api.get('/companies/tax-types'),
  updateCurrencySettings: (id, data) => api.put(`/companies/${id}/currency-settings`, data),
  // Super admin - manage currencies
  createCurrency: (data) => api.post('/companies/currencies', data),
  updateCurrency: (id, data) => api.put(`/companies/currencies/${id}`, data),
  deleteCurrency: (id) => api.delete(`/companies/currencies/${id}`),
  // Super admin - manage tax types
  createTaxType: (data) => api.post('/companies/tax-types', data),
  updateTaxType: (id, data) => api.put(`/companies/tax-types/${id}`, data),
  deleteTaxType: (id) => api.delete(`/companies/tax-types/${id}`),
  // Company contacts
  getCompanyContacts: (companyId, params) => api.get(`/companies/${companyId}/contacts`, { params }),
  addCompanyContact: (companyId, data) => api.post(`/companies/${companyId}/contacts`, data),
  updateCompanyContact: (companyId, contactId, data) => api.put(`/companies/${companyId}/contacts/${contactId}`, data),
  deleteCompanyContact: (companyId, contactId) => api.delete(`/companies/${companyId}/contacts/${contactId}`),
  getCompanyContactHistory: (companyId) => api.get(`/companies/${companyId}/contacts/history`),
  setCompanyPrimaryContact: (companyId, contactId) => api.put(`/companies/${companyId}/contacts/${contactId}/set-primary`),

  // Company email configuration (SMTP)
  getCompanyEmailConfig: (companyId) => api.get(`/companies/${companyId}/email-config`),
  updateCompanyEmailConfig: (companyId, data) => api.put(`/companies/${companyId}/email-config`, data),
  testCompanyEmailConfig: (companyId) => api.post(`/companies/${companyId}/email-config/test`),
  sendTestEmail: (companyId, data) => api.post(`/companies/${companyId}/email-config/send-test`, data),

  // Company storage configuration (SharePoint/Zoho)
  getCompanyStorageConfig: (companyId) => api.get(`/companies/${companyId}/storage-config`),
  updateCompanyStorageConfig: (companyId, data) => api.put(`/companies/${companyId}/storage-config`, data),
  testCompanyStorageConfig: (companyId) => api.post(`/companies/${companyId}/storage-config/test`),
  getZohoAuthUrl: (companyId) => api.get(`/companies/${companyId}/storage-config/zoho/auth-url`),
  connectZohoDrive: (companyId, data) => api.post(`/companies/${companyId}/storage-config/zoho/callback`, data),
  getGoogleAuthUrl: (companyId) => api.get(`/companies/${companyId}/storage-config/google/auth-url`),
  connectGoogleDrive: (companyId, data) => api.post(`/companies/${companyId}/storage-config/google/callback`, data),
  disconnectGoogleDrive: (companyId) => api.post(`/companies/${companyId}/storage-config/google/disconnect`),

  // System email configuration (Super Admin)
  getSystemEmailConfig: () => api.get('/companies/system/email-config'),
  updateSystemEmailConfig: (data) => api.put('/companies/system/email-config', data),
  testSystemEmailConfig: () => api.post('/companies/system/email-config/test'),
  sendSystemTestEmail: (data) => api.post('/companies/system/email-config/send-test', data),
};

// Client Entities API (Client organizations: companies, trusts, SMSFs, etc.)
export const clientEntitiesAPI = {
  // List entities for current company (admin/accountant only)
  list: (params) => api.get('/client-entities', { params }),

  // Get entities where current user is a contact (for regular users)
  getMyEntities: () => api.get('/client-entities/my-entities'),

  // Get a specific entity
  get: (id) => api.get(`/client-entities/${id}`),

  // Create a new entity
  create: (data) => api.post('/client-entities', data),

  // Update an entity
  update: (id, data) => api.patch(`/client-entities/${id}`, data),

  // Delete (soft) an entity
  delete: (id) => api.delete(`/client-entities/${id}`),

  // Search entities by name or ABN
  search: (query) => api.get('/client-entities/search', { params: { q: query } }),

  // Get entity contacts
  getContacts: (entityId) => api.get(`/client-entities/${entityId}/contacts`),

  // Add a contact to an entity
  addContact: (entityId, data) => api.post(`/client-entities/${entityId}/contacts`, data),

  // Update a contact
  updateContact: (entityId, contactId, data) => api.patch(`/client-entities/${entityId}/contacts/${contactId}`, data),

  // End a contact (set effective_to date)
  endContact: (entityId, contactId, effectiveTo) =>
    api.patch(`/client-entities/${entityId}/contacts/${contactId}`, { effective_to: effectiveTo }),

  // Get entity service requests
  getRequests: (entityId, params) => api.get(`/client-entities/${entityId}/requests`, { params }),
};

// Status API (Kanban board status columns)
export const statusAPI = {
  // Get statuses for current company (custom or system defaults)
  list: (includeInactive = false, category = null) => {
    const params = { include_inactive: includeInactive };
    if (category) params.category = category;
    return api.get('/statuses', { params });
  },

  // Get system default statuses
  getSystemDefaults: () => api.get('/statuses/system'),

  // Initialize custom statuses by copying from system defaults
  initialize: () => api.post('/statuses/initialize'),

  // Create a new custom status
  create: (data) => api.post('/statuses', data),

  // Update a custom status
  update: (id, data) => api.patch(`/statuses/${id}`, data),

  // Delete a custom status
  delete: (id) => api.delete(`/statuses/${id}`),

  // Reorder statuses
  reorder: (statusIds) => api.post('/statuses/reorder', { status_ids: statusIds }),

  // Reset to system defaults
  reset: () => api.post('/statuses/reset'),

  // Lookup a specific status by key
  lookup: (statusKey) => api.get(`/statuses/lookup/${statusKey}`),

  // Transition endpoints
  getTransitions: () => api.get('/statuses/transitions'),
  getAllowedTransitions: (fromStatus) => api.get('/statuses/transitions/allowed', { params: { from_status: fromStatus } }),
  createTransition: (data) => api.post('/statuses/transitions', data),
  updateTransition: (id, data) => api.patch(`/statuses/transitions/${id}`, data),
  deleteTransition: (id) => api.delete(`/statuses/transitions/${id}`),
};

// Documents API (Azure Blob Storage)
export const documentsAPI = {
  upload: (file, serviceRequestId, category, description) => {
    const formData = new FormData();
    formData.append('file', file);
    if (serviceRequestId) formData.append('service_request_id', serviceRequestId);
    if (category) formData.append('category', category);
    if (description) formData.append('description', description);
    return api.post('/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: (params) => api.get('/documents', { params }),
  get: (id) => api.get(`/documents/${id}`),
  getDownloadUrl: (id) => api.get(`/documents/${id}/download`),
  getViewUrl: (id) => api.get(`/documents/${id}/view`),
  getProxyUrl: (id) => `${API_BASE_URL}/documents/${id}/proxy`,
  createShareLink: (id) => api.post(`/documents/${id}/share`),
  delete: (id) => api.delete(`/documents/${id}`),
  getCategories: () => api.get('/documents/categories'),
};

// Tags API
export const tagsAPI = {
  list: (params) => api.get('/tags', { params }),
  create: (data) => api.post('/tags', data),
  update: (id, data) => api.patch(`/tags/${id}`, data),
  delete: (id) => api.delete(`/tags/${id}`),
  getUserTags: (userId) => api.get(`/tags/users/${userId}/tags`),
  assignTag: (userId, tagId) => api.post(`/tags/users/${userId}/tags`, { tag_id: tagId }),
  removeTag: (userId, tagId) => api.delete(`/tags/users/${userId}/tags/${tagId}`),
};

// Search API
export const searchAPI = {
  global: (query, type, limit) => api.get('/search', { params: { q: query, type, limit } }),
  users: (params) => api.get('/search/users', { params }),
  requests: (params) => api.get('/search/requests', { params }),
};

// Analytics API
export const analyticsAPI = {
  getDashboard: (params) => api.get('/analytics/dashboard', { params }),
  getBottlenecks: (params) => api.get('/analytics/bottlenecks', { params }),
  getWorkload: (params) => api.get('/analytics/workload', { params }),
  getRevenueByClient: (params) => api.get('/analytics/revenue/by-client', { params }),
  getRevenueByService: (params) => api.get('/analytics/revenue/by-service', { params }),
  getLodgementSummary: (params) => api.get('/analytics/lodgement-summary', { params }),
  // Job state duration analytics
  getStateDurations: (params) => api.get('/requests/analytics/state-durations', { params }),
  getOverdueRequests: (params) => api.get('/requests/analytics/overdue', { params }),
  getDeadlineSummary: (params) => api.get('/requests/analytics/deadline-summary', { params }),
  getRequestStateHistory: (requestId) => api.get(`/requests/${requestId}/state-history`),
  // Revenue vs Cost analytics
  getRevenueCost: (params) => api.get('/requests/analytics/revenue-cost', { params }),
  // Admin dashboard analytics (client/user activity metrics)
  getAdminDashboard: (params) => api.get('/analytics/admin-dashboard', { params }),
};

// Activity API
export const activityAPI = {
  list: (params) => api.get('/activity', { params }),
  getEntityActivity: (entityType, entityId, limit) => api.get(`/activity/entity/${entityType}/${entityId}`, { params: { limit } }),
  getUserActivity: (userId, limit) => api.get(`/activity/users/${userId}`, { params: { limit } }),
  search: (params) => api.get('/activity/search', { params }),
};

// Workflows API
export const workflowsAPI = {
  // Workflow CRUD
  list: (params) => api.get('/workflows', { params }),
  get: (id) => api.get(`/workflows/${id}`),
  create: (data) => api.post('/workflows', data),
  update: (id, data) => api.put(`/workflows/${id}`, data),
  delete: (id) => api.delete(`/workflows/${id}`),
  duplicate: (id, data) => api.post(`/workflows/${id}/duplicate`, data),
  validate: (id) => api.get(`/workflows/${id}/validate`),

  // Steps
  addStep: (workflowId, data) => api.post(`/workflows/${workflowId}/steps`, data),
  updateStep: (workflowId, stepId, data) => api.put(`/workflows/${workflowId}/steps/${stepId}`, data),
  deleteStep: (workflowId, stepId) => api.delete(`/workflows/${workflowId}/steps/${stepId}`),

  // Transitions
  addTransition: (workflowId, data) => api.post(`/workflows/${workflowId}/transitions`, data),
  updateTransition: (workflowId, transitionId, data) => api.put(`/workflows/${workflowId}/transitions/${transitionId}`, data),
  deleteTransition: (workflowId, transitionId) => api.delete(`/workflows/${workflowId}/transitions/${transitionId}`),

  // Automations
  listAutomations: (workflowId) => api.get(`/workflows/${workflowId}/automations`),
  addAutomation: (workflowId, data) => api.post(`/workflows/${workflowId}/automations`, data),
  updateAutomation: (workflowId, automationId, data) => api.put(`/workflows/${workflowId}/automations/${automationId}`, data),
  deleteAutomation: (workflowId, automationId) => api.delete(`/workflows/${workflowId}/automations/${automationId}`),

  // Request workflow operations
  getRequestTransitions: (requestId) => api.get(`/workflows/requests/${requestId}/transitions`),
  executeTransition: (requestId, transitionId, data) => api.post(`/workflows/requests/${requestId}/transitions/${transitionId}`, data),
  getRequestWorkflow: (requestId) => api.get(`/workflows/requests/${requestId}/workflow`),
};

// Tasks API (Kanban task board for accountants)
export const tasksAPI = {
  // List tasks (accountants see only assigned, admins see all)
  list: (params) => api.get('/tasks', { params }),

  // Get a single task
  get: (id) => api.get(`/tasks/${id}`),

  // Create a new task
  create: (data) => api.post('/tasks', data),

  // Update a task
  update: (id, data) => api.patch(`/tasks/${id}`, data),

  // Delete a task (admin only)
  delete: (id) => api.delete(`/tasks/${id}`),

  // Quick status update (for Kanban drag-drop)
  updateStatus: (id, status) => api.patch(`/tasks/${id}/status`, { status }),
};

// Renewals API (Service renewal reminders)
export const renewalsAPI = {
  // List upcoming renewals
  list: (params) => api.get('/renewals', { params }),
  get: (id) => api.get(`/renewals/${id}`),

  // Create manual renewal
  create: (data) => api.post('/renewals/create', data),

  // Send manual reminder
  sendReminder: (id) => api.post(`/renewals/${id}/send-reminder`),

  // Mark renewal as completed
  markComplete: (id, requestId = null) => api.post(`/renewals/${id}/complete`, { request_id: requestId }),

  // Skip a renewal
  skip: (id, reason = null) => api.post(`/renewals/${id}/skip`, { reason }),

  // Get renewals for a specific user
  getUserRenewals: (userId) => api.get(`/renewals/user/${userId}`),

  // Get renewals for a specific service
  getServiceRenewals: (serviceId) => api.get(`/renewals/service/${serviceId}`),

  // Get renewal statistics
  getStats: (params) => api.get('/renewals/stats', { params }),

  // Trigger reminder processing (admin)
  processReminders: () => api.post('/renewals/process-reminders'),
};

// Leads API (Website form submissions)
export const leadsAPI = {
  getLeads: (params) => api.get('/leads/admin/leads', { params }),
  getLead: (id) => api.get(`/leads/admin/leads/${id}`),
  updateLead: (id, data) => api.patch(`/leads/admin/leads/${id}`, data),
  deleteLead: (id) => api.delete(`/leads/admin/leads/${id}`),
  exportLeads: () => api.get('/leads/admin/leads/export'),
  getStats: () => api.get('/leads/admin/stats'),
};

// Client Pricing API (Admin-only: client-specific pricing management)
export const clientPricingAPI = {
  // List all client pricing records (with optional filters)
  list: (params) => api.get('/client-pricing', { params }),

  // Get pricing for a specific user
  getForUser: (userId, params) => api.get(`/client-pricing/user/${userId}`, { params }),

  // Get pricing for a specific client entity
  getForEntity: (entityId, params) => api.get(`/client-pricing/entity/${entityId}`, { params }),

  // Get a specific pricing record
  get: (id) => api.get(`/client-pricing/${id}`),

  // Create a new client pricing record
  create: (data) => api.post('/client-pricing', data),

  // Update a pricing record
  update: (id, data) => api.patch(`/client-pricing/${id}`, data),

  // Delete a pricing record
  delete: (id) => api.delete(`/client-pricing/${id}`),

  // Get effective price for a service (considering client-specific pricing)
  getEffectivePrice: (serviceId, params) => api.get(`/client-pricing/effective-price/${serviceId}`, { params }),
};

// SMSF Basic Data Sheet API
export const smsfDataSheetAPI = {
  list:    (params) => api.get('/smsf-data-sheets', { params }),
  get:     (id)     => api.get(`/smsf-data-sheets/${id}`),
  create:  (data)   => api.post('/smsf-data-sheets', data),
  update:  (id, data) => api.put(`/smsf-data-sheets/${id}`, data),
  delete:  (id)     => api.delete(`/smsf-data-sheets/${id}`),
  getPdf:  (id)     => api.get(`/smsf-data-sheets/${id}/pdf`, { responseType: 'blob' }),
  preview: (id)     => api.get(`/smsf-data-sheets/${id}/preview-html`),
};

// Letters API (SMSF Engagement & Representation letter generation)
export const lettersAPI = {
  list: (params) => api.get('/letters', { params }),
  get: (id) => api.get(`/letters/${id}`),
  create: (data) => api.post('/letters', data),
  update: (id, data) => api.patch(`/letters/${id}`, data),
  delete: (id) => api.delete(`/letters/${id}`),
  // Generate and stream PDF (responseType blob)
  getPdf: (id, download = false) =>
    api.get(`/letters/${id}/pdf`, { responseType: 'blob', params: { download: download ? 1 : 0 } }),
  getSignedPdf: (id) =>
    api.get(`/letters/${id}/signed-pdf`, { responseType: 'blob' }),
  sign: (id, data) => api.patch(`/letters/${id}/sign`, data),
  uploadSigned: (id, formData) =>
    api.post(`/letters/${id}/upload-signed`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
};

// Blog API (public website articles)
export const blogAPI = {
  // Public
  list: (params) => api.get('/blogs', { params }),
  get: (slug) => api.get(`/blogs/${slug}`),
  // Admin
  adminList: () => api.get('/admin/blogs'),
  create: (data) => api.post('/admin/blogs', data),
  update: (id, data) => api.put(`/admin/blogs/${id}`, data),
  delete: (id) => api.delete(`/admin/blogs/${id}`),
};

// ATO Alerts API (public website regulatory notices)
export const atoAlertsAPI = {
  // Public
  list: () => api.get('/ato-alerts'),
  // Admin
  adminList: () => api.get('/admin/ato-alerts'),
  create: (data) => api.post('/admin/ato-alerts', data),
  update: (id, data) => api.put(`/admin/ato-alerts/${id}`, data),
  delete: (id) => api.delete(`/admin/ato-alerts/${id}`),
};

// Client Portal API (admin: invite; client: dashboard, start audit, pdf, upload)
export const clientPortalAPI = {
  // Admin
  invite: (data) => api.post('/client-portal/invite', data),
  listClients: (params) => api.get('/client-portal/clients', { params }),
  // Client
  myPortal: () => api.get('/client-portal/my-portal'),
  startAudit: (data) => api.post('/client-portal/start-audit', data),
  myPdf: (download = false) =>
    api.get('/client-portal/my-pdf', { responseType: 'blob', params: { download: download ? 1 : 0 } }),
  uploadSigned: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/client-portal/upload-signed', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export default api;
