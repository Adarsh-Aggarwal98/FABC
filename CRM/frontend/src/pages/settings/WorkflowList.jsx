import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PlusIcon,
  PencilIcon,
  DocumentDuplicateIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  CogIcon,
  ArrowLeftIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { workflowsAPI } from '../../services/api';

export default function WorkflowList() {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWorkflows();
  }, []);

  const loadWorkflows = async () => {
    try {
      setLoading(true);
      const response = await workflowsAPI.list({ active_only: false });
      setWorkflows(response.data.data.workflows);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load workflows');
    } finally {
      setLoading(false);
    }
  };

  const handleDuplicate = async (workflow) => {
    const newName = prompt('Enter name for the duplicated workflow:', `${workflow.name} (Copy)`);
    if (!newName) return;

    try {
      await workflowsAPI.duplicate(workflow.id, { name: newName });
      toast.success('Workflow duplicated');
      loadWorkflows();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to duplicate workflow');
    }
  };

  const handleDelete = async (workflow) => {
    if (workflow.is_default) {
      toast.error('Cannot delete the default workflow');
      return;
    }

    if (!confirm(`Are you sure you want to delete "${workflow.name}"?`)) return;

    try {
      await workflowsAPI.delete(workflow.id);
      toast.success('Workflow deleted');
      loadWorkflows();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete workflow');
    }
  };

  const handleToggleActive = async (workflow) => {
    try {
      await workflowsAPI.update(workflow.id, { is_active: !workflow.is_active });
      toast.success(workflow.is_active ? 'Workflow deactivated' : 'Workflow activated');
      loadWorkflows();
    } catch (error) {
      toast.error('Failed to update workflow');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Back to Dashboard Button */}
      <button
        onClick={() => navigate('/dashboard')}
        className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
      >
        <ArrowLeftIcon className="w-4 h-4" />
        Back to Dashboard
      </button>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Workflows</h1>
          <p className="text-gray-600 mt-1">
            Manage custom service request workflows
          </p>
        </div>
        <button
          onClick={() => navigate('/settings/workflows/new')}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          <PlusIcon className="w-5 h-5" />
          New Workflow
        </button>
      </div>

      {workflows.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <CogIcon className="w-12 h-12 mx-auto text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900">No workflows yet</h3>
          <p className="text-gray-500 mt-2">
            Create a custom workflow to define how service requests progress
          </p>
          <button
            onClick={() => navigate('/settings/workflows/new')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            Create Workflow
          </button>
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Workflow
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Steps
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Services
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {workflows.map((workflow) => (
                <tr key={workflow.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div>
                        <div className="font-medium text-gray-900">
                          {workflow.name}
                          {workflow.is_default && (
                            <span className="ml-2 px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded">
                              Default
                            </span>
                          )}
                        </div>
                        {workflow.description && (
                          <div className="text-sm text-gray-500">
                            {workflow.description}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {workflow.steps?.length || 0} steps
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {workflow.service_count || 0} services
                  </td>
                  <td className="px-6 py-4">
                    <button
                      onClick={() => handleToggleActive(workflow)}
                      disabled={workflow.is_default}
                      className={`flex items-center gap-1 text-sm ${
                        workflow.is_active
                          ? 'text-green-600'
                          : 'text-gray-400'
                      } ${workflow.is_default ? 'cursor-not-allowed' : 'cursor-pointer hover:underline'}`}
                    >
                      {workflow.is_active ? (
                        <>
                          <CheckCircleIcon className="w-4 h-4" />
                          Active
                        </>
                      ) : (
                        <>
                          <XCircleIcon className="w-4 h-4" />
                          Inactive
                        </>
                      )}
                    </button>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => navigate(`/settings/workflows/${workflow.id}`)}
                        className="p-1 text-gray-400 hover:text-blue-600"
                        title="Edit"
                      >
                        <PencilIcon className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleDuplicate(workflow)}
                        className="p-1 text-gray-400 hover:text-blue-600"
                        title="Duplicate"
                      >
                        <DocumentDuplicateIcon className="w-5 h-5" />
                      </button>
                      {!workflow.is_default && (
                        <button
                          onClick={() => handleDelete(workflow)}
                          className="p-1 text-gray-400 hover:text-red-600"
                          title="Delete"
                        >
                          <TrashIcon className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
