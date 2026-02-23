import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  CheckIcon,
  PencilSquareIcon,
  DocumentTextIcon,
  LinkIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import Badge from '../../components/common/Badge';
import Input, { TextArea, Select, Checkbox } from '../../components/common/Input';
import { servicesAPI, requestsAPI, formsAPI, workflowsAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import useCompanyStore from '../../store/companyStore';
import FormRenderer from '../../components/features/forms/FormRenderer';

export default function ServiceList() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { fetchCompany, formatPrice, getTaxLabel, getCurrencySettings } = useCompanyStore();
  const [services, setServices] = useState([]);
  const [forms, setForms] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [selectedServices, setSelectedServices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [currentForm, setCurrentForm] = useState(null);
  const [formResponses, setFormResponses] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingService, setEditingService] = useState(null);

  const isSuperAdmin = user?.role === 'super_admin';
  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'senior_accountant';
  const isUser = user?.role === 'user';

  // Get currency settings
  const currencySettings = getCurrencySettings();
  const taxLabel = getTaxLabel();

  // Service form data
  const [serviceData, setServiceData] = useState({
    name: '',
    description: '',
    category: '',
    base_price: '',
    form_id: '',
    workflow_id: '',
    is_active: true,
    cost_percentage: '',
    cost_category: '',
  });

  useEffect(() => {
    fetchServices();
    fetchCompany(); // Fetch company currency settings
    if (isAdmin) {
      fetchForms();
      fetchWorkflows();
    }
  }, []);

  const fetchServices = async () => {
    setIsLoading(true);
    try {
      const response = await servicesAPI.list({ active_only: !isAdmin });
      const allServices = response.data.data.services || [];

      // For services with form_id but missing/empty form questions, fetch form data
      const enriched = await Promise.all(
        allServices.map(async (service) => {
          if (service.form_id && (!service.form || !service.form.questions || service.form.questions.length === 0)) {
            try {
              const formRes = await formsAPI.get(service.form_id);
              const formData = formRes.data.data?.form || formRes.data.form || formRes.data;
              return { ...service, form: formData };
            } catch {
              return service;
            }
          }
          return service;
        })
      );

      setServices(enriched);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch services');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchForms = async () => {
    try {
      // Use company forms endpoint for admin, system forms for super_admin
      const response = isSuperAdmin
        ? await formsAPI.list()
        : await formsAPI.listCompanyForms();
      setForms(response.data.data.forms || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch forms');
    }
  };

  const fetchWorkflows = async () => {
    try {
      const response = await workflowsAPI.list();
      setWorkflows(response.data.data.workflows || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch workflows');
    }
  };

  const toggleServiceSelection = (serviceId) => {
    setSelectedServices((prev) =>
      prev.includes(serviceId)
        ? prev.filter((id) => id !== serviceId)
        : [...prev, serviceId]
    );
  };

  const handleRequestServices = async () => {
    if (selectedServices.length === 0) {
      toast.error('Please select at least one service');
      return;
    }

    const serviceWithForm = services.find(
      (s) => selectedServices.includes(s.id) && s.form_id
    );

    if (serviceWithForm && serviceWithForm.form) {
      setCurrentForm(serviceWithForm.form);
      setIsFormModalOpen(true);
      return;
    }

    await submitRequests();
  };

  const submitRequests = async () => {
    setIsSubmitting(true);
    try {
      await requestsAPI.create(selectedServices);
      toast.success('Service request(s) submitted successfully!');
      setSelectedServices([]);
      navigate('/requests');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to submit request');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFormSubmit = async () => {
    setIsSubmitting(true);
    try {
      const response = await requestsAPI.create(selectedServices);
      const createdRequests = response.data.data.requests || [response.data.data.request];

      for (const request of createdRequests) {
        const service = services.find((s) => s.id === request.service?.id);
        if (service?.form_id) {
          await formsAPI.submit(service.form_id, formResponses, request.id);
        }
      }

      toast.success('Service request(s) submitted successfully!');
      setSelectedServices([]);
      setFormResponses({});
      setIsFormModalOpen(false);
      navigate('/requests');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to submit request');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateService = async (e) => {
    e.preventDefault();
    try {
      const parsedCost = serviceData.cost_percentage !== '' && serviceData.cost_percentage !== null
        ? parseFloat(serviceData.cost_percentage)
        : null;
      const data = {
        ...serviceData,
        form_id: serviceData.form_id || null,
        workflow_id: serviceData.workflow_id || null,
        base_price: serviceData.base_price ? parseFloat(serviceData.base_price) : null,
        cost_percentage: parsedCost !== null && !isNaN(parsedCost) ? parsedCost : null,
        cost_category: serviceData.cost_category || null,
      };
      await servicesAPI.create(data);
      toast.success('Service created successfully');
      setIsCreateModalOpen(false);
      resetServiceForm();
      fetchServices();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create service');
    }
  };

  const handleEditService = (service) => {
    setEditingService(service);
    setServiceData({
      name: service.name,
      description: service.description || '',
      category: service.category || '',
      base_price: service.base_price || '',
      form_id: service.form_id || '',
      workflow_id: service.workflow_id || '',
      is_active: service.is_active !== false,
      cost_percentage: service.cost_percentage || '',
      cost_category: service.cost_category || '',
    });
    setIsEditModalOpen(true);
  };

  const handleUpdateService = async (e) => {
    e.preventDefault();
    try {
      const parsedCost = serviceData.cost_percentage !== '' && serviceData.cost_percentage !== null
        ? parseFloat(serviceData.cost_percentage)
        : null;
      const data = {
        ...serviceData,
        form_id: serviceData.form_id || null,
        workflow_id: serviceData.workflow_id || null,
        base_price: serviceData.base_price ? parseFloat(serviceData.base_price) : null,
        cost_percentage: parsedCost !== null && !isNaN(parsedCost) ? parsedCost : null,
        cost_category: serviceData.cost_category || null,
      };
      await servicesAPI.update(editingService.id, data);
      toast.success('Service updated successfully');
      setIsEditModalOpen(false);
      resetServiceForm();
      fetchServices();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update service');
    }
  };

  const resetServiceForm = () => {
    setServiceData({
      name: '',
      description: '',
      category: '',
      base_price: '',
      form_id: '',
      workflow_id: '',
      is_active: true,
      cost_percentage: '',
      cost_category: '',
    });
    setEditingService(null);
  };

  // Render Admin View with table
  const renderAdminView = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-900">Manage Services</h2>
        <Button icon={PlusIcon} onClick={() => setIsCreateModalOpen(true)}>
          Add Service
        </Button>
      </div>

      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Service
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Category
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Price (excl. Tax)
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Form
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {services.map((service) => (
                <tr key={service.id} className="hover:bg-gray-50">
                  <td className="px-4 py-4">
                    <div>
                      <p className="font-medium text-gray-900">{service.name}</p>
                      <p className="text-sm text-gray-500 truncate max-w-xs">
                        {service.description}
                      </p>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-600">
                    {service.category || '-'}
                  </td>
                  <td className="px-4 py-4 text-sm text-gray-600">
                    {service.base_price ? formatPrice(service.base_price) : '-'}
                  </td>
                  <td className="px-4 py-4">
                    {service.form ? (
                      <div className="flex items-center gap-1 text-green-600">
                        <LinkIcon className="h-4 w-4" />
                        <span className="text-sm">{service.form.name}</span>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-400">No form</span>
                    )}
                  </td>
                  <td className="px-4 py-4">
                    <Badge status={service.is_active !== false ? 'completed' : 'pending'}>
                      {service.is_active !== false ? 'Active' : 'Inactive'}
                    </Badge>
                  </td>
                  <td className="px-4 py-4">
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={PencilSquareIcon}
                      onClick={() => handleEditService(service)}
                    >
                      Edit
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Link to Form Builder */}
      {isAdmin && (
        <Card className="bg-gradient-to-r from-primary-50 to-blue-50">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gray-900">Form Builder</h3>
              <p className="text-sm text-gray-600 mt-1">
                Create custom forms with questions and file upload options to attach to services
              </p>
            </div>
            <Button
              variant="secondary"
              icon={DocumentTextIcon}
              onClick={() => navigate('/forms')}
            >
              Manage Forms
            </Button>
          </div>
        </Card>
      )}
    </div>
  );

  // Render User View with cards
  const renderUserView = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {services
          .filter((s) => s.is_active !== false)
          .map((service) => (
            <Card
              key={service.id}
              className={`cursor-pointer transition-all ${
                selectedServices.includes(service.id)
                  ? 'ring-2 ring-primary-500 bg-primary-50'
                  : 'hover:shadow-md'
              }`}
              onClick={() => toggleServiceSelection(service.id)}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{service.name}</h3>
                  {service.category && (
                    <span className="text-xs text-gray-400">{service.category}</span>
                  )}
                  <p className="text-sm text-gray-500 mt-2">{service.description}</p>
                  {/* Prices are hidden from client users - they only see prices after invoice */}
                  {service.form && (
                    <p className="text-xs text-gray-400 mt-2">
                      * Additional information required
                    </p>
                  )}
                </div>
                {selectedServices.includes(service.id) && (
                  <div className="bg-primary-600 rounded-full p-1">
                    <CheckIcon className="h-4 w-4 text-white" />
                  </div>
                )}
              </div>
            </Card>
          ))}
      </div>

      {selectedServices.length > 0 && (
        <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2">
          <Button
            size="lg"
            onClick={handleRequestServices}
            loading={isSubmitting}
            className="shadow-lg"
          >
            Request {selectedServices.length} Service
            {selectedServices.length > 1 ? 's' : ''}
          </Button>
        </div>
      )}
    </div>
  );

  // Service Form Content - rendered inline to prevent focus loss
  const renderServiceForm = (isEdit) => (
    <form onSubmit={isEdit ? handleUpdateService : handleCreateService} className="space-y-4">
      <Input
        label="Service Name"
        value={serviceData.name}
        onChange={(e) => setServiceData((prev) => ({ ...prev, name: e.target.value }))}
        placeholder="Tax Return Filing"
        required
      />
      <TextArea
        label="Description"
        value={serviceData.description}
        onChange={(e) => setServiceData((prev) => ({ ...prev, description: e.target.value }))}
        placeholder="Describe the service..."
        rows={3}
      />
      <div className="grid grid-cols-2 gap-4">
        <Select
          label="Category"
          value={serviceData.category}
          onChange={(e) => setServiceData((prev) => ({ ...prev, category: e.target.value }))}
          options={[
            { value: '', label: 'Select category' },
            { value: 'Tax', label: 'Tax' },
            { value: 'Accounting', label: 'Accounting' },
            { value: 'Bookkeeping', label: 'Bookkeeping' },
            { value: 'Payroll', label: 'Payroll' },
            { value: 'Advisory', label: 'Advisory' },
            { value: 'Compliance', label: 'Compliance' },
            { value: 'Audit', label: 'Audit' },
            { value: 'Business Services', label: 'Business Services' },
            { value: 'SMSF', label: 'SMSF' },
            { value: 'Other', label: 'Other' },
          ]}
        />
        <Input
          label={`Base Price (${currencySettings.currency_symbol} excl. Tax)`}
          type="number"
          step="0.01"
          value={serviceData.base_price}
          onChange={(e) => setServiceData((prev) => ({ ...prev, base_price: e.target.value }))}
          placeholder="0.00"
          helper={`Price excluding tax. Tax will be added automatically on invoices.`}
        />
      </div>

      {/* Cost Tracking (Admin only) */}
      {isAdmin && (
        <div className="border-t pt-4 mt-4">
          <p className="text-sm font-medium text-gray-700 mb-3">Cost Tracking (for analytics)</p>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Default Cost %"
              type="number"
              step="0.1"
              min="0"
              max="100"
              value={serviceData.cost_percentage}
              onChange={(e) => setServiceData((prev) => ({ ...prev, cost_percentage: e.target.value }))}
              placeholder="0"
              helper="Estimated cost as percentage of revenue (e.g., 40 means 40% cost)"
            />
            <Input
              label="Cost Category"
              value={serviceData.cost_category}
              onChange={(e) => setServiceData((prev) => ({ ...prev, cost_category: e.target.value }))}
              placeholder="Labor, Software, etc."
              helper="For grouping in revenue vs cost reports"
            />
          </div>
        </div>
      )}

      {/* Form Selection */}
      {isAdmin && (
        <div className="border-t pt-4">
          <Select
            label="Attach Form (Optional)"
            options={[
              { value: '', label: 'No form attached' },
              ...forms.map((f) => ({ value: f.id, label: f.name })),
            ]}
            value={serviceData.form_id}
            onChange={(e) => setServiceData((prev) => ({ ...prev, form_id: e.target.value }))}
          />
          <p className="text-xs text-gray-500 mt-1">
            Users will be required to fill out this form when requesting this service.
            You can create forms in the Form Builder.
          </p>
          {!forms.length && (
            <Button
              variant="secondary"
              size="sm"
              className="mt-2"
              type="button"
              onClick={() => navigate('/forms/new')}
            >
              Create a Form
            </Button>
          )}
        </div>
      )}

      {/* Workflow Selection */}
      {isAdmin && (
        <div className="border-t pt-4">
          <Select
            label="Workflow (Optional)"
            options={[
              { value: '', label: 'Use default workflow' },
              ...workflows.map((w) => ({ value: w.id, label: `${w.name}${w.is_default ? ' (Default)' : ''}` })),
            ]}
            value={serviceData.workflow_id}
            onChange={(e) => setServiceData((prev) => ({ ...prev, workflow_id: e.target.value }))}
          />
          <p className="text-xs text-gray-500 mt-1">
            Custom workflow for this service. Leave empty to use the default workflow.
          </p>
          <Button
            variant="secondary"
            size="sm"
            className="mt-2"
            type="button"
            onClick={() => navigate('/settings/workflows')}
          >
            Manage Workflows
          </Button>
        </div>
      )}

      {isEdit && (
        <Checkbox
          label="Service is active"
          checked={serviceData.is_active}
          onChange={(e) => setServiceData((prev) => ({ ...prev, is_active: e.target.checked }))}
        />
      )}

      <div className="flex justify-end gap-2 pt-4">
        <Button
          variant="secondary"
          onClick={() => {
            isEdit ? setIsEditModalOpen(false) : setIsCreateModalOpen(false);
            resetServiceForm();
          }}
          type="button"
        >
          Cancel
        </Button>
        <Button type="submit">{isEdit ? 'Update' : 'Create'} Service</Button>
      </div>
    </form>
  );

  if (isLoading) {
    return (
      <DashboardLayout title="Services">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Services">
      {isAdmin ? renderAdminView() : renderUserView()}

      {/* Create Service Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          resetServiceForm();
        }}
        title="Add New Service"
        size="lg"
      >
        {renderServiceForm(false)}
      </Modal>

      {/* Edit Service Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => {
          setIsEditModalOpen(false);
          resetServiceForm();
        }}
        title="Edit Service"
        size="lg"
      >
        {renderServiceForm(true)}
      </Modal>

      {/* Form Modal for Users */}
      <Modal
        isOpen={isFormModalOpen}
        onClose={() => setIsFormModalOpen(false)}
        title={currentForm?.name || 'Additional Information'}
        size="lg"
      >
        {currentForm && (
          <div className="space-y-6">
            {currentForm.description && (
              <p className="text-gray-500">{currentForm.description}</p>
            )}
            <FormRenderer
              form={currentForm}
              responses={formResponses}
              onChange={setFormResponses}
            />
            <div className="flex justify-end gap-2 pt-4">
              <Button variant="secondary" onClick={() => setIsFormModalOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleFormSubmit} loading={isSubmitting}>
                Submit Request
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </DashboardLayout>
  );
}
