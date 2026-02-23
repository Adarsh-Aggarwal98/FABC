import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { PlusIcon, BuildingOfficeIcon, UserGroupIcon, EyeIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { Select } from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import { companiesAPI } from '../../services/api';

export default function CompanyList() {
  const navigate = useNavigate();
  const [companies, setCompanies] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [showInactive, setShowInactive] = useState(false);

  // Create form
  const [companyData, setCompanyData] = useState({
    name: '',
    trading_name: '',
    company_type: 'tax_agent',
    abn: '',
    acn: '',
    company_email: '',
    phone: '',
    website: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postcode: '',
    country: 'Australia',
    owner_email: '',
    owner_first_name: '',
    owner_last_name: '',
    owner_phone: '',
    plan_type: 'standard',
    max_users: 10,
    max_clients: 100,
  });
  const [isCreating, setIsCreating] = useState(false);
  const [tempPassword, setTempPassword] = useState(null);

  useEffect(() => {
    fetchCompanies(1);
  }, [searchTerm, showInactive]);

  const fetchCompanies = async (page) => {
    setIsLoading(true);
    try {
      const response = await companiesAPI.list({
        page,
        search: searchTerm || undefined,
        active_only: !showInactive,
      });
      setCompanies(response.data.companies || []);
      setPagination(response.data.pagination);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch companies');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    setIsCreating(true);

    try {
      const response = await companiesAPI.create(companyData);
      toast.success('Company created successfully');

      // Show the temp password if returned
      if (response.data.temp_password) {
        setTempPassword(response.data.temp_password);
      } else {
        setIsCreateModalOpen(false);
        resetForm();
      }

      fetchCompanies(1);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create company');
    } finally {
      setIsCreating(false);
    }
  };

  const resetForm = () => {
    setCompanyData({
      name: '',
      trading_name: '',
      company_type: 'tax_agent',
      abn: '',
      acn: '',
      company_email: '',
      phone: '',
      website: '',
      address_line1: '',
      address_line2: '',
      city: '',
      state: '',
      postcode: '',
      country: 'Australia',
      owner_email: '',
      owner_first_name: '',
      owner_last_name: '',
      owner_phone: '',
      plan_type: 'standard',
      max_users: 10,
      max_clients: 100,
    });
    setTempPassword(null);
  };

  const handleCloseModal = () => {
    setIsCreateModalOpen(false);
    resetForm();
  };

  const handleDelete = async (companyId) => {
    if (!window.confirm('Are you sure you want to deactivate this company?')) return;

    try {
      await companiesAPI.delete(companyId);
      toast.success('Company deactivated');
      fetchCompanies(pagination?.page || 1);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to deactivate company');
    }
  };

  const getCompanyTypeLabel = (type) => {
    const types = {
      tax_agent: 'Tax Agent',
      accountant: 'Accountant',
      bas_agent: 'BAS Agent',
      bookkeeper: 'Bookkeeper',
      auditor: 'Auditor',
      financial_planner: 'Financial Planner',
      mortgage_broker: 'Mortgage Broker',
      other: 'Other',
    };
    return types[type] || type || 'N/A';
  };

  const isPracticeOwnerType = (type) => {
    return ['tax_agent', 'accountant', 'bas_agent', 'bookkeeper'].includes(type);
  };

  const columns = [
    {
      key: 'name',
      title: 'Company',
      render: (row) => (
        <div className="flex items-center">
          <div className="h-10 w-10 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mr-3">
            <BuildingOfficeIcon className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="font-medium text-gray-900">{row.name}</p>
            {row.trading_name && (
              <p className="text-sm text-gray-500">Trading as: {row.trading_name}</p>
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'type',
      title: 'Type',
      render: (row) => (
        <div className="flex flex-col">
          {isPracticeOwnerType(row.company_type) && (
            <span className="text-xs text-gray-500">Practice Owner</span>
          )}
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            isPracticeOwnerType(row.company_type)
              ? 'bg-blue-100 text-blue-800'
              : 'bg-gray-100 text-gray-800'
          }`}>
            {getCompanyTypeLabel(row.company_type)}
          </span>
        </div>
      ),
    },
    {
      key: 'owner',
      title: 'Practice Owner',
      render: (row) => (
        <div>
          <p className="font-medium text-gray-900">{row.owner?.full_name || 'N/A'}</p>
          <p className="text-sm text-gray-500">{row.owner?.email}</p>
        </div>
      ),
    },
    {
      key: 'stats',
      title: 'Users / Clients',
      render: (row) => (
        <div className="flex items-center gap-4">
          <div className="flex items-center text-sm">
            <UserGroupIcon className="h-4 w-4 mr-1 text-gray-400" />
            <span>{row.user_count || 0} users</span>
          </div>
          <div className="flex items-center text-sm">
            <span className="text-gray-400">Clients:</span>
            <span className="ml-1">{row.client_count || 0}</span>
          </div>
        </div>
      ),
    },
    {
      key: 'plan',
      title: 'Plan',
      render: (row) => (
        <Badge status={row.plan_type === 'premium' ? 'success' : row.plan_type === 'enterprise' ? 'info' : 'default'}>
          {row.plan_type?.charAt(0).toUpperCase() + row.plan_type?.slice(1)}
        </Badge>
      ),
    },
    {
      key: 'status',
      title: 'Status',
      render: (row) => (
        <Badge status={row.is_active ? 'active' : 'inactive'}>
          {row.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      title: 'Created',
      render: (row) => (
        <span className="text-sm text-gray-500">
          {new Date(row.created_at).toLocaleDateString()}
        </span>
      ),
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (row) => (
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={EyeIcon}
            onClick={() => navigate(`/companies/${row.id}`)}
          >
            View
          </Button>
          {row.is_active && (
            <Button
              variant="danger"
              size="sm"
              onClick={() => handleDelete(row.id)}
            >
              Deactivate
            </Button>
          )}
        </div>
      ),
    },
  ];

  const planOptions = [
    { value: 'standard', label: 'Standard' },
    { value: 'premium', label: 'Premium' },
    { value: 'enterprise', label: 'Enterprise' },
  ];

  const companyTypeOptions = [
    // Practice Owner Types
    { value: 'tax_agent', label: 'Practice Owner - Tax Agent' },
    { value: 'accountant', label: 'Practice Owner - Accountant' },
    { value: 'bas_agent', label: 'Practice Owner - BAS Agent' },
    { value: 'bookkeeper', label: 'Practice Owner - Bookkeeper' },
    // Other Types
    { value: 'auditor', label: 'Auditor (SMSF/Financial)' },
    { value: 'financial_planner', label: 'Financial Planner' },
    { value: 'mortgage_broker', label: 'Mortgage Broker' },
    { value: 'other', label: 'Other' },
  ];

  const stateOptions = [
    { value: '', label: 'Select State' },
    { value: 'NSW', label: 'New South Wales' },
    { value: 'VIC', label: 'Victoria' },
    { value: 'QLD', label: 'Queensland' },
    { value: 'WA', label: 'Western Australia' },
    { value: 'SA', label: 'South Australia' },
    { value: 'TAS', label: 'Tasmania' },
    { value: 'ACT', label: 'Australian Capital Territory' },
    { value: 'NT', label: 'Northern Territory' },
  ];

  return (
    <DashboardLayout title="Companies">
      <div className="space-y-6">
        <Card>
          <CardHeader
            title="Practice Management"
            subtitle="Create and manage accounting practices"
            action={
              <Button icon={PlusIcon} onClick={() => setIsCreateModalOpen(true)}>
                Add Company
              </Button>
            }
          />

          {/* Filters */}
          <div className="flex items-center gap-4 mb-6">
            <Input
              placeholder="Search companies..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-64"
            />
            <label className="flex items-center gap-2 text-sm text-gray-600">
              <input
                type="checkbox"
                checked={showInactive}
                onChange={(e) => setShowInactive(e.target.checked)}
                className="rounded border-gray-300"
              />
              Show inactive
            </label>
          </div>

          <DataTable
            columns={columns}
            data={companies}
            pagination={pagination}
            onPageChange={fetchCompanies}
            loading={isLoading}
            emptyMessage="No companies found"
          />
        </Card>
      </div>

      {/* Create Company Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={handleCloseModal}
        title={tempPassword ? 'Company Created' : 'Create New Company'}
        size="lg"
      >
        {tempPassword ? (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-medium text-green-800 mb-2">Company created successfully!</h4>
              <p className="text-sm text-green-700">
                The practice owner has been invited. Here are the temporary credentials:
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div>
                <span className="text-sm text-gray-500">Email:</span>
                <p className="font-medium">{companyData.owner_email}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Temporary Password:</span>
                <p className="font-mono font-medium text-lg bg-white px-3 py-2 rounded border">
                  {tempPassword}
                </p>
              </div>
            </div>

            <p className="text-sm text-gray-600">
              An invitation email has been sent to the practice owner with these credentials.
              They will be required to change their password on first login.
            </p>

            <div className="flex justify-end pt-4">
              <Button onClick={handleCloseModal}>
                Done
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleCreate} className="space-y-6">
            {/* Company Details Section */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Company Details</h4>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Company Name *"
                  value={companyData.name}
                  onChange={(e) => setCompanyData({ ...companyData, name: e.target.value })}
                  placeholder="ABC Accounting"
                  required
                />
                <Select
                  label="Company Type *"
                  options={companyTypeOptions}
                  value={companyData.company_type}
                  onChange={(e) => setCompanyData({ ...companyData, company_type: e.target.value })}
                />
                <Input
                  label="Trading Name"
                  value={companyData.trading_name}
                  onChange={(e) => setCompanyData({ ...companyData, trading_name: e.target.value })}
                  placeholder="ABC Tax Services"
                />
                <Input
                  label="ABN"
                  value={companyData.abn}
                  onChange={(e) => setCompanyData({ ...companyData, abn: e.target.value })}
                  placeholder="12 345 678 901"
                />
                <Input
                  label="ACN"
                  value={companyData.acn}
                  onChange={(e) => setCompanyData({ ...companyData, acn: e.target.value })}
                  placeholder="123 456 789"
                />
                <Input
                  label="Company Email"
                  type="email"
                  value={companyData.company_email}
                  onChange={(e) => setCompanyData({ ...companyData, company_email: e.target.value })}
                  placeholder="info@company.com"
                />
                <Input
                  label="Phone"
                  value={companyData.phone}
                  onChange={(e) => setCompanyData({ ...companyData, phone: e.target.value })}
                  placeholder="+61 2 1234 5678"
                />
                <Input
                  label="Website"
                  value={companyData.website}
                  onChange={(e) => setCompanyData({ ...companyData, website: e.target.value })}
                  placeholder="https://www.company.com"
                  className="col-span-2"
                />
              </div>
            </div>

            {/* Address Section */}
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Address</h4>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Address Line 1"
                  value={companyData.address_line1}
                  onChange={(e) => setCompanyData({ ...companyData, address_line1: e.target.value })}
                  placeholder="123 Main Street"
                  className="col-span-2"
                />
                <Input
                  label="Address Line 2"
                  value={companyData.address_line2}
                  onChange={(e) => setCompanyData({ ...companyData, address_line2: e.target.value })}
                  placeholder="Suite 100"
                  className="col-span-2"
                />
                <Input
                  label="City"
                  value={companyData.city}
                  onChange={(e) => setCompanyData({ ...companyData, city: e.target.value })}
                  placeholder="Sydney"
                />
                <Select
                  label="State"
                  options={stateOptions}
                  value={companyData.state}
                  onChange={(e) => setCompanyData({ ...companyData, state: e.target.value })}
                />
                <Input
                  label="Postcode"
                  value={companyData.postcode}
                  onChange={(e) => setCompanyData({ ...companyData, postcode: e.target.value })}
                  placeholder="2000"
                />
                <Input
                  label="Country"
                  value={companyData.country}
                  onChange={(e) => setCompanyData({ ...companyData, country: e.target.value })}
                  placeholder="Australia"
                />
              </div>
            </div>

            {/* Practice Owner Section */}
            <div className="border-t pt-6">
              <h4 className="font-medium text-gray-900 mb-1">Practice Owner (Admin)</h4>
              <p className="text-sm text-gray-500 mb-3">
                This person will be the primary administrator for this practice.
                They will receive an email with login credentials.
              </p>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Owner Email *"
                  type="email"
                  value={companyData.owner_email}
                  onChange={(e) => setCompanyData({ ...companyData, owner_email: e.target.value })}
                  placeholder="owner@company.com"
                  required
                  className="col-span-2"
                />
                <Input
                  label="First Name"
                  value={companyData.owner_first_name}
                  onChange={(e) => setCompanyData({ ...companyData, owner_first_name: e.target.value })}
                  placeholder="John"
                />
                <Input
                  label="Last Name"
                  value={companyData.owner_last_name}
                  onChange={(e) => setCompanyData({ ...companyData, owner_last_name: e.target.value })}
                  placeholder="Smith"
                />
                <Input
                  label="Owner Phone"
                  value={companyData.owner_phone}
                  onChange={(e) => setCompanyData({ ...companyData, owner_phone: e.target.value })}
                  placeholder="+61 400 123 456"
                  className="col-span-2"
                />
              </div>
            </div>

            {/* Plan Settings */}
            <div className="border-t pt-6">
              <h4 className="font-medium text-gray-900 mb-3">Plan Settings</h4>
              <div className="grid grid-cols-1 gap-4">
                <Select
                  label="Plan Type"
                  options={planOptions}
                  value={companyData.plan_type}
                  onChange={(e) => setCompanyData({ ...companyData, plan_type: e.target.value })}
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3 pt-4 border-t">
              <Button
                variant="secondary"
                onClick={handleCloseModal}
                type="button"
              >
                Cancel
              </Button>
              <Button type="submit" loading={isCreating}>
                Create Company
              </Button>
            </div>
          </form>
        )}
      </Modal>
    </DashboardLayout>
  );
}
