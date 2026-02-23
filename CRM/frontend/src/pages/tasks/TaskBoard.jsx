import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  FunnelIcon,
  ClipboardDocumentListIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { TaskKanbanCard } from '../../components/kanban';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { Select } from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import { tasksAPI, userAPI, requestsAPI, statusAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

// Fallback task statuses (used if API fetch fails)
const FALLBACK_TASK_STATUSES = [
  { status_key: 'pending', display_name: 'Pending', color: '#F59E0B', position: 1 },
  { status_key: 'in_progress', display_name: 'In Progress', color: '#3B82F6', position: 2 },
  { status_key: 'review', display_name: 'Review', color: '#8B5CF6', position: 3 },
  { status_key: 'completed', display_name: 'Completed', color: '#10B981', position: 4 },
];

function TaskColumn({ status, tasks, onDrop, onCardClick, accountants, onAssign, isLoading }) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const taskId = e.dataTransfer.getData('text/plain');
    if (taskId && onDrop) {
      onDrop(taskId, status.status_key);
    }
  };

  return (
    <div
      className={`
        flex flex-col min-w-[280px] max-w-[320px] bg-gray-100 rounded-lg
        ${isDragOver ? 'ring-2 ring-blue-400 bg-blue-50' : ''}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Column Header */}
      <div
        className="p-3 border-b border-gray-200"
        style={{ borderTopWidth: '3px', borderTopColor: status.color }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-gray-900">{status.display_name}</h3>
            <span className="text-xs px-2 py-0.5 rounded-full bg-gray-200 text-gray-700">
              {tasks.length}
            </span>
          </div>
        </div>
      </div>

      {/* Cards Container */}
      <div className="flex-1 p-2 space-y-2 overflow-y-auto max-h-[calc(100vh-300px)]">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin h-6 w-6 border-2 border-blue-500 rounded-full border-t-transparent"></div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">
            No tasks
          </div>
        ) : (
          tasks.map((task) => (
            <TaskKanbanCard
              key={task.id}
              task={task}
              onClick={onCardClick}
              accountants={accountants}
              onAssign={onAssign}
            />
          ))
        )}
      </div>

      {/* Drop indicator */}
      {isDragOver && (
        <div className="mx-2 mb-2 border-2 border-dashed border-blue-300 rounded-lg p-4 text-center text-blue-500 text-sm">
          Drop here
        </div>
      )}
    </div>
  );
}

export default function TaskBoard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [tasks, setTasks] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [accountants, setAccountants] = useState([]);
  const [requests, setRequests] = useState([]);
  const [taskStatuses, setTaskStatuses] = useState(FALLBACK_TASK_STATUSES);

  // Filters
  const [assigneeFilter, setAssigneeFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [requestFilter, setRequestFilter] = useState('');

  // Create/Edit modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    assigned_to_id: '',
    service_request_id: '',
    due_date: '',
    priority: 'normal',
    estimated_minutes: '',
  });

  const isAdmin = ['super_admin', 'admin', 'senior_accountant'].includes(user?.role);
  const isAccountant = ['accountant', 'senior_accountant'].includes(user?.role);

  useEffect(() => {
    fetchTaskStatuses();
    fetchTasks();
    fetchAccountants();
    fetchRequests();
  }, [assigneeFilter, priorityFilter, requestFilter]);

  const fetchTaskStatuses = async () => {
    try {
      const response = await statusAPI.list(false, 'task');
      const fetched = response.data.statuses || [];
      if (fetched.length > 0) {
        setTaskStatuses(fetched);
      }
    } catch (error) {
      console.error('Failed to fetch task statuses, using fallback:', error);
    }
  };

  const fetchTasks = async () => {
    setIsLoading(true);
    try {
      const params = {};
      if (assigneeFilter) params.assigned_to_id = assigneeFilter;
      if (priorityFilter) params.priority = priorityFilter;
      if (requestFilter) params.service_request_id = requestFilter;

      const response = await tasksAPI.list(params);
      setTasks(response.data.data || []);
    } catch (error) {
      toast.error('Failed to fetch tasks');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchAccountants = async () => {
    try {
      const response = await userAPI.getAccountants();
      setAccountants(response.data.data || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch accountants');
    }
  };

  const fetchRequests = async () => {
    try {
      const response = await requestsAPI.list({ per_page: 100 });
      setRequests(response.data.data?.requests || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch requests');
    }
  };

  // Group tasks by status
  const groupedTasks = useMemo(() => {
    const groups = {};
    taskStatuses.forEach((status) => {
      groups[status.status_key] = tasks.filter((t) => t.status === status.status_key);
    });
    return groups;
  }, [tasks, taskStatuses]);

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await tasksAPI.updateStatus(taskId, newStatus);

      // Optimistic update
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
      );

      toast.success('Task updated');
    } catch (error) {
      toast.error('Failed to update task');
      fetchTasks();
    }
  };

  const handleAssign = async (taskId, accountantId) => {
    try {
      await tasksAPI.update(taskId, { assigned_to_id: accountantId });
      fetchTasks();
      toast.success('Task assigned');
    } catch (error) {
      toast.error('Failed to assign task');
    }
  };

  const handleCardClick = (task) => {
    setEditingTask(task);
    setFormData({
      title: task.title || '',
      description: task.description || '',
      assigned_to_id: task.assigned_to?.id || '',
      service_request_id: task.service_request?.id || '',
      due_date: task.due_date || '',
      priority: task.priority || 'normal',
      estimated_minutes: task.estimated_minutes ? String(Math.round(task.estimated_minutes / 60)) : '',
    });
    setIsModalOpen(true);
  };

  const handleCreateNew = () => {
    setEditingTask(null);
    setFormData({
      title: '',
      description: '',
      assigned_to_id: isAccountant && !isAdmin ? user.id : '',
      service_request_id: '',
      due_date: '',
      priority: 'normal',
      estimated_minutes: '',
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const data = {
        ...formData,
        estimated_minutes: formData.estimated_minutes ? parseInt(formData.estimated_minutes) * 60 : null,
        assigned_to_id: formData.assigned_to_id || null,
        service_request_id: formData.service_request_id || null,
      };

      if (editingTask) {
        await tasksAPI.update(editingTask.id, data);
        toast.success('Task updated');
      } else {
        await tasksAPI.create(data);
        toast.success('Task created');
      }

      setIsModalOpen(false);
      fetchTasks();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save task');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!editingTask || !window.confirm('Are you sure you want to delete this task?')) return;

    try {
      await tasksAPI.delete(editingTask.id);
      toast.success('Task deleted');
      setIsModalOpen(false);
      fetchTasks();
    } catch (error) {
      toast.error('Failed to delete task');
    }
  };

  const clearFilters = () => {
    setAssigneeFilter('');
    setPriorityFilter('');
    setRequestFilter('');
  };

  const hasFilters = assigneeFilter || priorityFilter || requestFilter;

  return (
    <DashboardLayout title="Task Board">
      <div className="space-y-6">
        <Card>
          <CardHeader
            title="Tasks"
            subtitle="Manage and track your tasks"
            action={
              <Button icon={PlusIcon} onClick={handleCreateNew}>
                Create Task
              </Button>
            }
          />

          {/* Filters */}
          <div className="flex flex-wrap gap-3 mb-6 items-end">
            <div className="flex items-center gap-2">
              <FunnelIcon className="h-4 w-4 text-gray-400" />
              <span className="text-sm text-gray-500">Filters:</span>
            </div>

            {isAdmin && (
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">Assignee</label>
                <Select
                  options={[
                    { value: '', label: 'All Assignees' },
                    ...accountants.map((a) => ({ value: a.id, label: a.full_name || a.email })),
                  ]}
                  value={assigneeFilter}
                  onChange={(e) => setAssigneeFilter(e.target.value)}
                  className="w-40"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Priority</label>
              <Select
                options={[
                  { value: '', label: 'All Priorities' },
                  { value: 'urgent', label: 'Urgent' },
                  { value: 'high', label: 'High' },
                  { value: 'normal', label: 'Normal' },
                  { value: 'low', label: 'Low' },
                ]}
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="w-36"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Request</label>
              <Select
                options={[
                  { value: '', label: 'All Requests' },
                  ...requests.map((r) => ({
                    value: r.id,
                    label: `${r.request_number} - ${r.service?.name || 'Unknown'}`,
                  })),
                ]}
                value={requestFilter}
                onChange={(e) => setRequestFilter(e.target.value)}
                className="w-56"
              />
            </div>

            {hasFilters && (
              <Button variant="secondary" size="sm" onClick={clearFilters}>
                Clear Filters
              </Button>
            )}
          </div>

          {/* Kanban Board */}
          <div className="flex gap-4 overflow-x-auto pb-4">
            {taskStatuses.sort((a, b) => a.position - b.position).map((status) => (
              <TaskColumn
                key={status.status_key}
                status={status}
                tasks={groupedTasks[status.status_key] || []}
                onDrop={handleStatusChange}
                onCardClick={handleCardClick}
                accountants={isAdmin ? accountants : []}
                onAssign={isAdmin ? handleAssign : null}
                isLoading={isLoading}
              />
            ))}
          </div>

          {/* Empty state */}
          {!isLoading && tasks.length === 0 && (
            <div className="text-center py-12">
              <ClipboardDocumentListIcon className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No tasks yet</h3>
              <p className="text-gray-500 mb-4">Create your first task to get started</p>
              <Button icon={PlusIcon} onClick={handleCreateNew}>
                Create Task
              </Button>
            </div>
          )}
        </Card>
      </div>

      {/* Create/Edit Task Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingTask ? 'Edit Task' : 'Create Task'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="Task title"
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Task description"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Assign To"
              options={[
                { value: '', label: 'Unassigned' },
                ...accountants.map((a) => ({ value: a.id, label: a.full_name || a.email })),
              ]}
              value={formData.assigned_to_id}
              onChange={(e) => setFormData({ ...formData, assigned_to_id: e.target.value })}
              disabled={!isAdmin && formData.assigned_to_id === user?.id}
            />

            <Select
              label="Priority"
              options={[
                { value: 'low', label: 'Low' },
                { value: 'normal', label: 'Normal' },
                { value: 'high', label: 'High' },
                { value: 'urgent', label: 'Urgent' },
              ]}
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Due Date"
              type="date"
              value={formData.due_date}
              onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
            />

            <Input
              label="Estimated Hours"
              type="number"
              min="0"
              step="0.5"
              value={formData.estimated_minutes}
              onChange={(e) => setFormData({ ...formData, estimated_minutes: e.target.value })}
              placeholder="e.g., 2"
            />
          </div>

          <Select
            label="Link to Request (optional)"
            options={[
              { value: '', label: 'No linked request' },
              ...requests.map((r) => ({
                value: r.id,
                label: `${r.request_number} - ${r.service?.name || 'Unknown'}`,
              })),
            ]}
            value={formData.service_request_id}
            onChange={(e) => setFormData({ ...formData, service_request_id: e.target.value })}
          />

          <div className="flex justify-between pt-4">
            <div>
              {editingTask && isAdmin && (
                <Button variant="danger" type="button" onClick={handleDelete}>
                  Delete
                </Button>
              )}
            </div>
            <div className="flex gap-3">
              <Button variant="secondary" type="button" onClick={() => setIsModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={isSubmitting}>
                {editingTask ? 'Update Task' : 'Create Task'}
              </Button>
            </div>
          </div>
        </form>
      </Modal>
    </DashboardLayout>
  );
}
