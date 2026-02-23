import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { PlusIcon, TrashIcon, DocumentTextIcon, DocumentDuplicateIcon } from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Modal from '../../components/common/Modal';
import Input from '../../components/common/Input';
import { formsAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

export default function FormList() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [forms, setForms] = useState([]);
  const [defaultForms, setDefaultForms] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCloneModalOpen, setIsCloneModalOpen] = useState(false);
  const [formToClone, setFormToClone] = useState(null);
  const [cloneName, setCloneName] = useState('');

  const isSuperAdmin = user?.role === 'super_admin';
  const isAdmin = user?.role === 'admin' || user?.role === 'senior_accountant';

  useEffect(() => {
    fetchForms();
    if (isAdmin) {
      fetchDefaultForms();
    }
  }, []);

  const fetchForms = async () => {
    setIsLoading(true);
    try {
      // Use company forms endpoint for admin, all forms for super_admin
      const response = isSuperAdmin
        ? await formsAPI.list({ active_only: false })
        : await formsAPI.listCompanyForms({ include_defaults: false });
      setForms(response.data.data.forms || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch forms');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDefaultForms = async () => {
    try {
      const response = await formsAPI.listDefaultForms({ include_questions: false });
      setDefaultForms(response.data.data.forms || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch default forms');
    }
  };

  const handleDelete = async (formId) => {
    if (!confirm('Are you sure you want to delete this form?')) return;

    try {
      await formsAPI.delete(formId);
      toast.success('Form deleted');
      fetchForms();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete form');
    }
  };

  const handleToggleActive = async (form) => {
    try {
      await formsAPI.update(form.id, { is_active: !form.is_active });
      toast.success(`Form ${form.is_active ? 'deactivated' : 'activated'}`);
      fetchForms();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update form');
    }
  };

  const handleCloneForm = async () => {
    if (!cloneName.trim()) {
      toast.error('Please enter a name for the cloned form');
      return;
    }
    try {
      await formsAPI.clone(formToClone.id, { name: cloneName });
      toast.success('Form cloned successfully');
      setIsCloneModalOpen(false);
      setFormToClone(null);
      setCloneName('');
      fetchForms();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to clone form');
    }
  };

  const openCloneModal = (form) => {
    setFormToClone(form);
    setCloneName(`${form.name} (Copy)`);
    setIsCloneModalOpen(true);
  };

  return (
    <DashboardLayout title="Forms">
      <div className="space-y-6">
        {/* Default Forms to Clone (for Practice Admin) */}
        {isAdmin && defaultForms.length > 0 && (
          <Card>
            <CardHeader
              title="Default Form Templates"
              subtitle="Clone these system forms to customize for your practice"
            />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {defaultForms.map((form) => (
                <div
                  key={form.id}
                  className="border border-blue-200 bg-blue-50 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="font-semibold text-gray-900">{form.name}</h3>
                      <span className="text-xs text-blue-600 capitalize">
                        System Template
                      </span>
                    </div>
                  </div>
                  {form.description && (
                    <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                      {form.description}
                    </p>
                  )}
                  <div className="text-xs text-gray-400 mb-3">
                    {form.question_count || 0} question(s)
                  </div>
                  <Button
                    variant="secondary"
                    size="sm"
                    icon={DocumentDuplicateIcon}
                    onClick={() => openCloneModal(form)}
                  >
                    Clone & Customize
                  </Button>
                </div>
              ))}
            </div>
          </Card>
        )}

        <Card>
          <CardHeader
            title={isAdmin ? "Your Practice Forms" : "Form Builder"}
            subtitle={isAdmin ? "Forms for your practice only - create new or clone from templates above" : "Create custom forms for services (like Google Forms)"}
            action={
              <Button icon={PlusIcon} onClick={() => navigate('/forms/new')}>
                Create Form
              </Button>
            }
          />

          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
            </div>
          ) : forms.length === 0 ? (
            <div className="text-center py-12">
              <DocumentTextIcon className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No forms created yet</p>
              <Button className="mt-4" onClick={() => navigate('/forms/new')}>
                Create your first form
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {forms.map((form) => (
                <div
                  key={form.id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-gray-900">{form.name}</h3>
                      <span className="text-xs text-gray-400 capitalize">
                        {form.form_type}
                      </span>
                    </div>
                    <Badge status={form.is_active ? 'active' : 'inactive'}>
                      {form.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>

                  {form.description && (
                    <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                      {form.description}
                    </p>
                  )}

                  <div className="text-xs text-gray-400 mb-4">
                    {form.questions?.length || 0} question(s)
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <div className="flex gap-2">
                      <Link to={`/forms/${form.id}`}>
                        <Button variant="secondary" size="sm">
                          Edit
                        </Button>
                      </Link>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleToggleActive(form)}
                      >
                        {form.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDelete(form.id)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* Clone Form Modal */}
      <Modal
        isOpen={isCloneModalOpen}
        onClose={() => {
          setIsCloneModalOpen(false);
          setFormToClone(null);
          setCloneName('');
        }}
        title="Clone Form"
      >
        <div className="space-y-4">
          <p className="text-gray-600">
            Create a copy of "{formToClone?.name}" that you can customize for your practice.
          </p>
          <Input
            label="New Form Name"
            value={cloneName}
            onChange={(e) => setCloneName(e.target.value)}
            placeholder="Enter name for the cloned form"
            required
          />
          <div className="flex justify-end gap-2 pt-4">
            <Button
              variant="secondary"
              onClick={() => {
                setIsCloneModalOpen(false);
                setFormToClone(null);
                setCloneName('');
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleCloneForm}>
              Clone Form
            </Button>
          </div>
        </div>
      </Modal>
    </DashboardLayout>
  );
}
