import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  EyeIcon,
  MagnifyingGlassIcon,
  BuildingOffice2Icon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { Select } from '../../components/common/Input';
import DataTable from '../../components/common/DataTable';
import Badge from '../../components/common/Badge';
import { ClientEntityForm } from '../../components/features/client-entities';
import { clientEntitiesAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

const ENTITY_TYPE_OPTIONS = [
  { value: '', label: 'All Types' },
  { value: 'COMPANY', label: 'Company' },
  { value: 'TRUST', label: 'Trust' },
  { value: 'SMSF', label: 'SMSF' },
  { value: 'PARTNERSHIP', label: 'Partnership' },
  { value: 'SOLE_TRADER', label: 'Sole Trader' },
  { value: 'INDIVIDUAL', label: 'Individual' },
];

export default function ClientEntityList() {
  const navigate = useNavigate();
  const { user: currentUser } = useAuthStore();
  const [entities, setEntities] = useState([]);
  const [pagination, setPagination] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [typeFilter, setTypeFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('active');

  const isAdmin = currentUser?.role === 'admin' || currentUser?.role === 'super_admin';
  const isStaff = isAdmin || currentUser?.role === 'accountant';

  useEffect(() => {
    fetchEntities(1);
  }, [typeFilter, activeFilter]);

  const fetchEntities = async (page) => {
    setIsLoading(true);
    try {
      if (isStaff) {
        // Staff can see all entities
        const params = {
          page,
          per_page: 20,
        };

        if (typeFilter) params.entity_type = typeFilter;
        if (activeFilter === 'active') params.is_active = true;
        if (activeFilter === 'inactive') params.is_active = false;
        if (searchQuery) params.search = searchQuery;

        const response = await clientEntitiesAPI.list(params);
        setEntities(response.data.data?.entities || response.data.data || []);
        setPagination(response.data.pagination);
      } else {
        // Regular users see only their linked entities
        const response = await clientEntitiesAPI.getMyEntities();
        let userEntities = response.data.entities || [];

        // Apply local filters for users
        if (typeFilter) {
          userEntities = userEntities.filter(e => e.entity_type === typeFilter);
        }
        if (searchQuery) {
          const query = searchQuery.toLowerCase();
          userEntities = userEntities.filter(e =>
            e.name?.toLowerCase().includes(query) ||
            e.abn?.includes(query)
          );
        }

        setEntities(userEntities);
        setPagination(null); // No pagination for user's own entities
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch client entities');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = () => {
    fetchEntities(1);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const handleCreateSuccess = (newEntity) => {
    setIsCreateModalOpen(false);
    toast.success('Client entity created successfully');
    fetchEntities(1);
  };

  const getEntityTypeLabel = (type) => {
    const labels = {
      COMPANY: 'Company',
      TRUST: 'Trust',
      SMSF: 'SMSF',
      PARTNERSHIP: 'Partnership',
      SOLE_TRADER: 'Sole Trader',
      INDIVIDUAL: 'Individual',
    };
    return labels[type] || type;
  };

  const getEntityTypeBadgeColor = (type) => {
    const colors = {
      COMPANY: 'primary',
      TRUST: 'secondary',
      SMSF: 'success',
      PARTNERSHIP: 'warning',
      SOLE_TRADER: 'info',
      INDIVIDUAL: 'default',
    };
    return colors[type] || 'default';
  };

  const columns = [
    {
      key: 'name',
      title: 'Entity',
      render: (row) => (
        <div className="flex items-start gap-3">
          <BuildingOffice2Icon className="h-5 w-5 text-gray-400 mt-1" />
          <div>
            <p className="font-medium text-gray-900">{row.name}</p>
            {row.trading_name && (
              <p className="text-sm text-gray-500">
                Trading as: {row.trading_name}
              </p>
            )}
          </div>
        </div>
      ),
    },
    {
      key: 'entity_type',
      title: 'Type',
      render: (row) => (
        <Badge status={getEntityTypeBadgeColor(row.entity_type)}>
          {getEntityTypeLabel(row.entity_type)}
        </Badge>
      ),
    },
    {
      key: 'abn',
      title: 'ABN',
      render: (row) => (
        <span className="text-sm text-gray-600">
          {row.abn || '-'}
        </span>
      ),
    },
    {
      key: 'contact',
      title: 'Contact',
      render: (row) => (
        <div className="text-sm">
          {row.email && <p className="text-gray-600">{row.email}</p>}
          {row.phone && <p className="text-gray-500">{row.phone}</p>}
          {!row.email && !row.phone && <span className="text-gray-400">-</span>}
        </div>
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
      key: 'actions',
      title: 'Actions',
      render: (row) => (
        <div className="flex gap-2">
          <Link to={`/client-entities/${row.id}`}>
            <Button variant="secondary" size="sm" icon={EyeIcon}>
              View
            </Button>
          </Link>
        </div>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {isStaff ? 'Client Entities' : 'My Business Entities'}
            </h1>
            <p className="text-gray-500 mt-1">
              {isStaff
                ? 'Manage client organizations (companies, trusts, SMSFs, etc.)'
                : 'View your linked business organizations'}
            </p>
          </div>
          {isAdmin && (
            <Button
              icon={PlusIcon}
              onClick={() => setIsCreateModalOpen(true)}
            >
              Add Entity
            </Button>
          )}
        </div>

        {/* Filters */}
        <Card>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by name or ABN..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                />
              </div>
            </div>
            <Select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              options={ENTITY_TYPE_OPTIONS}
              className="w-40"
            />
            <Select
              value={activeFilter}
              onChange={(e) => setActiveFilter(e.target.value)}
              options={[
                { value: 'all', label: 'All Status' },
                { value: 'active', label: 'Active' },
                { value: 'inactive', label: 'Inactive' },
              ]}
              className="w-32"
            />
            <Button variant="secondary" onClick={handleSearch}>
              Search
            </Button>
          </div>
        </Card>

        {/* Results */}
        <Card>
          <CardHeader
            title="Entities"
            subtitle={`${pagination?.total || entities.length} total entities`}
          />
          <DataTable
            columns={columns}
            data={entities}
            loading={isLoading}
            pagination={pagination}
            onPageChange={(page) => fetchEntities(page)}
            emptyMessage="No client entities found"
          />
        </Card>
      </div>

      {/* Create Modal */}
      {isCreateModalOpen && (
        <ClientEntityForm
          isModal
          onSave={handleCreateSuccess}
          onCancel={() => setIsCreateModalOpen(false)}
        />
      )}
    </DashboardLayout>
  );
}
