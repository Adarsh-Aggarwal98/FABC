import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  ClockIcon,
  CurrencyDollarIcon,
  DocumentTextIcon,
  UsersIcon,
  ChatBubbleLeftRightIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  FunnelIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader, StatCard } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Input, { Select } from '../../components/common/Input';
import { analyticsAPI, companiesAPI, userAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import useCompanyStore from '../../store/companyStore';

export default function AdminAnalytics() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { formatPrice } = useCompanyStore();
  const [data, setData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [companies, setCompanies] = useState([]);
  const [clients, setClients] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [selectedClientId, setSelectedClientId] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'senior_accountant';
  const isSuperAdmin = user?.role === 'super_admin';

  useEffect(() => {
    if (!isAdmin) {
      navigate('/dashboard');
      return;
    }
    if (isSuperAdmin) {
      fetchCompanies();
    }
    fetchClients();
  }, [isAdmin, isSuperAdmin]);

  useEffect(() => {
    fetchAnalytics();
  }, [selectedCompanyId, selectedClientId, dateFrom, dateTo]);

  const fetchCompanies = async () => {
    try {
      const response = await companiesAPI.list({ active_only: true });
      setCompanies(response.data.companies || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch companies');
    }
  };

  const fetchClients = async () => {
    try {
      const params = { role: 'user', per_page: 500 };
      if (isSuperAdmin && selectedCompanyId) {
        params.company_id = selectedCompanyId;
      }
      const response = await userAPI.list(params);
      setClients(response.data.data?.users || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch clients');
    }
  };

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const params = {};
      if (isSuperAdmin && selectedCompanyId) {
        params.company_id = selectedCompanyId;
      }
      if (selectedClientId) {
        params.client_id = selectedClientId;
      }
      if (dateFrom) {
        params.date_from = dateFrom;
      }
      if (dateTo) {
        params.date_to = dateTo;
      }

      const response = await analyticsAPI.getAdminDashboard(params);
      setData(response.data.data || null);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load analytics data');
    } finally {
      setIsLoading(false);
    }
  };

  const formatHours = (hours) => {
    if (!hours) return '0h';
    if (hours < 1) {
      const minutes = Math.round(hours * 60);
      return `${minutes}m`;
    }
    const wholeHours = Math.floor(hours);
    const minutes = Math.round((hours - wholeHours) * 60);
    return minutes > 0 ? `${wholeHours}h ${minutes}m` : `${wholeHours}h`;
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-amber-500',
      assigned: 'bg-blue-500',
      in_progress: 'bg-indigo-500',
      processing: 'bg-purple-500',
      query_raised: 'bg-orange-500',
      completed: 'bg-green-500',
      invoice_raised: 'bg-teal-500',
      accountant_review_pending: 'bg-cyan-500',
    };
    return colors[status] || 'bg-gray-500';
  };

  const clearFilters = () => {
    setSelectedClientId('');
    setDateFrom('');
    setDateTo('');
  };

  if (isLoading) {
    return (
      <DashboardLayout title="Admin Analytics">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  const summary = data?.summary || {};
  const clientsData = data?.clients || [];
  const requestsDetail = data?.requests_detail || [];

  // Calculate max for status bar chart
  const statusEntries = Object.entries(summary.status_breakdown || {});
  const maxStatusCount = Math.max(...statusEntries.map(([, count]) => count), 1);

  return (
    <DashboardLayout title="Admin Analytics">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <Button
            variant="ghost"
            icon={ArrowLeftIcon}
            onClick={() => navigate('/dashboard')}
          >
            Back to Dashboard
          </Button>
          <div className="flex flex-wrap items-center gap-3">
            {/* Company Filter for Super Admin */}
            {isSuperAdmin && companies.length > 0 && (
              <Select
                options={[
                  { value: '', label: 'All Companies' },
                  ...companies.map((c) => ({ value: c.id, label: c.name })),
                ]}
                value={selectedCompanyId}
                onChange={(e) => {
                  setSelectedCompanyId(e.target.value);
                  setSelectedClientId('');
                  fetchClients();
                }}
                className="w-48"
              />
            )}
            {/* Client Filter */}
            <Select
              options={[
                { value: '', label: 'All Clients' },
                ...clients.map((c) => ({
                  value: c.id,
                  label: c.full_name || c.email,
                })),
              ]}
              value={selectedClientId}
              onChange={(e) => setSelectedClientId(e.target.value)}
              className="w-48"
            />
            {/* Date Range Filters */}
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => setDateFrom(e.target.value)}
              placeholder="From"
              className="w-36"
            />
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => setDateTo(e.target.value)}
              placeholder="To"
              className="w-36"
            />
            {(selectedClientId || dateFrom || dateTo) && (
              <Button variant="ghost" size="sm" onClick={clearFilters}>
                Clear Filters
              </Button>
            )}
          </div>
        </div>

        {/* Summary Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <StatCard
            title="Total Requests"
            value={summary.total_requests || 0}
            icon={DocumentTextIcon}
            color="blue"
          />
          <StatCard
            title="Pending"
            value={summary.status_breakdown?.pending || 0}
            icon={ExclamationCircleIcon}
            color="amber"
          />
          <StatCard
            title="Completed"
            value={summary.status_breakdown?.completed || 0}
            icon={CheckCircleIcon}
            color="green"
          />
          <StatCard
            title="Total Revenue"
            value={formatPrice(summary.total_revenue || 0)}
            icon={CurrencyDollarIcon}
            color="emerald"
          />
          <StatCard
            title="Time Spent"
            value={formatHours(summary.total_time_spent_hours || 0)}
            icon={ClockIcon}
            color="purple"
          />
          <StatCard
            title="Queries Raised"
            value={summary.total_queries || 0}
            icon={ChatBubbleLeftRightIcon}
            color="orange"
          />
        </div>

        {/* Status Breakdown Chart */}
        <Card>
          <CardHeader
            title="Request Status Breakdown"
            subtitle="Distribution of requests by current status"
          />
          {statusEntries.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <DocumentTextIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p>No request data available</p>
            </div>
          ) : (
            <div className="space-y-3">
              {statusEntries.map(([status, count]) => (
                <div key={status} className="flex items-center gap-4">
                  <div className="w-40">
                    <span className="text-sm font-medium text-gray-700 capitalize">
                      {status.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <div className="flex-1 bg-gray-100 rounded-full h-6 overflow-hidden">
                        <div
                          className={`h-full ${getStatusColor(status)} rounded-full transition-all duration-500`}
                          style={{
                            width: `${(count / maxStatusCount) * 100}%`,
                          }}
                        />
                      </div>
                      <span className="text-sm font-semibold text-gray-700 w-12 text-right">
                        {count}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Client Analytics Table */}
        <Card>
          <CardHeader
            title="Client Analytics"
            subtitle="Performance metrics per client"
            icon={UserGroupIcon}
          />
          {clientsData.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <UsersIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p>No client data available</p>
            </div>
          ) : (
            <div className="overflow-x-auto -mx-6">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Client
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Entities
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Requests
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Revenue
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Time Spent
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Queries
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {clientsData.map((client) => (
                    <tr key={client.client_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {client.client_name}
                          </div>
                          <div className="text-xs text-gray-500">
                            {client.client_email}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 text-right">
                        {client.entity_count}
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-gray-900 text-right">
                        {client.request_count}
                      </td>
                      <td className="px-6 py-4 text-sm text-green-600 font-medium text-right">
                        {formatPrice(client.total_revenue)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 text-right">
                        {formatHours(client.total_time_spent_hours)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 text-right">
                        {client.query_count}
                      </td>
                      <td className="px-6 py-4 text-center">
                        <Button
                          variant="secondary"
                          size="sm"
                          icon={FunnelIcon}
                          onClick={() => setSelectedClientId(client.client_id)}
                        >
                          Filter
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Request Time Analysis Table */}
        <Card>
          <CardHeader
            title="Request Time Analysis"
            subtitle="Per-request breakdown with time spent and queries"
          />
          {requestsDetail.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <DocumentTextIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p>No request data available</p>
            </div>
          ) : (
            <div className="overflow-x-auto -mx-6">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Request #
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Service
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Client
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Invoice
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Time
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Queries
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {requestsDetail.map((req) => (
                    <tr key={req.request_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <Link
                          to={`/requests/${req.request_id}`}
                          className="text-sm font-medium text-primary-600 hover:text-primary-800"
                        >
                          {req.request_number}
                        </Link>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {req.service_name}
                      </td>
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm text-gray-900">{req.client_name}</div>
                          {req.client_entity_name && (
                            <div className="text-xs text-gray-500">
                              {req.client_entity_name}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <Badge status={req.status} />
                      </td>
                      <td className="px-6 py-4 text-right">
                        {req.invoice_amount ? (
                          <div>
                            <span className={`text-sm font-medium ${req.invoice_paid ? 'text-green-600' : 'text-gray-900'}`}>
                              {formatPrice(req.invoice_amount)}
                            </span>
                            {req.invoice_paid && (
                              <span className="ml-1 text-xs text-green-500">(Paid)</span>
                            )}
                          </div>
                        ) : (
                          <span className="text-sm text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 text-right">
                        {formatHours(req.time_spent_hours)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600 text-right">
                        {req.query_count}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {req.created_at
                          ? new Date(req.created_at).toLocaleDateString()
                          : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
          <p className="font-medium text-blue-800 mb-2">About Admin Analytics</p>
          <ul className="text-blue-700 space-y-1">
            <li>View comprehensive metrics for client activity, revenue, and time tracking</li>
            <li>Filter by client, date range, or company (super admin) to drill down into specific data</li>
            <li>Revenue shows only paid invoices; Time includes both labor hours and job note entries</li>
            <li>Click "Filter" on any client row to see detailed data for that client only</li>
          </ul>
        </div>
      </div>
    </DashboardLayout>
  );
}
