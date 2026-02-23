import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  ClockIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  CalendarDaysIcon,
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader, StatCard } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import { Select } from '../../components/common/Input';
import { analyticsAPI, companiesAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import useCompanyStore from '../../store/companyStore';

export default function JobAnalytics() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { formatPrice, fetchCompany } = useCompanyStore();
  const [stateDurations, setStateDurations] = useState([]);
  const [overdueRequests, setOverdueRequests] = useState([]);
  const [deadlineSummary, setDeadlineSummary] = useState(null);
  const [revenueCostData, setRevenueCostData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [dateRange, setDateRange] = useState('30'); // Days
  const [costGroupBy, setCostGroupBy] = useState('service');

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
    fetchAnalytics();
  }, [isAdmin, isSuperAdmin, selectedCompanyId, dateRange, costGroupBy]);

  const fetchCompanies = async () => {
    try {
      const response = await companiesAPI.list({ active_only: true });
      setCompanies(response.data.companies || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch companies');
    }
  };

  const fetchAnalytics = async () => {
    setIsLoading(true);
    try {
      const params = { days: dateRange };
      if (isSuperAdmin && selectedCompanyId) {
        params.company_id = selectedCompanyId;
      }

      const [durationsRes, overdueRes, deadlineRes, revenueCostRes] = await Promise.all([
        analyticsAPI.getStateDurations(params),
        analyticsAPI.getOverdueRequests(params),
        analyticsAPI.getDeadlineSummary(params),
        analyticsAPI.getRevenueCost({ ...params, group_by: costGroupBy }),
      ]);

      setStateDurations(durationsRes.data.data?.state_durations || []);
      setOverdueRequests(overdueRes.data.data?.overdue_requests || []);
      setDeadlineSummary(deadlineRes.data.data || null);
      setRevenueCostData(revenueCostRes.data.data || null);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load analytics data');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDuration = (hours) => {
    if (!hours) return '0h';
    if (hours < 24) return `${Math.round(hours)}h`;
    const days = Math.floor(hours / 24);
    const remainingHours = Math.round(hours % 24);
    return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-amber-100 text-amber-800',
      assigned: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-indigo-100 text-indigo-800',
      processing: 'bg-purple-100 text-purple-800',
      query_raised: 'bg-orange-100 text-orange-800',
      completed: 'bg-green-100 text-green-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (isLoading) {
    return (
      <DashboardLayout title="Job Analytics">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Job Analytics">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            icon={ArrowLeftIcon}
            onClick={() => navigate('/dashboard')}
          >
            Back to Dashboard
          </Button>
          <div className="flex items-center gap-4">
            {/* Company Filter for Super Admin */}
            {isSuperAdmin && companies.length > 0 && (
              <Select
                options={[
                  { value: '', label: 'All Companies' },
                  ...companies.map((c) => ({ value: c.id, label: c.name })),
                ]}
                value={selectedCompanyId}
                onChange={(e) => setSelectedCompanyId(e.target.value)}
                className="w-48"
              />
            )}
            {/* Date Range Filter */}
            <Select
              options={[
                { value: '7', label: 'Last 7 days' },
                { value: '30', label: 'Last 30 days' },
                { value: '90', label: 'Last 90 days' },
                { value: '365', label: 'Last year' },
              ]}
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="w-40"
            />
          </div>
        </div>

        {/* Deadline Summary Stats */}
        {deadlineSummary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatCard
              title="Total with Deadlines"
              value={deadlineSummary.total_with_deadline || 0}
              icon={CalendarDaysIcon}
              color="blue"
            />
            <StatCard
              title="On Track"
              value={deadlineSummary.on_track || 0}
              icon={ClockIcon}
              color="green"
            />
            <StatCard
              title="Due Soon"
              value={deadlineSummary.due_soon || 0}
              icon={ExclamationTriangleIcon}
              color="amber"
            />
            <StatCard
              title="Overdue"
              value={deadlineSummary.overdue || 0}
              icon={ExclamationTriangleIcon}
              color="red"
            />
          </div>
        )}

        {/* State Duration Analytics */}
        <Card>
          <CardHeader
            title="Average Time in Each State"
            subtitle="How long jobs typically spend in each status"
          />
          {stateDurations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <ChartBarIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p>No state transition data available yet</p>
              <p className="text-sm mt-1">Data will appear once jobs start moving through different states</p>
            </div>
          ) : (
            <div className="space-y-4">
              {stateDurations.map((item) => (
                <div key={item.state} className="flex items-center gap-4">
                  <div className="w-32">
                    <span className={`inline-flex px-2.5 py-1 rounded-full text-xs font-medium ${getStatusColor(item.state)}`}>
                      {item.state.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden">
                        <div
                          className="h-full bg-primary-500 rounded-full transition-all duration-500"
                          style={{
                            width: `${Math.min(100, (item.avg_hours / 168) * 100)}%`, // Scale to max 1 week
                          }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-700 w-20 text-right">
                        {formatDuration(item.avg_hours)}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{item.count || 0} transitions</span>
                      <span>Min: {formatDuration(item.min_hours)} / Max: {formatDuration(item.max_hours)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Overdue Requests */}
        <Card>
          <CardHeader
            title="Overdue Requests"
            subtitle="Requests that have passed their deadline"
          />
          {overdueRequests.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <ExclamationTriangleIcon className="h-12 w-12 mx-auto mb-3 text-green-300" />
              <p className="text-green-600 font-medium">No overdue requests!</p>
              <p className="text-sm mt-1">All jobs with deadlines are on track</p>
            </div>
          ) : (
            <div className="overflow-x-auto -mx-6">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Service
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Client
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Deadline
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Days Overdue
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Assigned To
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {overdueRequests.map((request) => {
                    const daysOverdue = Math.ceil(
                      (new Date() - new Date(request.deadline_date)) / (1000 * 60 * 60 * 24)
                    );
                    return (
                      <tr key={request.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">
                          {request.service?.name}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {request.user?.full_name || request.user?.email}
                        </td>
                        <td className="px-6 py-4">
                          <Badge status={request.status} />
                        </td>
                        <td className="px-6 py-4 text-sm text-red-600 font-medium">
                          {new Date(request.deadline_date).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4">
                          <span className="inline-flex px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
                            {daysOverdue} day{daysOverdue !== 1 ? 's' : ''}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {request.assigned_accountant?.full_name || 'Unassigned'}
                        </td>
                        <td className="px-6 py-4">
                          <Button
                            variant="secondary"
                            size="sm"
                            onClick={() => navigate(`/requests/${request.id}`)}
                          >
                            View
                          </Button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Revenue vs Cost Analytics */}
        <Card>
          <CardHeader
            title="Revenue vs Cost Analysis"
            subtitle="Compare revenue earned against costs incurred"
            action={
              <Select
                options={[
                  { value: 'service', label: 'Group by Service' },
                  { value: 'category', label: 'Group by Category' },
                  { value: 'month', label: 'Group by Month' },
                  { value: 'accountant', label: 'Group by Accountant' },
                ]}
                value={costGroupBy}
                onChange={(e) => setCostGroupBy(e.target.value)}
                className="w-44"
              />
            }
          />

          {/* Summary Stats */}
          {revenueCostData?.summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-sm text-green-600 font-medium">Total Revenue</p>
                <p className="text-2xl font-bold text-green-700">
                  {formatPrice(revenueCostData.summary.total_revenue || 0)}
                </p>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <p className="text-sm text-red-600 font-medium">Total Cost</p>
                <p className="text-2xl font-bold text-red-700">
                  {formatPrice(revenueCostData.summary.total_cost || 0)}
                </p>
              </div>
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-sm text-blue-600 font-medium">Net Profit</p>
                <p className={`text-2xl font-bold ${(revenueCostData.summary.profit || 0) >= 0 ? 'text-blue-700' : 'text-red-700'}`}>
                  {formatPrice(revenueCostData.summary.profit || 0)}
                </p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <p className="text-sm text-purple-600 font-medium">Profit Margin</p>
                <p className="text-2xl font-bold text-purple-700 flex items-center gap-2">
                  {(revenueCostData.summary.profit_margin || 0).toFixed(1)}%
                  {(revenueCostData.summary.profit_margin || 0) >= 0 ? (
                    <ArrowTrendingUpIcon className="h-5 w-5 text-green-500" />
                  ) : (
                    <ArrowTrendingDownIcon className="h-5 w-5 text-red-500" />
                  )}
                </p>
              </div>
            </div>
          )}

          {/* Grouped Breakdown */}
          {revenueCostData?.grouped?.length > 0 ? (
            <div className="overflow-x-auto -mx-6">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      {costGroupBy === 'service' ? 'Service' :
                       costGroupBy === 'category' ? 'Category' :
                       costGroupBy === 'month' ? 'Month' : 'Accountant'}
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Jobs
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Revenue
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Estimated Cost
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Actual Cost
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Profit
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">
                      Margin
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {revenueCostData.grouped.map((item, index) => {
                    const profit = (item.revenue || 0) - (item.actual_cost || item.estimated_cost || 0);
                    const margin = item.revenue > 0 ? (profit / item.revenue * 100) : 0;
                    return (
                      <tr key={index} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">
                          {item.label || item.name || item.month || 'Unknown'}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600 text-right">
                          {item.count || 0}
                        </td>
                        <td className="px-6 py-4 text-sm text-green-600 font-medium text-right">
                          {formatPrice(item.revenue || 0)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 text-right">
                          {formatPrice(item.estimated_cost || 0)}
                        </td>
                        <td className="px-6 py-4 text-sm text-red-600 font-medium text-right">
                          {formatPrice(item.actual_cost || 0)}
                        </td>
                        <td className={`px-6 py-4 text-sm font-medium text-right ${profit >= 0 ? 'text-blue-600' : 'text-red-600'}`}>
                          {formatPrice(profit)}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${
                            margin >= 30 ? 'bg-green-100 text-green-800' :
                            margin >= 15 ? 'bg-yellow-100 text-yellow-800' :
                            margin >= 0 ? 'bg-orange-100 text-orange-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {margin.toFixed(1)}%
                            {margin >= 0 ? (
                              <ArrowTrendingUpIcon className="h-3 w-3" />
                            ) : (
                              <ArrowTrendingDownIcon className="h-3 w-3" />
                            )}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <CurrencyDollarIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p>No revenue or cost data available yet</p>
              <p className="text-sm mt-1">Data will appear once jobs have invoice amounts or costs recorded</p>
            </div>
          )}
        </Card>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
          <p className="font-medium text-blue-800 mb-2">About Job Analytics</p>
          <ul className="text-blue-700 space-y-1">
            <li>State duration data is collected automatically when jobs transition between statuses</li>
            <li>Deadline tracking requires setting a deadline when assigning jobs to accountants</li>
            <li>Cost tracking shows both estimated costs (based on service percentage) and actual costs entered on jobs</li>
            <li>Use these insights to identify bottlenecks, track profitability, and improve workflow efficiency</li>
          </ul>
        </div>
      </div>
    </DashboardLayout>
  );
}
