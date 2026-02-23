import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  PlusIcon,
  TrashIcon,
  ArrowPathIcon,
  Squares2X2Icon,
  CheckIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import { statusAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

export default function StatusSettings() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [statuses, setStatuses] = useState([]);
  const [isCustomized, setIsCustomized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Modal states
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingStatus, setEditingStatus] = useState(null);
  const [showResetConfirm, setShowResetConfirm] = useState(false);

  // Form state for add/edit
  const [formData, setFormData] = useState({
    status_key: '',
    display_name: '',
    description: '',
    color: '#6B7280',
    wip_limit: '',
    is_final: false,
    category: 'request',
    is_default: false,
  });

  // Transitions state
  const [transitions, setTransitions] = useState([]);
  const [showTransitionModal, setShowTransitionModal] = useState(false);
  const [transitionForm, setTransitionForm] = useState({
    from_status_key: '',
    to_status_key: '',
    allowed_roles: [],
    requires_note: false,
  });

  const allRoles = ['super_admin', 'admin', 'senior_accountant', 'accountant', 'external_accountant'];

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'senior_accountant';

  useEffect(() => {
    if (!isAdmin) {
      navigate('/dashboard');
      return;
    }
    fetchStatuses();
    fetchTransitions();
  }, [isAdmin]);

  const fetchTransitions = async () => {
    try {
      const response = await statusAPI.getTransitions();
      setTransitions(response.data.transitions || []);
    } catch (error) {
      console.error('Failed to fetch transitions:', error);
    }
  };

  const handleAddTransition = async () => {
    if (!transitionForm.from_status_key || !transitionForm.to_status_key) {
      toast.error('From and To statuses are required');
      return;
    }
    setIsSaving(true);
    try {
      await statusAPI.createTransition({
        from_status_key: transitionForm.from_status_key,
        to_status_key: transitionForm.to_status_key,
        allowed_roles: transitionForm.allowed_roles.length > 0 ? transitionForm.allowed_roles : null,
        requires_note: transitionForm.requires_note,
      });
      toast.success('Transition rule created');
      setShowTransitionModal(false);
      fetchTransitions();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create transition');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteTransition = async (id) => {
    if (!window.confirm('Delete this transition rule?')) return;
    try {
      await statusAPI.deleteTransition(id);
      toast.success('Transition deleted');
      fetchTransitions();
    } catch (error) {
      toast.error('Failed to delete transition');
    }
  };

  const fetchStatuses = async () => {
    setIsLoading(true);
    try {
      const response = await statusAPI.list(true); // include inactive
      setStatuses(response.data.statuses || []);
      setIsCustomized(response.data.is_customized || false);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch statuses');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInitialize = async () => {
    setIsSaving(true);
    try {
      await statusAPI.initialize();
      toast.success('Custom statuses initialized successfully');
      fetchStatuses();
    } catch (error) {
      if (error.response?.data?.error?.includes('already')) {
        toast.error('Custom statuses are already initialized');
      } else {
        toast.error(error.response?.data?.error || 'Failed to initialize');
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = async () => {
    setIsSaving(true);
    try {
      await statusAPI.reset();
      toast.success('Statuses reset to system defaults');
      setShowResetConfirm(false);
      fetchStatuses();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to reset');
    } finally {
      setIsSaving(false);
    }
  };

  const openAddModal = () => {
    setFormData({
      status_key: '',
      display_name: '',
      description: '',
      color: '#6B7280',
      wip_limit: '',
      is_final: false,
      category: 'request',
      is_default: false,
    });
    setEditingStatus(null);
    setShowAddModal(true);
  };

  const openEditModal = (status) => {
    setFormData({
      status_key: status.status_key,
      display_name: status.display_name,
      description: status.description || '',
      color: status.color,
      wip_limit: status.wip_limit || '',
      is_final: status.is_final,
      category: status.category || 'request',
      is_default: status.is_default || false,
    });
    setEditingStatus(status);
    setShowAddModal(true);
  };

  const handleSaveStatus = async () => {
    if (!formData.display_name.trim()) {
      toast.error('Display name is required');
      return;
    }

    setIsSaving(true);
    try {
      if (editingStatus) {
        // Update existing
        await statusAPI.update(editingStatus.id, {
          display_name: formData.display_name,
          description: formData.description || null,
          color: formData.color,
          wip_limit: formData.wip_limit ? parseInt(formData.wip_limit, 10) : null,
          is_final: formData.is_final,
          category: formData.category,
          is_default: formData.is_default,
        });
        toast.success('Status updated successfully');
      } else {
        // Create new
        if (!formData.status_key.trim()) {
          toast.error('Status key is required');
          setIsSaving(false);
          return;
        }
        await statusAPI.create({
          status_key: formData.status_key.toLowerCase().replace(/\s+/g, '_'),
          display_name: formData.display_name,
          description: formData.description || null,
          color: formData.color,
          wip_limit: formData.wip_limit ? parseInt(formData.wip_limit, 10) : null,
          is_final: formData.is_final,
          category: formData.category,
          is_default: formData.is_default,
        });
        toast.success('Status created successfully');
      }
      setShowAddModal(false);
      fetchStatuses();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save status');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteStatus = async (status) => {
    if (!window.confirm(`Are you sure you want to delete "${status.display_name}"?`)) {
      return;
    }

    try {
      await statusAPI.delete(status.id);
      toast.success('Status deleted');
      fetchStatuses();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete status');
    }
  };

  const handleToggleActive = async (status) => {
    try {
      await statusAPI.update(status.id, { is_active: !status.is_active });
      toast.success(`Status ${status.is_active ? 'deactivated' : 'activated'}`);
      fetchStatuses();
    } catch (error) {
      toast.error('Failed to update status');
    }
  };

  // Predefined colors for quick selection
  const colorOptions = [
    '#F59E0B', // Yellow
    '#3B82F6', // Blue
    '#10B981', // Green
    '#EF4444', // Red
    '#8B5CF6', // Purple
    '#6B7280', // Gray
    '#EC4899', // Pink
    '#14B8A6', // Teal
  ];

  if (isLoading) {
    return (
      <DashboardLayout title="Status Settings">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin h-8 w-8 border-2 border-blue-500 rounded-full border-t-transparent" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Status Settings">
      <div className="space-y-6">
        {/* Header with back button */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="secondary"
              onClick={() => navigate('/settings')}
              className="flex items-center gap-2"
            >
              <ArrowLeftIcon className="w-4 h-4" />
              Back
            </Button>
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Kanban Board Statuses</h1>
              <p className="text-sm text-gray-500">
                Customize the status columns for your Kanban board
              </p>
            </div>
          </div>
        </div>

        {/* Main Card */}
        <Card>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-medium text-gray-900">
                {isCustomized ? 'Custom Statuses' : 'System Default Statuses'}
              </h2>
              <p className="text-sm text-gray-500">
                {isCustomized
                  ? 'You have customized your status columns'
                  : 'Using system default statuses. Initialize to customize.'}
              </p>
            </div>
            <div className="flex gap-2">
              {!isCustomized ? (
                <Button onClick={handleInitialize} disabled={isSaving}>
                  <Squares2X2Icon className="w-4 h-4 mr-2" />
                  Customize Statuses
                </Button>
              ) : (
                <>
                  <Button variant="secondary" onClick={() => setShowResetConfirm(true)}>
                    <ArrowPathIcon className="w-4 h-4 mr-2" />
                    Reset to Defaults
                  </Button>
                  <Button onClick={openAddModal}>
                    <PlusIcon className="w-4 h-4 mr-2" />
                    Add Status
                  </Button>
                </>
              )}
            </div>
          </div>

          {/* Statuses List */}
          <div className="space-y-2">
            {statuses
              .sort((a, b) => a.position - b.position)
              .map((status) => (
                <div
                  key={status.id || status.status_key}
                  className={`flex items-center justify-between p-4 rounded-lg border ${
                    status.is_active ? 'bg-white border-gray-200' : 'bg-gray-50 border-gray-100'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    {/* Color indicator */}
                    <div
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: status.color }}
                    />
                    {/* Status info */}
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900">{status.display_name}</span>
                        <span className="text-xs text-gray-400 font-mono">{status.status_key}</span>
                        {status.category && (
                          <span className={`text-xs px-2 py-0.5 rounded ${
                            status.category === 'both' ? 'bg-purple-100 text-purple-600' :
                            status.category === 'task' ? 'bg-cyan-100 text-cyan-600' :
                            'bg-indigo-100 text-indigo-600'
                          }`}>
                            {status.category === 'both' ? 'Both' : status.category === 'task' ? 'Task' : 'Request'}
                          </span>
                        )}
                        {status.is_default && (
                          <span className="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded">
                            Default
                          </span>
                        )}
                        {status.is_final && (
                          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded">
                            Final
                          </span>
                        )}
                        {!status.is_active && (
                          <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded">
                            Inactive
                          </span>
                        )}
                        {status.wip_limit && (
                          <span className="text-xs bg-blue-100 text-blue-600 px-2 py-0.5 rounded">
                            WIP: {status.wip_limit}
                          </span>
                        )}
                      </div>
                      {status.description && (
                        <p className="text-sm text-gray-500">{status.description}</p>
                      )}
                    </div>
                  </div>

                  {/* Actions (only for custom statuses) */}
                  {isCustomized && !status.is_system && (
                    <div className="flex items-center gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleToggleActive(status)}
                      >
                        {status.is_active ? 'Deactivate' : 'Activate'}
                      </Button>
                      <Button variant="secondary" size="sm" onClick={() => openEditModal(status)}>
                        Edit
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleDeleteStatus(status)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </Button>
                    </div>
                  )}
                </div>
              ))}
          </div>
        </Card>

        {/* Workflow Transitions */}
        <Card>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-medium text-gray-900">Workflow Transitions</h2>
              <p className="text-sm text-gray-500">
                Define which status changes are allowed and for which roles.
                {transitions.length > 0 && transitions[0]?.is_system && (
                  <span className="ml-1 text-gray-400">(Using system defaults)</span>
                )}
              </p>
            </div>
            <Button onClick={() => {
              setTransitionForm({ from_status_key: '', to_status_key: '', allowed_roles: [], requires_note: false });
              setShowTransitionModal(true);
            }}>
              <PlusIcon className="w-4 h-4 mr-2" />
              Add Rule
            </Button>
          </div>

          <div className="space-y-2">
            {transitions.length === 0 ? (
              <p className="text-gray-400 text-sm text-center py-6">
                No transition rules defined. All status changes are allowed.
              </p>
            ) : (
              transitions.map((t) => {
                const fromStatus = statuses.find(s => s.status_key === t.from_status_key);
                const toStatus = statuses.find(s => s.status_key === t.to_status_key);
                return (
                  <div key={t.id} className="flex items-center justify-between p-3 rounded-lg border bg-white border-gray-200">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2">
                        <span
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: fromStatus?.color || '#6B7280' }}
                        />
                        <span className="font-medium text-sm">{fromStatus?.display_name || t.from_status_key}</span>
                      </div>
                      <ArrowRightIcon className="w-4 h-4 text-gray-400" />
                      <div className="flex items-center gap-2">
                        <span
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: toStatus?.color || '#6B7280' }}
                        />
                        <span className="font-medium text-sm">{toStatus?.display_name || t.to_status_key}</span>
                      </div>
                      {t.allowed_roles && (
                        <div className="flex gap-1 ml-2">
                          {t.allowed_roles.map(role => (
                            <span key={role} className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
                              {role.replace('_', ' ')}
                            </span>
                          ))}
                        </div>
                      )}
                      {t.requires_note && (
                        <span className="text-xs bg-yellow-100 text-yellow-700 px-1.5 py-0.5 rounded">
                          Note required
                        </span>
                      )}
                      {t.is_system && (
                        <span className="text-xs bg-blue-50 text-blue-500 px-1.5 py-0.5 rounded">
                          System
                        </span>
                      )}
                    </div>
                    {!t.is_system && (
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleDeleteTransition(t.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <TrashIcon className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                );
              })
            )}
          </div>
        </Card>

        {/* Add Transition Modal */}
        <Modal
          isOpen={showTransitionModal}
          onClose={() => setShowTransitionModal(false)}
          title="Add Transition Rule"
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">From Status</label>
              <select
                value={transitionForm.from_status_key}
                onChange={(e) => setTransitionForm({ ...transitionForm, from_status_key: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select status...</option>
                {statuses.filter(s => s.is_active !== false).map(s => (
                  <option key={s.status_key} value={s.status_key}>{s.display_name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">To Status</label>
              <select
                value={transitionForm.to_status_key}
                onChange={(e) => setTransitionForm({ ...transitionForm, to_status_key: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="">Select status...</option>
                {statuses.filter(s => s.is_active !== false).map(s => (
                  <option key={s.status_key} value={s.status_key}>{s.display_name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Allowed Roles (leave empty for all roles)
              </label>
              <div className="space-y-1">
                {allRoles.map(role => (
                  <label key={role} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={transitionForm.allowed_roles.includes(role)}
                      onChange={(e) => {
                        const roles = e.target.checked
                          ? [...transitionForm.allowed_roles, role]
                          : transitionForm.allowed_roles.filter(r => r !== role);
                        setTransitionForm({ ...transitionForm, allowed_roles: roles });
                      }}
                      className="h-4 w-4 text-blue-600 rounded border-gray-300"
                    />
                    <span className="text-sm text-gray-700 capitalize">{role.replace(/_/g, ' ')}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="requires_note"
                checked={transitionForm.requires_note}
                onChange={(e) => setTransitionForm({ ...transitionForm, requires_note: e.target.checked })}
                className="h-4 w-4 text-blue-600 rounded border-gray-300"
              />
              <label htmlFor="requires_note" className="ml-2 text-sm text-gray-700">
                Require a note for this transition
              </label>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="secondary" onClick={() => setShowTransitionModal(false)}>
                Cancel
              </Button>
              <Button onClick={handleAddTransition} disabled={isSaving}>
                {isSaving ? 'Saving...' : 'Create Rule'}
              </Button>
            </div>
          </div>
        </Modal>

        {/* Add/Edit Modal */}
        <Modal
          isOpen={showAddModal}
          onClose={() => setShowAddModal(false)}
          title={editingStatus ? 'Edit Status' : 'Add Status'}
        >
          <div className="space-y-4">
            {!editingStatus && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status Key
                </label>
                <Input
                  value={formData.status_key}
                  onChange={(e) =>
                    setFormData({ ...formData, status_key: e.target.value })
                  }
                  placeholder="e.g., review_pending"
                  className="font-mono"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Lowercase with underscores. Cannot be changed later.
                </p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Display Name
              </label>
              <Input
                value={formData.display_name}
                onChange={(e) =>
                  setFormData({ ...formData, display_name: e.target.value })
                }
                placeholder="e.g., Review Pending"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description (optional)
              </label>
              <Input
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
                placeholder="Brief description of this status"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Color</label>
              <div className="flex items-center gap-3">
                <input
                  type="color"
                  value={formData.color}
                  onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                  className="w-10 h-10 rounded cursor-pointer border border-gray-300"
                />
                <div className="flex gap-1">
                  {colorOptions.map((color) => (
                    <button
                      key={color}
                      onClick={() => setFormData({ ...formData, color })}
                      className={`w-6 h-6 rounded border-2 ${
                        formData.color === color ? 'border-gray-900' : 'border-transparent'
                      }`}
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                WIP Limit (optional)
              </label>
              <Input
                type="number"
                min="1"
                value={formData.wip_limit}
                onChange={(e) => setFormData({ ...formData, wip_limit: e.target.value })}
                placeholder="Max items in this column"
              />
              <p className="text-xs text-gray-500 mt-1">
                Work-in-Progress limit. Leave empty for no limit.
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option value="request">Request only</option>
                <option value="task">Task only</option>
                <option value="both">Both (Request & Task)</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                Controls which boards this status appears on.
              </p>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_final"
                checked={formData.is_final}
                onChange={(e) => setFormData({ ...formData, is_final: e.target.checked })}
                className="h-4 w-4 text-blue-600 rounded border-gray-300"
              />
              <label htmlFor="is_final" className="ml-2 text-sm text-gray-700">
                This is a final status (e.g., Completed, Cancelled)
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="is_default"
                checked={formData.is_default}
                onChange={(e) => setFormData({ ...formData, is_default: e.target.checked })}
                className="h-4 w-4 text-blue-600 rounded border-gray-300"
              />
              <label htmlFor="is_default" className="ml-2 text-sm text-gray-700">
                Default status for new items
              </label>
            </div>

            <div className="flex justify-end gap-3 pt-4">
              <Button variant="secondary" onClick={() => setShowAddModal(false)}>
                Cancel
              </Button>
              <Button onClick={handleSaveStatus} disabled={isSaving}>
                {isSaving ? 'Saving...' : editingStatus ? 'Update' : 'Create'}
              </Button>
            </div>
          </div>
        </Modal>

        {/* Reset Confirmation Modal */}
        <Modal
          isOpen={showResetConfirm}
          onClose={() => setShowResetConfirm(false)}
          title="Reset to System Defaults?"
        >
          <div className="space-y-4">
            <p className="text-gray-600">
              This will delete all your custom statuses and revert to system defaults.
              This action cannot be undone.
            </p>
            <p className="text-sm text-red-600">
              Note: This will fail if any requests are using custom statuses that
              don't exist in system defaults.
            </p>
            <div className="flex justify-end gap-3 pt-4">
              <Button variant="secondary" onClick={() => setShowResetConfirm(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleReset}
                disabled={isSaving}
                className="bg-red-600 hover:bg-red-700"
              >
                {isSaving ? 'Resetting...' : 'Reset to Defaults'}
              </Button>
            </div>
          </div>
        </Modal>
      </div>
    </DashboardLayout>
  );
}
