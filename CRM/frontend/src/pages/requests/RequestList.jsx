import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { PlusIcon } from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { Select } from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import { KanbanBoard, ViewToggle } from '../../components/kanban';
import { requestsAPI, companiesAPI, servicesAPI, userAPI, tasksAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

export default function RequestList() {
  const { user } = useAuthStore();
  const [searchParams, setSearchParams] = useSearchParams();
  const [requests, setRequests] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // View state (persisted in localStorage)
  const [currentView, setCurrentView] = useState(() => {
    return localStorage.getItem('requestListView') || 'list';
  });

  // Tasks state
  const [tasks, setTasks] = useState([]);
  const [isLoadingTasks, setIsLoadingTasks] = useState(false);

  // Type filter: 'all' | 'requests' | 'tasks'
  const [typeFilter, setTypeFilter] = useState(searchParams.get('type') || 'all');

  // Filter states
  const [statusFilter, setStatusFilter] = useState(searchParams.get('status') || '');
  const [companyFilter, setCompanyFilter] = useState(searchParams.get('company_id') || '');
  const [serviceFilter, setServiceFilter] = useState(searchParams.get('service_id') || '');
  const [invoiceStatusFilter, setInvoiceStatusFilter] = useState(searchParams.get('invoice_status') || '');
  const [dateFrom, setDateFrom] = useState(searchParams.get('date_from') || '');
  const [dateTo, setDateTo] = useState(searchParams.get('date_to') || '');
  const [searchTerm, setSearchTerm] = useState(searchParams.get('search') || '');
  const [accountantFilter, setAccountantFilter] = useState(searchParams.get('accountant_id') || '');
  const [clientFilter, setClientFilter] = useState(searchParams.get('user_id') || '');
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  // Data for dropdowns
  const [companies, setCompanies] = useState([]);
  const [services, setServices] = useState([]);
  const [accountants, setAccountants] = useState([]);
  const [clients, setClients] = useState([]);

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'senior_accountant';
  const isAccountant = ['accountant', 'senior_accountant'].includes(user?.role);
  const isSuperAdmin = user?.role === 'super_admin';
  const isStaff = isAdmin || user?.role === 'accountant';

  // Task modal state
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [isTaskSubmitting, setIsTaskSubmitting] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [taskFormData, setTaskFormData] = useState({
    title: '',
    description: '',
    assigned_to_id: '',
    due_date: '',
    priority: 'normal',
    estimated_minutes: '',
  });

  useEffect(() => {
    fetchServices();
    if (isAdmin) {
      fetchAccountants();
      fetchClients();
    }
    if (isSuperAdmin) {
      fetchCompanies();
    }
  }, [isAdmin, isSuperAdmin]);

  useEffect(() => {
    fetchRequests(1);
  }, [statusFilter, companyFilter, serviceFilter, invoiceStatusFilter, dateFrom, dateTo, accountantFilter, clientFilter]);

  useEffect(() => {
    if (isStaff) {
      fetchTasks();
    }
  }, [accountantFilter]);

  const fetchCompanies = async () => {
    try {
      const response = await companiesAPI.list({ active_only: true });
      setCompanies(response.data.data?.companies || response.data.companies || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch companies');
    }
  };

  const fetchServices = async () => {
    try {
      const response = await servicesAPI.list({ active_only: true });
      setServices(response.data.data?.services || response.data.services || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch services');
    }
  };

  const fetchAccountants = async () => {
    try {
      const response = await userAPI.getAccountants();
      setAccountants(response.data.data?.accountants || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch accountants');
    }
  };

  const fetchClients = async () => {
    try {
      const response = await userAPI.list({ role: 'user', per_page: 500 });
      setClients(response.data.data || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch clients');
    }
  };

  const fetchRequests = async (page) => {
    setIsLoading(true);
    try {
      const params = {
        page,
        status: statusFilter || undefined,
        service_id: serviceFilter || undefined,
        invoice_status: invoiceStatusFilter || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        search: searchTerm || undefined,
        accountant_id: accountantFilter || undefined,
        user_id: clientFilter || undefined,
      };
      if (isSuperAdmin && companyFilter) {
        params.company_id = companyFilter;
      }
      const response = await requestsAPI.list(params);
      setRequests(response.data.data.requests || []);
      setPagination(response.data.data.pagination);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch requests');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTasks = async () => {
    setIsLoadingTasks(true);
    try {
      const params = {};
      if (accountantFilter) params.assigned_to_id = accountantFilter;
      const response = await tasksAPI.list(params);
      setTasks(response.data.data || []);
    } catch (error) {
      toast.error('Failed to fetch tasks');
    } finally {
      setIsLoadingTasks(false);
    }
  };

  const handleStatusFilterChange = (e) => {
    setStatusFilter(e.target.value);
    updateSearchParams({ status: e.target.value });
  };

  const handleCompanyFilterChange = (e) => {
    setCompanyFilter(e.target.value);
    updateSearchParams({ company_id: e.target.value });
  };

  const handleServiceFilterChange = (e) => {
    setServiceFilter(e.target.value);
    updateSearchParams({ service_id: e.target.value });
  };

  const handleInvoiceStatusFilterChange = (e) => {
    setInvoiceStatusFilter(e.target.value);
    updateSearchParams({ invoice_status: e.target.value });
  };

  const handleDateFromChange = (e) => {
    setDateFrom(e.target.value);
    updateSearchParams({ date_from: e.target.value });
  };

  const handleDateToChange = (e) => {
    setDateTo(e.target.value);
    updateSearchParams({ date_to: e.target.value });
  };

  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSearchSubmit = (e) => {
    if (e.key === 'Enter') {
      updateSearchParams({ search: searchTerm });
      fetchRequests(1);
    }
  };

  const handleAccountantFilterChange = (e) => {
    setAccountantFilter(e.target.value);
    updateSearchParams({ accountant_id: e.target.value });
  };

  const handleClientFilterChange = (e) => {
    setClientFilter(e.target.value);
    updateSearchParams({ user_id: e.target.value });
  };

  const clearAllFilters = () => {
    setStatusFilter('');
    setCompanyFilter('');
    setServiceFilter('');
    setInvoiceStatusFilter('');
    setDateFrom('');
    setDateTo('');
    setSearchTerm('');
    setAccountantFilter('');
    setClientFilter('');
    setTypeFilter('all');
    setSearchParams(new URLSearchParams());
  };

  const hasActiveFilters = statusFilter || companyFilter || serviceFilter ||
    invoiceStatusFilter || dateFrom || dateTo || searchTerm || accountantFilter || clientFilter || typeFilter !== 'all';

  // Task handlers
  const handleOpenTaskModal = () => {
    setEditingTask(null);
    setTaskFormData({
      title: '',
      description: '',
      assigned_to_id: isAccountant && !isAdmin ? user.id : '',
      due_date: '',
      priority: 'normal',
      estimated_minutes: '',
    });
    setIsTaskModalOpen(true);
  };

  const handleEditTask = (task) => {
    setEditingTask(task);
    setTaskFormData({
      title: task.title || '',
      description: task.description || '',
      assigned_to_id: task.assigned_to?.id || '',
      due_date: task.due_date || '',
      priority: task.priority || 'normal',
      estimated_minutes: task.estimated_minutes ? String(Math.round(task.estimated_minutes / 60)) : '',
    });
    setIsTaskModalOpen(true);
  };

  const handleTaskSubmit = async (e) => {
    e.preventDefault();
    setIsTaskSubmitting(true);
    try {
      const data = {
        ...taskFormData,
        estimated_minutes: taskFormData.estimated_minutes ? parseInt(taskFormData.estimated_minutes) * 60 : null,
        assigned_to_id: taskFormData.assigned_to_id || null,
        service_request_id: taskFormData.service_request_id || null,
      };
      if (editingTask) {
        await tasksAPI.update(editingTask.id, data);
        toast.success('Task updated');
      } else {
        data.service_request_id = null;
        await tasksAPI.create(data);
        toast.success('Task created');
      }
      setIsTaskModalOpen(false);
      fetchTasks();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save task');
    } finally {
      setIsTaskSubmitting(false);
    }
  };

  const handleDeleteTask = async () => {
    if (!editingTask || !window.confirm('Are you sure you want to delete this task?')) return;
    try {
      await tasksAPI.delete(editingTask.id);
      toast.success('Task deleted');
      setIsTaskModalOpen(false);
      fetchTasks();
    } catch (error) {
      toast.error('Failed to delete task');
    }
  };

  const handleTaskStatusChange = (taskId, newStatus, shouldRefresh = false) => {
    if (shouldRefresh) {
      fetchTasks();
    } else if (newStatus) {
      setTasks((prev) => prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t)));
    }
  };

  // Handle view toggle
  const handleViewChange = (view) => {
    setCurrentView(view);
    localStorage.setItem('requestListView', view);
  };

  // Handle status change from Kanban (refresh data)
  const handleKanbanStatusChange = (requestId, newStatus, shouldRefresh = false) => {
    if (shouldRefresh) {
      fetchRequests(pagination?.current_page || 1);
    } else if (newStatus) {
      setRequests((prev) =>
        prev.map((r) => (r.id === requestId ? { ...r, status: newStatus } : r))
      );
    }
  };

  const updateSearchParams = (updates) => {
    const newParams = new URLSearchParams(searchParams);
    Object.entries(updates).forEach(([key, value]) => {
      if (value) {
        newParams.set(key, value);
      } else {
        newParams.delete(key);
      }
    });
    setSearchParams(newParams);
  };

  // Task status helpers
  const getTaskStatusBadge = (status) => {
    const styles = {
      todo: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-blue-100 text-blue-800',
      review: 'bg-purple-100 text-purple-800',
      done: 'bg-green-100 text-green-800',
    };
    const labels = { todo: 'To Do', in_progress: 'In Progress', review: 'Review', done: 'Done' };
    return { style: styles[status] || 'bg-gray-100 text-gray-600', label: labels[status] || status };
  };

  // Normalize tasks into request-like rows for the unified list
  const normalizedTasks = tasks.map((task) => ({
    ...task,
    _isTask: true,
    _type: 'task',
  }));

  const normalizedRequests = requests.map((req) => ({
    ...req,
    _isTask: false,
    _type: 'request',
  }));

  // Unified list based on type filter
  const getUnifiedData = () => {
    if (typeFilter === 'tasks') return normalizedTasks;
    if (typeFilter === 'requests') return normalizedRequests;
    return [...normalizedRequests, ...normalizedTasks];
  };

  // Unified columns that handle both types
  const unifiedColumns = [
    {
      key: 'type',
      title: 'Type',
      render: (row) => row._isTask ? (
        <span className="text-xs px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700 font-medium">Task</span>
      ) : (
        <span className="text-xs px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 font-medium">Request</span>
      ),
    },
    {
      key: 'name',
      title: 'Name / Service',
      render: (row) => row._isTask ? (
        <div>
          <p className="font-medium text-gray-900">{row.title}</p>
          {row.description && <p className="text-xs text-gray-400 line-clamp-1">{row.description}</p>}
          {row.service_request && (
            <Link to={`/requests/${row.service_request.id}`} className="text-xs text-primary-600 hover:underline">
              Linked: {row.service_request.request_number}
            </Link>
          )}
        </div>
      ) : (
        <div>
          <p className="font-medium text-gray-900">{row.service?.name}</p>
          {row.service?.category && <p className="text-xs text-gray-400">{row.service.category}</p>}
        </div>
      ),
    },
    ...(isAdmin ? [
      {
        key: 'client_assignee',
        title: 'Client / Assignee',
        render: (row) => row._isTask ? (
          row.assigned_to ? (
            <span className="text-sm text-gray-600">{row.assigned_to.full_name}</span>
          ) : (
            <span className="text-sm text-gray-400">Unassigned</span>
          )
        ) : (
          <div>
            <p className="text-sm text-gray-900">{row.user?.full_name || 'N/A'}</p>
            <p className="text-xs text-gray-500">{row.user?.email}</p>
          </div>
        ),
      },
      {
        key: 'assigned_to',
        title: 'Assigned To',
        render: (row) => row._isTask ? (
          <span className="text-sm text-gray-400">-</span>
        ) : (
          row.assigned_accountant ? (
            <span className="text-sm text-gray-600">{row.assigned_accountant.full_name}</span>
          ) : (
            <span className="text-sm text-gray-400">Unassigned</span>
          )
        ),
      },
    ] : []),
    {
      key: 'status',
      title: 'Status',
      render: (row) => {
        if (row._isTask) {
          const { style, label } = getTaskStatusBadge(row.status);
          return <span className={`text-xs px-2 py-0.5 rounded-full ${style}`}>{label}</span>;
        }
        return <Badge status={row.status} />;
      },
    },
    {
      key: 'priority_invoice',
      title: 'Priority / Invoice',
      render: (row) => {
        if (row._isTask) {
          const priorityStyles = {
            urgent: 'bg-red-100 text-red-700',
            high: 'bg-orange-100 text-orange-700',
            normal: 'bg-blue-100 text-blue-700',
            low: 'bg-gray-100 text-gray-600',
          };
          return (
            <span className={`text-xs px-2 py-0.5 rounded-full capitalize ${priorityStyles[row.priority] || priorityStyles.normal}`}>
              {row.priority}
            </span>
          );
        }
        return (
          <div className="text-sm">
            {row.invoice_raised ? (
              row.invoice_paid ? (
                <span className="text-green-600">Paid</span>
              ) : (
                <span className="text-orange-600">Pending</span>
              )
            ) : (
              <span className="text-gray-400">Not Raised</span>
            )}
          </div>
        );
      },
    },
    {
      key: 'date',
      title: 'Date',
      render: (row) => {
        if (row._isTask && row.due_date) {
          const isOverdue = new Date(row.due_date) < new Date() && row.status !== 'completed';
          return (
            <span className={`text-sm ${isOverdue ? 'text-red-600 font-medium' : 'text-gray-500'}`}>
              Due: {new Date(row.due_date).toLocaleDateString()}
            </span>
          );
        }
        if (row._isTask) return <span className="text-sm text-gray-400">-</span>;
        return (
          <span className="text-sm text-gray-500">
            {new Date(row.created_at).toLocaleDateString()}
          </span>
        );
      },
    },
    {
      key: 'actions',
      title: '',
      render: (row) => row._isTask ? (
        <Button variant="secondary" size="sm" onClick={() => handleEditTask(row)}>
          Edit
        </Button>
      ) : (
        <Link to={`/requests/${row.id}`}>
          <Button variant="secondary" size="sm">
            View
          </Button>
        </Link>
      ),
    },
  ];

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'pending', label: 'Pending' },
    { value: 'assigned', label: 'Assigned' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'query_raised', label: 'Query Raised' },
    { value: 'review', label: 'Under Review' },
    { value: 'completed', label: 'Completed' },
    { value: 'cancelled', label: 'Cancelled' },
  ];

  const invoiceStatusOptions = [
    { value: '', label: 'All Invoice Status' },
    { value: 'not_raised', label: 'Not Raised' },
    { value: 'pending', label: 'Pending Payment' },
    { value: 'paid', label: 'Paid' },
  ];

  const serviceOptions = [
    { value: '', label: 'All Services' },
    ...services.map((s) => ({ value: s.id.toString(), label: s.name })),
  ];

  const accountantOptions = [
    { value: '', label: 'All Accountants' },
    ...accountants.map((a) => ({ value: a.id, label: a.full_name || `${a.first_name} ${a.last_name}` })),
  ];

  const clientOptions = [
    { value: '', label: 'All Clients' },
    ...clients.map((c) => ({ value: c.id, label: c.full_name || `${c.first_name || ''} ${c.last_name || ''}`.trim() || c.email })),
  ];

  // Tasks to pass to kanban board (filtered by type)
  const kanbanTasks = (isStaff && typeFilter !== 'requests') ? tasks : [];
  const kanbanRequests = typeFilter !== 'tasks' ? requests : [];

  return (
    <DashboardLayout title="Service Requests">
      <div className="space-y-6">
        <Card>
          <div className="flex items-start justify-between mb-4">
            <CardHeader
              title={isAdmin ? 'Work Items' : 'My Service Requests'}
              subtitle={isAdmin ? 'Manage service requests and tasks' : 'Track your service requests'}
            />
            <div className="flex items-center gap-3">
              {isStaff && (
                <Button icon={PlusIcon} size="sm" onClick={handleOpenTaskModal}>
                  Create Task
                </Button>
              )}
              <ViewToggle currentView={currentView} onChange={handleViewChange} />
            </div>
          </div>

          {/* Filters */}
          <div className="mb-4 space-y-3">
            <div className="flex flex-wrap gap-3 items-center">
              {isStaff && (
                <Select
                  options={[
                    { value: 'all', label: 'All Items' },
                    { value: 'requests', label: 'Requests Only' },
                    { value: 'tasks', label: 'Tasks Only' },
                  ]}
                  value={typeFilter}
                  onChange={(e) => {
                    setTypeFilter(e.target.value);
                    updateSearchParams({ type: e.target.value === 'all' ? '' : e.target.value });
                  }}
                  className="w-36"
                />
              )}
              {typeFilter !== 'tasks' && (
                <>
                  <Select
                    options={statusOptions}
                    value={statusFilter}
                    onChange={handleStatusFilterChange}
                    className="w-40"
                  />
                  <Select
                    options={serviceOptions}
                    value={serviceFilter}
                    onChange={handleServiceFilterChange}
                    className="w-44"
                  />
                  <Select
                    options={invoiceStatusOptions}
                    value={invoiceStatusFilter}
                    onChange={handleInvoiceStatusFilterChange}
                    className="w-44"
                  />
                </>
              )}
              {isSuperAdmin && companies.length > 0 && typeFilter !== 'tasks' && (
                <Select
                  options={[
                    { value: '', label: 'All Companies' },
                    ...companies.map((c) => ({ value: c.id, label: c.name })),
                  ]}
                  value={companyFilter}
                  onChange={handleCompanyFilterChange}
                  className="w-48"
                />
              )}
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              >
                {showAdvancedFilters ? 'Hide Filters' : 'More Filters'}
              </Button>
              {hasActiveFilters && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={clearAllFilters}
                  className="text-red-600 hover:text-red-700"
                >
                  Clear All
                </Button>
              )}
            </div>

            {showAdvancedFilters && (
              <div className="flex flex-wrap gap-3 items-end p-3 bg-gray-50 rounded-lg">
                {isAdmin && clients.length > 0 && typeFilter !== 'tasks' && (
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Client</label>
                    <Select
                      options={clientOptions}
                      value={clientFilter}
                      onChange={handleClientFilterChange}
                      className="w-48"
                    />
                  </div>
                )}
                {isAdmin && accountants.length > 0 && (
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Accountant / Assignee</label>
                    <Select
                      options={accountantOptions}
                      value={accountantFilter}
                      onChange={handleAccountantFilterChange}
                      className="w-44"
                    />
                  </div>
                )}
                {typeFilter !== 'tasks' && (
                  <>
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">Date From</label>
                      <input
                        type="date"
                        value={dateFrom}
                        onChange={handleDateFromChange}
                        className="w-40 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">Date To</label>
                      <input
                        type="date"
                        value={dateTo}
                        onChange={handleDateToChange}
                        className="w-40 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">Search (Client / Xero ID)</label>
                      <input
                        type="text"
                        value={searchTerm}
                        onChange={handleSearchChange}
                        onKeyDown={handleSearchSubmit}
                        placeholder="Press Enter to search..."
                        className="w-52 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Content */}
          {currentView === 'board' ? (
            <KanbanBoard
              requests={kanbanRequests}
              tasks={kanbanTasks}
              onStatusChange={handleKanbanStatusChange}
              onTaskStatusChange={handleTaskStatusChange}
              onTaskClick={handleEditTask}
              isLoading={isLoading}
            />
          ) : currentView === 'workflow' ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-lg font-medium mb-2">Workflow View</p>
              <p className="text-sm">
                The workflow visualization is available on individual request details.
              </p>
              <p className="text-sm mt-1">
                Click on a request to see its workflow progress.
              </p>
            </div>
          ) : (
            <DataTable
              columns={isStaff ? unifiedColumns : unifiedColumns.filter(c => c.key !== 'type')}
              data={getUnifiedData()}
              pagination={typeFilter !== 'tasks' ? pagination : null}
              onPageChange={typeFilter !== 'tasks' ? fetchRequests : undefined}
              loading={isLoading || isLoadingTasks}
              emptyMessage="No work items found"
            />
          )}
        </Card>
      </div>

      {/* Task Modal (Create / Edit) */}
      {isStaff && (
        <Modal
          isOpen={isTaskModalOpen}
          onClose={() => setIsTaskModalOpen(false)}
          title={editingTask ? 'Edit Task' : 'Create Task'}
        >
          <form onSubmit={handleTaskSubmit} className="space-y-4">
            <Input
              label="Title"
              value={taskFormData.title}
              onChange={(e) => setTaskFormData({ ...taskFormData, title: e.target.value })}
              placeholder="Task title"
              required
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={taskFormData.description}
                onChange={(e) => setTaskFormData({ ...taskFormData, description: e.target.value })}
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
                  ...accountants.map((a) => ({ value: a.id, label: a.full_name || `${a.first_name} ${a.last_name}` })),
                ]}
                value={taskFormData.assigned_to_id}
                onChange={(e) => setTaskFormData({ ...taskFormData, assigned_to_id: e.target.value })}
                disabled={!isAdmin && taskFormData.assigned_to_id === user?.id}
              />

              <Select
                label="Priority"
                options={[
                  { value: 'low', label: 'Low' },
                  { value: 'normal', label: 'Normal' },
                  { value: 'high', label: 'High' },
                  { value: 'urgent', label: 'Urgent' },
                ]}
                value={taskFormData.priority}
                onChange={(e) => setTaskFormData({ ...taskFormData, priority: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Due Date"
                type="date"
                value={taskFormData.due_date}
                onChange={(e) => setTaskFormData({ ...taskFormData, due_date: e.target.value })}
              />

              <Input
                label="Estimated Hours"
                type="number"
                min="0"
                step="0.5"
                value={taskFormData.estimated_minutes}
                onChange={(e) => setTaskFormData({ ...taskFormData, estimated_minutes: e.target.value })}
                placeholder="e.g., 2"
              />
            </div>

            <div className="flex justify-between pt-4">
              <div>
                {editingTask && isAdmin && (
                  <Button variant="danger" type="button" onClick={handleDeleteTask}>
                    Delete
                  </Button>
                )}
              </div>
              <div className="flex gap-3">
                <Button variant="secondary" type="button" onClick={() => setIsTaskModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" loading={isTaskSubmitting}>
                  {editingTask ? 'Update Task' : 'Create Task'}
                </Button>
              </div>
            </div>
          </form>
        </Modal>
      )}
    </DashboardLayout>
  );
}
