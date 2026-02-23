import React, { useEffect, useState } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { PlusIcon, EyeIcon, ArrowUpTrayIcon } from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { Select } from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import DataTable from '../../components/common/DataTable';
import Badge, { RoleBadge } from '../../components/common/Badge';
import { userAPI, companiesAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

export default function UserList() {
  const navigate = useNavigate();
  const { user: currentUser } = useAuthStore();
  const [searchParams] = useSearchParams();
  const [users, setUsers] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(searchParams.get('invite') === 'true');
  const [roleFilter, setRoleFilter] = useState('');
  const [nameSearch, setNameSearch] = useState('');

  // Invite form
  const [inviteData, setInviteData] = useState({
    email: '',
    role: 'user',
    first_name: '',
    last_name: '',
    company_id: '',
  });
  const [isInviting, setIsInviting] = useState(false);
  const [companies, setCompanies] = useState([]);

  // Fetch companies for super_admin to select when inviting admin/senior_accountant
  useEffect(() => {
    if (currentUser?.role === 'super_admin') {
      fetchCompanies();
    }
  }, [currentUser]);

  const fetchCompanies = async () => {
    try {
      const response = await companiesAPI.list();
      setCompanies(response.data.companies || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch companies');
    }
  };

  useEffect(() => {
    fetchUsers(1);
  }, [roleFilter]);

  const fetchUsers = async (page) => {
    setIsLoading(true);
    try {
      const response = await userAPI.list({
        page,
        role: roleFilter || undefined,
        name: nameSearch || undefined
      });
      // API returns { success, data: [...users], pagination: {...} }
      setUsers(response.data.data || []);
      setPagination(response.data.pagination);
    } catch (error) {
      toast.error('Failed to fetch users');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNameSearch = (e) => {
    if (e.key === 'Enter') {
      fetchUsers(1);
    }
  };

  const handleInvite = async (e) => {
    e.preventDefault();
    setIsInviting(true);

    try {
      await userAPI.invite(inviteData);
      toast.success('User invited successfully');
      setIsInviteModalOpen(false);
      setInviteData({ email: '', role: 'user', first_name: '', last_name: '', company_id: '' });
      fetchUsers(1);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to invite user');
    } finally {
      setIsInviting(false);
    }
  };

  const handleToggleStatus = async (userId, currentStatus) => {
    try {
      await userAPI.toggleStatus(userId, !currentStatus);
      toast.success(`User ${currentStatus ? 'deactivated' : 'activated'}`);
      fetchUsers(pagination?.page || 1);
    } catch (error) {
      toast.error('Failed to update user status');
    }
  };

  const columns = [
    {
      key: 'name',
      title: 'Name',
      render: (row) => (
        <div>
          <p className="font-medium text-gray-900">{row.full_name || 'N/A'}</p>
          <p className="text-sm text-gray-500">{row.email}</p>
        </div>
      ),
    },
    {
      key: 'role',
      title: 'Role',
      render: (row) => <RoleBadge role={row.role} />,
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
      title: 'Joined',
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
        <div className="flex gap-2">
          <Link to={`/users/${row.id}`}>
            <Button variant="secondary" size="sm" icon={EyeIcon}>
              View
            </Button>
          </Link>
          <Button
            variant={row.is_active ? 'danger' : 'success'}
            size="sm"
            onClick={() => handleToggleStatus(row.id, row.is_active)}
          >
            {row.is_active ? 'Deactivate' : 'Activate'}
          </Button>
        </div>
      ),
    },
  ];

  const roleOptions = [
    { value: '', label: 'All Roles' },
    { value: 'super_admin', label: 'Super Admin' },
    { value: 'admin', label: 'Admin' },
    { value: 'senior_accountant', label: 'Senior Accountant' },
    { value: 'accountant', label: 'Accountant' },
    { value: 'external_accountant', label: 'External Accountant' },
    { value: 'user', label: 'User' },
  ];

  // Build invite role options based on current user's role
  // - Super admin: can invite all roles
  // - Admin: can invite senior_accountant, accountant, external_accountant, user
  // - Senior Accountant: can invite accountant, external_accountant, user
  // - Accountant: can invite external_accountant, user
  // - External accountant & user: cannot invite anyone
  const getInviteRoleOptions = () => {
    if (currentUser?.role === 'super_admin') {
      return [
        { value: 'user', label: 'User (Client)' },
        { value: 'external_accountant', label: 'External Accountant' },
        { value: 'accountant', label: 'Accountant' },
        { value: 'senior_accountant', label: 'Senior Accountant' },
        { value: 'admin', label: 'Admin' },
        { value: 'super_admin', label: 'Super Admin' },
      ];
    } else if (currentUser?.role === 'admin') {
      return [
        { value: 'user', label: 'User (Client)' },
        { value: 'external_accountant', label: 'External Accountant' },
        { value: 'accountant', label: 'Accountant' },
        { value: 'senior_accountant', label: 'Senior Accountant' },
      ];
    } else if (currentUser?.role === 'senior_accountant') {
      return [
        { value: 'user', label: 'User (Client)' },
        { value: 'external_accountant', label: 'External Accountant' },
        { value: 'accountant', label: 'Accountant' },
      ];
    } else if (currentUser?.role === 'accountant') {
      return [
        { value: 'user', label: 'User (Client)' },
        { value: 'external_accountant', label: 'External Accountant' },
      ];
    }
    return [];
  };

  const inviteRoleOptions = getInviteRoleOptions();

  return (
    <DashboardLayout title="Users">
      <div className="space-y-6">
        <Card>
          <CardHeader
            title="User Management"
            subtitle="Invite and manage users"
            action={
              (currentUser?.role === 'super_admin' || currentUser?.role === 'admin' || currentUser?.role === 'senior_accountant') && (
                <div className="flex gap-2">
                  <Button
                    variant="secondary"
                    icon={ArrowUpTrayIcon}
                    onClick={() => navigate('/settings/import')}
                  >
                    Import CSV
                  </Button>
                  <Button icon={PlusIcon} onClick={() => setIsInviteModalOpen(true)}>
                    Invite User
                  </Button>
                </div>
              )
            }
          />

          {/* Filters */}
          <div className="mb-6 flex flex-wrap gap-3 items-end">
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Search by Name/Email</label>
              <input
                type="text"
                value={nameSearch}
                onChange={(e) => setNameSearch(e.target.value)}
                onKeyDown={handleNameSearch}
                placeholder="Type and press Enter..."
                className="w-56 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-500 mb-1">Role</label>
              <Select
                options={roleOptions}
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
                className="w-48"
              />
            </div>
            {(nameSearch || roleFilter) && (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => {
                  setNameSearch('');
                  setRoleFilter('');
                }}
                className="text-red-600 hover:text-red-700"
              >
                Clear Filters
              </Button>
            )}
          </div>

          <DataTable
            columns={columns}
            data={users}
            pagination={pagination}
            onPageChange={fetchUsers}
            loading={isLoading}
            emptyMessage="No users found"
          />
        </Card>
      </div>

      {/* Invite Modal */}
      <Modal
        isOpen={isInviteModalOpen}
        onClose={() => setIsInviteModalOpen(false)}
        title="Invite User"
      >
        <form onSubmit={handleInvite} className="space-y-4">
          <Input
            label="Email"
            type="email"
            value={inviteData.email}
            onChange={(e) => setInviteData({ ...inviteData, email: e.target.value })}
            placeholder="user@example.com"
            required
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="First Name"
              value={inviteData.first_name}
              onChange={(e) => setInviteData({ ...inviteData, first_name: e.target.value })}
              placeholder="John"
            />
            <Input
              label="Last Name"
              value={inviteData.last_name}
              onChange={(e) => setInviteData({ ...inviteData, last_name: e.target.value })}
              placeholder="Doe"
            />
          </div>

          <Select
            label="Role"
            options={inviteRoleOptions}
            value={inviteData.role}
            onChange={(e) => setInviteData({ ...inviteData, role: e.target.value })}
          />

          {/* Company selector for super_admin when inviting admin/senior_accountant */}
          {currentUser?.role === 'super_admin' && ['admin', 'senior_accountant'].includes(inviteData.role) && (
            <Select
              label="Company"
              options={[
                { value: '', label: 'Select Company' },
                ...companies.map(c => ({ value: c.id, label: c.name }))
              ]}
              value={inviteData.company_id}
              onChange={(e) => setInviteData({ ...inviteData, company_id: e.target.value })}
              required
            />
          )}

          <div className="flex justify-end space-x-3 pt-4">
            <Button
              variant="secondary"
              onClick={() => setIsInviteModalOpen(false)}
              type="button"
            >
              Cancel
            </Button>
            <Button type="submit" loading={isInviting}>
              Send Invite
            </Button>
          </div>
        </form>
      </Modal>
    </DashboardLayout>
  );
}
