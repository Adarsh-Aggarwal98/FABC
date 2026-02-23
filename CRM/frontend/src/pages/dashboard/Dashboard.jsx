import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  UsersIcon,
  FolderIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  BuildingOfficeIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { StatCard, CardHeader } from '../../components/common/Card';
import Badge from '../../components/common/Badge';
import Button from '../../components/common/Button';
import { Select } from '../../components/common/Input';
import useAuthStore from '../../store/authStore';
import { requestsAPI, companiesAPI } from '../../services/api';

export default function Dashboard() {
  const { user } = useAuthStore();
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    processing: 0,
    completed: 0,
    queries: 0,
  });
  const [invoiceStats, setInvoiceStats] = useState({
    raised: 0,
    paid: 0,
    total_revenue: 0,
    pending_payments: 0,
  });
  const [recentRequests, setRecentRequests] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState('');

  const isSuperAdmin = user?.role === 'super_admin';

  useEffect(() => {
    if (isSuperAdmin) {
      fetchCompanies();
    }
  }, [isSuperAdmin]);

  useEffect(() => {
    fetchDashboardData();
  }, [selectedCompanyId]);

  const fetchCompanies = async () => {
    try {
      const response = await companiesAPI.list({ active_only: true });
      setCompanies(response.data.companies || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch companies');
    }
  };

  const fetchDashboardData = async () => {
    setIsLoading(true);
    try {
      // Fetch metrics from the new endpoint
      const params = {};
      if (isSuperAdmin && selectedCompanyId) {
        params.company_id = selectedCompanyId;
      }
      const metricsResponse = await requestsAPI.getDashboardMetrics(params);
      const metrics = metricsResponse.data.data.metrics;

      setStats({
        total: metrics.requests.total,
        pending: metrics.requests.pending,
        processing: metrics.requests.processing,
        completed: metrics.requests.completed,
        queries: metrics.requests.queries,
      });

      setInvoiceStats(metrics.invoices);

      // Fetch recent requests
      const requestParams = { per_page: 5 };
      if (isSuperAdmin && selectedCompanyId) {
        requestParams.company_id = selectedCompanyId;
      }
      const response = await requestsAPI.list(requestParams);
      const requests = response.data.data.requests || [];
      setRecentRequests(requests);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'senior_accountant';
  const isAccountant = user?.role === 'accountant' || user?.role === 'senior_accountant';
  const canViewRevenue = user?.role === 'super_admin' || user?.role === 'admin'; // Only admin roles can see revenue/invoice data
  const isClient = user?.role === 'user' || user?.role === 'external_accountant'; // Clients and external accountants

  return (
    <DashboardLayout title="Dashboard">
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="relative overflow-hidden bg-gradient-to-r from-primary-600 via-primary-500 to-indigo-600 rounded-2xl p-8 text-white shadow-xl shadow-primary-500/20">
          {/* Decorative elements */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />

          <div className="relative flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold">
                {getGreeting()}, {user?.first_name || 'there'}!
              </h2>
              <p className="text-primary-100 mt-2 max-w-xl">
                {isAdmin
                  ? 'Here\'s an overview of your practice. Manage requests, track progress, and stay on top of your tasks.'
                  : isAccountant
                  ? 'Here are your assigned tasks. Complete requests efficiently and communicate with clients.'
                  : 'Here\'s the status of your requests. Track progress and respond to any queries from your accountant.'}
              </p>
            </div>

            {/* Company Filter for Super Admin */}
            {isSuperAdmin && companies.length > 0 && (
              <div className="flex items-center gap-2 bg-white/10 rounded-lg px-3 py-2">
                <BuildingOfficeIcon className="h-5 w-5 text-white/70" />
                <select
                  value={selectedCompanyId}
                  onChange={(e) => setSelectedCompanyId(e.target.value)}
                  className="bg-transparent text-white border-none focus:ring-0 text-sm font-medium cursor-pointer"
                >
                  <option value="" className="text-gray-900">All Companies</option>
                  {companies.map((company) => (
                    <option key={company.id} value={company.id} className="text-gray-900">
                      {company.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Stats Grid - Different view for clients vs staff */}
        {isClient ? (
          // Client/External Accountant view - only relevant stats
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <StatCard
              title="My Requests"
              value={stats.total}
              icon={FolderIcon}
              color="indigo"
            />
            <StatCard
              title="Queries to Answer"
              value={stats.queries}
              icon={ExclamationTriangleIcon}
              color="orange"
            />
            <StatCard
              title="Pending Payments"
              value={`$${invoiceStats.pending_payments?.toLocaleString() || 0}`}
              icon={CurrencyDollarIcon}
              color="amber"
            />
          </div>
        ) : (
          // Staff view - full stats
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Total Requests"
              value={stats.total}
              icon={FolderIcon}
              color="indigo"
            />
            <StatCard
              title="Pending"
              value={stats.pending}
              icon={ClockIcon}
              color="orange"
            />
            <StatCard
              title="Processing"
              value={stats.processing}
              icon={CurrencyDollarIcon}
              color="purple"
            />
            <StatCard
              title="Completed"
              value={stats.completed}
              icon={CheckCircleIcon}
              color="green"
            />
          </div>
        )}

        {/* Invoice Stats for Admin/Super Admin only (not accountants) */}
        {canViewRevenue && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              title="Invoices Raised"
              value={invoiceStats.raised}
              icon={FolderIcon}
              color="blue"
            />
            <StatCard
              title="Invoices Paid"
              value={invoiceStats.paid}
              icon={CheckCircleIcon}
              color="green"
            />
            <StatCard
              title="Total Revenue"
              value={`$${invoiceStats.total_revenue.toLocaleString()}`}
              icon={CurrencyDollarIcon}
              color="emerald"
            />
            <StatCard
              title="Pending Payments"
              value={`$${invoiceStats.pending_payments.toLocaleString()}`}
              icon={ClockIcon}
              color="amber"
            />
          </div>
        )}

        {/* Queries Alert */}
        {stats.queries > 0 && (
          <div className="bg-gradient-to-r from-orange-50 to-amber-50 border border-orange-200/50 rounded-xl p-5 flex items-center shadow-sm">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-amber-500 flex items-center justify-center mr-4 shadow-lg shadow-orange-500/20">
              <ExclamationTriangleIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-orange-800">
                {stats.queries} request(s) have queries that need {isClient ? 'your response' : 'attention'}
              </p>
              <p className="text-sm text-orange-600 mt-0.5">
                {isClient ? 'Your accountant needs more information' : 'Please respond to continue processing'}
              </p>
            </div>
            <Link
              to="/requests?status=query_raised"
              className="px-4 py-2 bg-orange-600 text-white rounded-lg text-sm font-medium hover:bg-orange-700 transition-colors shadow-lg shadow-orange-500/20"
            >
              {isClient ? 'Respond Now' : 'View queries'}
            </Link>
          </div>
        )}

        {/* Pending Payments Alert for Clients */}
        {isClient && invoiceStats.pending_payments > 0 && (
          <div className="bg-gradient-to-r from-amber-50 to-yellow-50 border border-amber-200/50 rounded-xl p-5 flex items-center shadow-sm">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-400 to-yellow-500 flex items-center justify-center mr-4 shadow-lg shadow-amber-500/20">
              <CurrencyDollarIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-amber-800">
                You have ${invoiceStats.pending_payments?.toLocaleString() || 0} in pending payments
              </p>
              <p className="text-sm text-amber-600 mt-0.5">Please complete payment to finalize your requests</p>
            </div>
            <Link
              to="/requests?invoice_status=pending"
              className="px-4 py-2 bg-amber-600 text-white rounded-lg text-sm font-medium hover:bg-amber-700 transition-colors shadow-lg shadow-amber-500/20"
            >
              View Invoices
            </Link>
          </div>
        )}

        {/* Recent Requests */}
        <Card>
          <CardHeader
            title="Recent Requests"
            action={
              <Link to="/requests">
                <Button variant="secondary" size="sm">
                  View All
                </Button>
              </Link>
            }
          />

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
            </div>
          ) : recentRequests.length === 0 ? (
            <div className="text-center py-8">
              <FolderIcon className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No requests yet</p>
              {!isAdmin && !isAccountant && (
                <Link to="/services/new">
                  <Button className="mt-4">Request a Service</Button>
                </Link>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto -mx-6">
              <table className="min-w-full">
                <thead className="table-header">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Service
                    </th>
                    {isAdmin && (
                      <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                        Client
                      </th>
                    )}
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {recentRequests.map((request) => (
                    <tr key={request.id} className="table-row">
                      <td className="px-6 py-4">
                        <p className="font-medium text-gray-900">
                          {request.service?.name}
                        </p>
                      </td>
                      {isAdmin && (
                        <td className="px-6 py-4 text-sm text-gray-600">
                          {request.user?.full_name || request.user?.email}
                        </td>
                      )}
                      <td className="px-6 py-4">
                        <Badge status={request.status} />
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {new Date(request.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <Link
                          to={`/requests/${request.id}`}
                          className="text-primary-600 hover:text-primary-700 text-sm font-medium hover:underline"
                        >
                          View Details
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {/* Quick Actions */}
        {!isAdmin && !isAccountant && (
          <Card>
            <CardHeader title="Quick Actions" />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Link
                to="/services/new"
                className="group p-6 border border-gray-200 rounded-xl hover:border-primary-300 hover:shadow-lg hover:shadow-primary-100/50 transition-all duration-300 bg-gradient-to-br from-white to-gray-50"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg shadow-primary-500/20">
                  <FolderIcon className="h-6 w-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 group-hover:text-primary-700 transition-colors">Request a Service</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Select services, fill details & upload documents
                </p>
              </Link>
              <Link
                to="/requests"
                className="group p-6 border border-gray-200 rounded-xl hover:border-indigo-300 hover:shadow-lg hover:shadow-indigo-100/50 transition-all duration-300 bg-gradient-to-br from-white to-gray-50"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-600 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg shadow-indigo-500/20">
                  <ClockIcon className="h-6 w-6 text-white" />
                </div>
                <h3 className="font-semibold text-gray-900 group-hover:text-indigo-700 transition-colors">View My Requests</h3>
                <p className="text-sm text-gray-500 mt-1">
                  Check status of your service requests
                </p>
              </Link>
            </div>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
