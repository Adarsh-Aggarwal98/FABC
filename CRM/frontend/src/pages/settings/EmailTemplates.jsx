import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  DocumentDuplicateIcon,
  EyeIcon,
  XMarkIcon,
  FunnelIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { TextArea, Select } from '../../components/common/Input';
import { notificationsAPI, servicesAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

export default function EmailTemplates() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [templates, setTemplates] = useState([]);
  const [services, setServices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [previewData, setPreviewData] = useState({ subject: '', body_html: '' });
  const [isSaving, setIsSaving] = useState(false);

  // Filters
  const [filterType, setFilterType] = useState('');
  const [filterCategory, setFilterCategory] = useState('');
  const [filterService, setFilterService] = useState('');

  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    subject: '',
    body_html: '',
    variables: [],
    template_type: '',
    service_id: '',
    service_category: '',
  });

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'senior_accountant';
  const isSuperAdmin = user?.role === 'super_admin';

  useEffect(() => {
    if (!isAdmin) {
      navigate('/dashboard');
      return;
    }
    fetchTemplates();
    fetchServices();
  }, [isAdmin]);

  const fetchTemplates = async () => {
    setIsLoading(true);
    try {
      const response = await notificationsAPI.getEmailTemplates();
      setTemplates(response.data.templates || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch email templates');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchServices = async () => {
    try {
      const response = await servicesAPI.getAll();
      setServices(response.data.services || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch services');
    }
  };

  const handleCreate = () => {
    setEditingTemplate(null);
    setFormData({
      name: '',
      slug: '',
      subject: '',
      body_html: '',
      variables: [],
      template_type: '',
      service_id: '',
      service_category: '',
    });
    setShowModal(true);
  };

  const handleEdit = (template) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      slug: template.slug,
      subject: template.subject,
      body_html: template.body_html,
      variables: template.variables || [],
      template_type: template.template_type || '',
      service_id: template.service_id || '',
      service_category: template.service_category || '',
    });
    setShowModal(true);
  };

  const handleClone = (template) => {
    setEditingTemplate(null);
    setFormData({
      name: `${template.name} (Copy)`,
      slug: `${template.slug}_copy`,
      subject: template.subject,
      body_html: template.body_html,
      variables: template.variables || [],
      template_type: template.template_type || '',
      service_id: template.service_id || '',
      service_category: template.service_category || '',
    });
    setShowModal(true);
  };

  const handlePreview = async (template) => {
    try {
      // Create sample context for preview
      const sampleContext = {
        client_name: 'John Smith',
        client_email: 'john@example.com',
        company_name: user?.company?.name || 'Your Company',
        service_name: 'Individual Tax Return',
        amount: '$350.00',
        invoice_number: 'INV-001',
        due_date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toLocaleDateString(),
        payment_link: 'https://pay.example.com/invoice/123',
        portal_link: 'https://portal.example.com',
        accountant_name: 'Jane Accountant',
        bank_details: 'BSB: 012-345\nAccount: 123456789',
        payment_terms: 'Due within 14 days',
        invoice_notes: 'Thank you for your business!',
        invoice_footer: 'Questions? Contact us at support@example.com',
        document_list: '- Income statement\n- Bank statements\n- Receipts',
        query_message: 'Please provide your work from home expense calculation.',
        tax_year: '2024',
        due_year: '2024',
        completion_notes: 'Your tax return has been lodged with the ATO.',
        reset_link: 'https://portal.example.com/reset-password/abc123',
        renewal_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString(),
        days_until_due: '30',
      };

      const response = await notificationsAPI.previewEmailTemplate(template.id, sampleContext);
      setPreviewData({
        subject: response.data.subject,
        body_html: response.data.body_html,
      });
      setShowPreviewModal(true);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to preview template');
    }
  };

  const handleSave = async () => {
    if (!formData.name || !formData.slug || !formData.subject || !formData.body_html) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsSaving(true);
    try {
      const payload = {
        ...formData,
        service_id: formData.service_id || null,
        service_category: formData.service_category || null,
        template_type: formData.template_type || null,
      };

      if (editingTemplate) {
        await notificationsAPI.updateEmailTemplate(editingTemplate.id, payload);
        toast.success('Template updated successfully');
      } else {
        await notificationsAPI.createEmailTemplate(payload);
        toast.success('Template created successfully');
      }
      setShowModal(false);
      fetchTemplates();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save template');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (template) => {
    if (template.is_system && !isSuperAdmin) {
      toast.error('Cannot delete system templates');
      return;
    }

    if (!window.confirm(`Are you sure you want to delete "${template.name}"?`)) {
      return;
    }

    try {
      await notificationsAPI.deleteEmailTemplate(template.id);
      toast.success('Template deleted successfully');
      fetchTemplates();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete template');
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Extract variables from template body
  const extractVariables = (text) => {
    const matches = text.match(/\{([^}]+)\}/g) || [];
    return [...new Set(matches.map((m) => m.slice(1, -1)))];
  };

  const handleBodyChange = (value) => {
    setFormData((prev) => ({
      ...prev,
      body_html: value,
      variables: extractVariables(value + ' ' + prev.subject),
    }));
  };

  const handleSubjectChange = (value) => {
    setFormData((prev) => ({
      ...prev,
      subject: value,
      variables: extractVariables(prev.body_html + ' ' + value),
    }));
  };

  const clearFilters = () => {
    setFilterType('');
    setFilterCategory('');
    setFilterService('');
  };

  const templateTypes = [
    { value: 'welcome', label: 'Welcome' },
    { value: 'invoice', label: 'Invoice' },
    { value: 'payment_reminder', label: 'Payment Reminder' },
    { value: 'document_request', label: 'Document Request' },
    { value: 'service_completed', label: 'Service Completed' },
    { value: 'query_raised', label: 'Query Raised' },
    { value: 'renewal_reminder', label: 'Renewal Reminder' },
    { value: 'annual_reminder', label: 'Annual Reminder' },
    { value: 'password_reset', label: 'Password Reset' },
  ];

  const serviceCategories = [
    { value: 'tax_agent', label: 'Tax Agent Services' },
    { value: 'bas_agent', label: 'BAS Agent Services' },
    { value: 'auditor', label: 'Auditor Services' },
    { value: 'bookkeeper', label: 'Bookkeeping Services' },
    { value: 'financial_planner', label: 'Financial Planning' },
    { value: 'mortgage_broker', label: 'Mortgage Broker' },
  ];

  const templateCategories = {
    welcome: { label: 'Welcome', color: 'bg-green-100 text-green-800' },
    invoice: { label: 'Invoice', color: 'bg-blue-100 text-blue-800' },
    payment_reminder: { label: 'Payment', color: 'bg-yellow-100 text-yellow-800' },
    document_request: { label: 'Documents', color: 'bg-purple-100 text-purple-800' },
    service_completed: { label: 'Completed', color: 'bg-teal-100 text-teal-800' },
    query_raised: { label: 'Query', color: 'bg-orange-100 text-orange-800' },
    renewal_reminder: { label: 'Renewal', color: 'bg-indigo-100 text-indigo-800' },
    annual_reminder: { label: 'Reminder', color: 'bg-pink-100 text-pink-800' },
    password_reset: { label: 'Security', color: 'bg-red-100 text-red-800' },
  };

  const categoryColors = {
    tax_agent: 'bg-blue-50 text-blue-700 border-blue-200',
    bas_agent: 'bg-green-50 text-green-700 border-green-200',
    auditor: 'bg-purple-50 text-purple-700 border-purple-200',
    bookkeeper: 'bg-yellow-50 text-yellow-700 border-yellow-200',
    financial_planner: 'bg-pink-50 text-pink-700 border-pink-200',
    mortgage_broker: 'bg-cyan-50 text-cyan-700 border-cyan-200',
  };

  // Filter templates
  const filteredTemplates = templates.filter((template) => {
    if (filterType && template.template_type !== filterType && template.slug !== filterType) {
      return false;
    }
    if (filterCategory && template.service_category !== filterCategory) {
      return false;
    }
    if (filterService && template.service_id !== parseInt(filterService)) {
      return false;
    }
    return true;
  });

  // Group templates by category for better organization
  const groupedTemplates = filteredTemplates.reduce((acc, template) => {
    const category = template.service_category || 'general';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(template);
    return acc;
  }, {});

  const hasActiveFilters = filterType || filterCategory || filterService;

  if (isLoading) {
    return (
      <DashboardLayout title="Email Templates">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Email Templates">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            icon={ArrowLeftIcon}
            onClick={() => navigate('/dashboard')}
          >
            Back to Dashboard
          </Button>
          <Button icon={PlusIcon} onClick={handleCreate}>
            New Template
          </Button>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-medium text-blue-800 mb-2">About Email Templates</h3>
          <p className="text-sm text-blue-700">
            Customize the emails sent to your clients. Templates can be associated with specific services
            or service categories for automatic renewal reminders. Use variables like{' '}
            <code className="bg-blue-100 px-1 rounded">{'{client_name}'}</code> to personalize emails.
          </p>
        </div>

        {/* Filters */}
        <Card>
          <div className="flex flex-wrap items-end gap-4">
            <div className="flex items-center gap-2 text-gray-500">
              <FunnelIcon className="w-5 h-5" />
              <span className="text-sm font-medium">Filters:</span>
            </div>

            <div className="flex-1 min-w-[150px] max-w-[200px]">
              <label className="block text-xs text-gray-500 mb-1">Template Type</label>
              <select
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
              >
                <option value="">All Types</option>
                {templateTypes.map((type) => (
                  <option key={type.value} value={type.value}>
                    {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1 min-w-[150px] max-w-[200px]">
              <label className="block text-xs text-gray-500 mb-1">Service Category</label>
              <select
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filterCategory}
                onChange={(e) => setFilterCategory(e.target.value)}
              >
                <option value="">All Categories</option>
                {serviceCategories.map((cat) => (
                  <option key={cat.value} value={cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex-1 min-w-[150px] max-w-[200px]">
              <label className="block text-xs text-gray-500 mb-1">Specific Service</label>
              <select
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                value={filterService}
                onChange={(e) => setFilterService(e.target.value)}
              >
                <option value="">All Services</option>
                {services.map((service) => (
                  <option key={service.id} value={service.id}>
                    {service.name}
                  </option>
                ))}
              </select>
            </div>

            {hasActiveFilters && (
              <Button
                variant="ghost"
                size="sm"
                icon={ArrowPathIcon}
                onClick={clearFilters}
              >
                Clear
              </Button>
            )}
          </div>

          {hasActiveFilters && (
            <div className="mt-3 pt-3 border-t">
              <p className="text-sm text-gray-600">
                Showing <span className="font-medium">{filteredTemplates.length}</span> of{' '}
                <span className="font-medium">{templates.length}</span> templates
              </p>
            </div>
          )}
        </Card>

        {/* Templates Grid - Grouped by Category */}
        {Object.entries(groupedTemplates).map(([category, categoryTemplates]) => (
          <div key={category} className="space-y-3">
            <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide flex items-center gap-2">
              {category === 'general' ? 'General Templates' : (
                <>
                  <span className={`px-2 py-0.5 rounded text-xs border ${categoryColors[category] || 'bg-gray-50 text-gray-700 border-gray-200'}`}>
                    {serviceCategories.find(c => c.value === category)?.label || category}
                  </span>
                  <span className="text-gray-400 font-normal">({categoryTemplates.length})</span>
                </>
              )}
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categoryTemplates.map((template) => (
                <Card key={template.id} className="relative">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">{template.name}</h3>
                      <p className="text-xs text-gray-500 font-mono mt-1">{template.slug}</p>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0 ml-2">
                      {template.is_system && (
                        <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                          System
                        </span>
                      )}
                      {(template.template_type && templateCategories[template.template_type]) && (
                        <span className={`px-2 py-0.5 text-xs rounded ${templateCategories[template.template_type].color}`}>
                          {templateCategories[template.template_type].label}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Service Association */}
                  {template.service_id && (
                    <div className="mb-2">
                      <span className="px-2 py-1 text-xs bg-primary-50 text-primary-700 rounded-full border border-primary-200">
                        {services.find(s => s.id === template.service_id)?.name || `Service #${template.service_id}`}
                      </span>
                    </div>
                  )}

                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    <strong>Subject:</strong> {template.subject}
                  </p>

                  {template.variables?.length > 0 && (
                    <div className="mb-3">
                      <p className="text-xs text-gray-500 mb-1">Variables:</p>
                      <div className="flex flex-wrap gap-1">
                        {template.variables.slice(0, 5).map((v) => (
                          <span key={v} className="px-1.5 py-0.5 text-xs bg-gray-100 rounded">
                            {v}
                          </span>
                        ))}
                        {template.variables.length > 5 && (
                          <span className="px-1.5 py-0.5 text-xs bg-gray-100 rounded">
                            +{template.variables.length - 5} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center gap-2 pt-3 border-t">
                    <Button
                      size="sm"
                      variant="ghost"
                      icon={EyeIcon}
                      onClick={() => handlePreview(template)}
                    >
                      Preview
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      icon={DocumentDuplicateIcon}
                      onClick={() => handleClone(template)}
                    >
                      Clone
                    </Button>
                    {(!template.is_system || isSuperAdmin) && (
                      <>
                        <Button
                          size="sm"
                          variant="ghost"
                          icon={PencilIcon}
                          onClick={() => handleEdit(template)}
                        >
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          icon={TrashIcon}
                          className="text-red-600 hover:text-red-700"
                          onClick={() => handleDelete(template)}
                        >
                          Delete
                        </Button>
                      </>
                    )}
                  </div>
                </Card>
              ))}
            </div>
          </div>
        ))}

        {filteredTemplates.length === 0 && (
          <Card className="text-center py-8">
            <p className="text-gray-500">
              {hasActiveFilters
                ? 'No templates match your filters.'
                : 'No email templates found.'}
            </p>
            {hasActiveFilters ? (
              <Button className="mt-4" variant="secondary" onClick={clearFilters}>
                Clear Filters
              </Button>
            ) : (
              <Button className="mt-4" icon={PlusIcon} onClick={handleCreate}>
                Create Your First Template
              </Button>
            )}
          </Card>
        )}
      </div>

      {/* Edit/Create Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50" onClick={() => setShowModal(false)} />
            <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold">
                  {editingTemplate ? 'Edit Template' : 'Create Template'}
                </h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-full"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>

              <div className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Template Name"
                    value={formData.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    placeholder="e.g., Welcome Email"
                    required
                  />
                  <Input
                    label="Slug (unique identifier)"
                    value={formData.slug}
                    onChange={(e) => handleChange('slug', e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, '_'))}
                    placeholder="e.g., welcome_email"
                    required
                    disabled={editingTemplate?.is_system}
                  />
                </div>

                {/* Service Association */}
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Template Type
                    </label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      value={formData.template_type}
                      onChange={(e) => handleChange('template_type', e.target.value)}
                    >
                      <option value="">Select Type</option>
                      {templateTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Service Category
                    </label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      value={formData.service_category}
                      onChange={(e) => handleChange('service_category', e.target.value)}
                    >
                      <option value="">None (General)</option>
                      {serviceCategories.map((cat) => (
                        <option key={cat.value} value={cat.value}>
                          {cat.label}
                        </option>
                      ))}
                    </select>
                    <p className="text-xs text-gray-500 mt-1">
                      Used for category-wide renewal reminders
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Specific Service
                    </label>
                    <select
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                      value={formData.service_id}
                      onChange={(e) => handleChange('service_id', e.target.value)}
                    >
                      <option value="">None</option>
                      {services.map((service) => (
                        <option key={service.id} value={service.id}>
                          {service.name}
                        </option>
                      ))}
                    </select>
                    <p className="text-xs text-gray-500 mt-1">
                      Used for service-specific reminders
                    </p>
                  </div>
                </div>

                <Input
                  label="Email Subject"
                  value={formData.subject}
                  onChange={(e) => handleSubjectChange(e.target.value)}
                  placeholder="e.g., Welcome to {company_name}!"
                  required
                />

                <TextArea
                  label="Email Body (HTML)"
                  value={formData.body_html}
                  onChange={(e) => handleBodyChange(e.target.value)}
                  rows={15}
                  placeholder="<p>Dear {client_name},</p>..."
                  required
                  className="font-mono text-sm"
                />

                {formData.variables.length > 0 && (
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm font-medium text-gray-700 mb-2">Detected Variables:</p>
                    <div className="flex flex-wrap gap-2">
                      {formData.variables.map((v) => (
                        <span key={v} className="px-2 py-1 text-sm bg-white border rounded">
                          {'{' + v + '}'}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="font-medium text-blue-800 mb-2">Common Variables:</p>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm text-blue-700">
                    <div><code>{'{client_name}'}</code> - Client's name</div>
                    <div><code>{'{client_email}'}</code> - Client's email</div>
                    <div><code>{'{company_name}'}</code> - Your company</div>
                    <div><code>{'{service_name}'}</code> - Service name</div>
                    <div><code>{'{amount}'}</code> - Invoice amount</div>
                    <div><code>{'{invoice_number}'}</code> - Invoice #</div>
                    <div><code>{'{due_date}'}</code> - Due date</div>
                    <div><code>{'{renewal_date}'}</code> - Renewal date</div>
                    <div><code>{'{days_until_due}'}</code> - Days until due</div>
                    <div><code>{'{payment_link}'}</code> - Payment URL</div>
                    <div><code>{'{portal_link}'}</code> - Portal URL</div>
                    <div><code>{'{accountant_name}'}</code> - Accountant</div>
                  </div>
                </div>
              </div>

              <div className="sticky bottom-0 bg-gray-50 border-t px-6 py-4 flex justify-end gap-3">
                <Button variant="secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </Button>
                <Button onClick={handleSave} loading={isSaving}>
                  {editingTemplate ? 'Save Changes' : 'Create Template'}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {showPreviewModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <div className="fixed inset-0 bg-black/50" onClick={() => setShowPreviewModal(false)} />
            <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
                <h2 className="text-lg font-semibold">Email Preview</h2>
                <button
                  onClick={() => setShowPreviewModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-full"
                >
                  <XMarkIcon className="w-5 h-5" />
                </button>
              </div>

              <div className="p-6">
                <div className="bg-gray-50 rounded-lg p-4 mb-4">
                  <p className="text-sm text-gray-500 mb-1">Subject:</p>
                  <p className="font-medium">{previewData.subject}</p>
                </div>

                <div className="bg-white border rounded-lg p-6">
                  <div
                    className="prose prose-sm max-w-none"
                    dangerouslySetInnerHTML={{ __html: previewData.body_html }}
                  />
                </div>

                <p className="text-xs text-gray-500 mt-4 text-center">
                  This is a preview with sample data. Actual emails will use real client information.
                </p>
              </div>

              <div className="sticky bottom-0 bg-gray-50 border-t px-6 py-4 flex justify-end">
                <Button variant="secondary" onClick={() => setShowPreviewModal(false)}>
                  Close
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
