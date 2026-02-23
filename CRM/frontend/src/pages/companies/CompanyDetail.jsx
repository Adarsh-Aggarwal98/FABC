import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  BuildingOfficeIcon,
  UserGroupIcon,
  PencilIcon,
  ArrowLeftIcon,
  PlusIcon,
  EnvelopeIcon,
  PhoneIcon,
  GlobeAltIcon,
  MapPinIcon,
  SwatchIcon,
  PhotoIcon,
  ArrowUpTrayIcon,
  TrashIcon,
  UserIcon,
  StarIcon,
  ClockIcon,
  EyeIcon,
  EyeSlashIcon,
} from '@heroicons/react/24/outline';
import { StarIcon as StarIconSolid } from '@heroicons/react/24/solid';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { Select } from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import DataTable from '../../components/common/DataTable';
import Badge, { RoleBadge } from '../../components/common/Badge';
import { companiesAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

export default function CompanyDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuthStore();
  const fileInputRef = useRef(null);
  const [company, setCompany] = useState(null);
  const [users, setUsers] = useState([]);
  const [userPagination, setUserPagination] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAddUserModalOpen, setIsAddUserModalOpen] = useState(false);
  const [editData, setEditData] = useState({});
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingLogo, setIsUploadingLogo] = useState(false);

  // Company contacts state
  const [contacts, setContacts] = useState([]);
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [showHistoricalContacts, setShowHistoricalContacts] = useState(false);
  const [isSavingContact, setIsSavingContact] = useState(false);
  const [contactFormData, setContactFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    position: '',
    contact_type: 'PRIMARY',
    is_primary: false,
    effective_from: '',
    effective_to: '',
    notes: '',
  });

  // Add user form
  const [newUserData, setNewUserData] = useState({
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    role: 'user',
  });
  const [isAddingUser, setIsAddingUser] = useState(false);
  const [tempPassword, setTempPassword] = useState(null);

  useEffect(() => {
    fetchCompany();
    fetchUsers(1);
    fetchContacts();
  }, [id]);

  useEffect(() => {
    fetchContacts();
  }, [showHistoricalContacts]);

  const fetchCompany = async () => {
    try {
      const response = await companiesAPI.get(id);
      setCompany(response.data.company);
      setEditData(response.data.company);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch company details');
      navigate('/companies');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchUsers = async (page) => {
    try {
      const response = await companiesAPI.getUsers(id, { page });
      setUsers(response.data.users || []);
      setUserPagination(response.data.pagination);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch company users');
    }
  };

  const fetchContacts = async () => {
    try {
      const response = showHistoricalContacts
        ? await companiesAPI.getCompanyContactHistory(id)
        : await companiesAPI.getCompanyContacts(id);
      setContacts(response.data.contacts || []);
    } catch (error) {
      // Silently fail if contacts not yet available (migration not run)
      console.error('Failed to fetch contacts:', error);
      setContacts([]);
    }
  };

  const resetContactForm = () => {
    setContactFormData({
      first_name: '',
      last_name: '',
      email: '',
      phone: '',
      position: '',
      contact_type: 'PRIMARY',
      is_primary: false,
      effective_from: '',
      effective_to: '',
      notes: '',
    });
    setEditingContact(null);
  };

  const handleOpenAddContact = () => {
    resetContactForm();
    setIsContactModalOpen(true);
  };

  const handleOpenEditContact = (contact) => {
    setEditingContact(contact);
    setContactFormData({
      first_name: contact.first_name || '',
      last_name: contact.last_name || '',
      email: contact.email || '',
      phone: contact.phone || '',
      position: contact.position || '',
      contact_type: contact.contact_type || 'PRIMARY',
      is_primary: contact.is_primary || false,
      effective_from: contact.effective_from || '',
      effective_to: contact.effective_to || '',
      notes: contact.notes || '',
    });
    setIsContactModalOpen(true);
  };

  const handleCloseContactModal = () => {
    setIsContactModalOpen(false);
    resetContactForm();
  };

  const handleSaveContact = async (e) => {
    e.preventDefault();
    setIsSavingContact(true);

    try {
      if (editingContact) {
        await companiesAPI.updateCompanyContact(id, editingContact.id, contactFormData);
        toast.success('Contact updated successfully');
      } else {
        await companiesAPI.addCompanyContact(id, contactFormData);
        toast.success('Contact added successfully');
      }
      handleCloseContactModal();
      fetchContacts();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save contact');
    } finally {
      setIsSavingContact(false);
    }
  };

  const handleDeleteContact = async (contact) => {
    if (!window.confirm(`Are you sure you want to remove ${contact.full_name} as a contact?`)) {
      return;
    }

    try {
      await companiesAPI.deleteCompanyContact(id, contact.id);
      toast.success('Contact removed successfully');
      fetchContacts();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to remove contact');
    }
  };

  const handleSetPrimaryContact = async (contact) => {
    try {
      await companiesAPI.setCompanyPrimaryContact(id, contact.id);
      toast.success(`${contact.full_name} is now the primary contact`);
      fetchContacts();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to set primary contact');
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      const response = await companiesAPI.update(id, editData);
      setCompany(response.data.company);
      toast.success('Company updated successfully');
      setIsEditModalOpen(false);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update company');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    setIsAddingUser(true);

    try {
      const response = await companiesAPI.addUser(id, newUserData);
      toast.success('User added successfully');

      if (response.data.temp_password) {
        setTempPassword(response.data.temp_password);
      } else {
        setIsAddUserModalOpen(false);
        resetUserForm();
      }

      fetchUsers(1);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to add user');
    } finally {
      setIsAddingUser(false);
    }
  };

  const resetUserForm = () => {
    setNewUserData({
      email: '',
      first_name: '',
      last_name: '',
      phone: '',
      role: 'user',
    });
    setTempPassword(null);
  };

  const handleCloseUserModal = () => {
    setIsAddUserModalOpen(false);
    resetUserForm();
  };

  const handleLogoUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/svg+xml'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Please upload a valid image file (PNG, JPG, GIF, WebP, or SVG)');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB');
      return;
    }

    setIsUploadingLogo(true);
    try {
      const response = await companiesAPI.uploadLogoForCompany(id, file);
      toast.success('Logo uploaded successfully');
      setCompany((prev) => ({ ...prev, logo_url: response.data.logo_url }));
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to upload logo');
    } finally {
      setIsUploadingLogo(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDeleteLogo = async () => {
    if (!window.confirm('Are you sure you want to delete the company logo?')) {
      return;
    }

    try {
      await companiesAPI.deleteLogoForCompany(id);
      toast.success('Logo deleted successfully');
      setCompany((prev) => ({ ...prev, logo_url: null }));
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete logo');
    }
  };

  const userColumns = [
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
  ];

  // Role options based on current user's role
  const getRoleOptions = () => {
    const role = currentUser?.role;
    switch (role) {
      case 'super_admin':
        return [
          { value: 'admin', label: 'Admin' },
          { value: 'senior_accountant', label: 'Senior Accountant' },
          { value: 'accountant', label: 'Accountant' },
          { value: 'external_accountant', label: 'External Accountant' },
          { value: 'user', label: 'Client' },
        ];
      case 'admin':
        return [
          { value: 'senior_accountant', label: 'Senior Accountant' },
          { value: 'accountant', label: 'Accountant' },
          { value: 'external_accountant', label: 'External Accountant' },
          { value: 'user', label: 'Client' },
        ];
      case 'senior_accountant':
        return [
          { value: 'accountant', label: 'Accountant' },
          { value: 'external_accountant', label: 'External Accountant' },
          { value: 'user', label: 'Client' },
        ];
      case 'accountant':
        return [
          { value: 'external_accountant', label: 'External Accountant' },
          { value: 'user', label: 'Client' },
        ];
      default:
        return [];
    }
  };
  const roleOptions = getRoleOptions();

  // Check if user can invite others (external_accountant and client cannot)
  const canInviteUsers = !['external_accountant', 'user'].includes(currentUser?.role);

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

  const contactTypeOptions = [
    { value: 'PRIMARY', label: 'Primary Contact' },
    { value: 'BILLING', label: 'Billing Contact' },
    { value: 'TECHNICAL', label: 'Technical Contact' },
    { value: 'COMPLIANCE', label: 'Compliance Contact' },
    { value: 'OTHER', label: 'Other' },
  ];

  const getContactTypeBadgeColor = (type) => {
    const colors = {
      PRIMARY: 'bg-blue-100 text-blue-800',
      BILLING: 'bg-green-100 text-green-800',
      TECHNICAL: 'bg-purple-100 text-purple-800',
      COMPLIANCE: 'bg-orange-100 text-orange-800',
      OTHER: 'bg-gray-100 text-gray-800',
    };
    return colors[type] || colors.OTHER;
  };

  const getContactTypeLabel = (type) => {
    const labels = {
      PRIMARY: 'Primary',
      BILLING: 'Billing',
      TECHNICAL: 'Technical',
      COMPLIANCE: 'Compliance',
      OTHER: 'Other',
    };
    return labels[type] || type || 'N/A';
  };

  if (isLoading) {
    return (
      <DashboardLayout title="Company Details">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Company Details">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button
            variant="secondary"
            icon={ArrowLeftIcon}
            onClick={() => navigate('/companies')}
          >
            Back to Companies
          </Button>
          <Button icon={PencilIcon} onClick={() => setIsEditModalOpen(true)}>
            Edit Company
          </Button>
        </div>

        {/* Company Overview */}
        <Card>
          <div className="flex items-start justify-between">
            <div className="flex items-center">
              <div className="h-16 w-16 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center mr-4">
                <BuildingOfficeIcon className="h-8 w-8 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{company?.name}</h2>
                {company?.trading_name && (
                  <p className="text-gray-500">Trading as: {company.trading_name}</p>
                )}
                <div className="flex items-center gap-2 mt-2 flex-wrap">
                  <Badge status={company?.is_active ? 'active' : 'inactive'}>
                    {company?.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    isPracticeOwnerType(company?.company_type)
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {isPracticeOwnerType(company?.company_type) && 'Practice Owner - '}
                    {getCompanyTypeLabel(company?.company_type)}
                  </span>
                  <Badge status={company?.plan_type === 'premium' ? 'success' : company?.plan_type === 'enterprise' ? 'info' : 'default'}>
                    {company?.plan_type?.charAt(0).toUpperCase() + company?.plan_type?.slice(1)} Plan
                  </Badge>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Created</p>
              <p className="font-medium">{new Date(company?.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </Card>

        {/* Details Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Business Details */}
          <Card>
            <CardHeader title="Business Details" />
            <div className="space-y-4">
              {company?.abn && (
                <div>
                  <span className="text-sm text-gray-500">ABN</span>
                  <p className="font-medium">{company.abn}</p>
                </div>
              )}
              {company?.acn && (
                <div>
                  <span className="text-sm text-gray-500">ACN</span>
                  <p className="font-medium">{company.acn}</p>
                </div>
              )}
              {company?.email && (
                <div className="flex items-center gap-2">
                  <EnvelopeIcon className="h-4 w-4 text-gray-400" />
                  <span>{company.email}</span>
                </div>
              )}
              {company?.phone && (
                <div className="flex items-center gap-2">
                  <PhoneIcon className="h-4 w-4 text-gray-400" />
                  <span>{company.phone}</span>
                </div>
              )}
              {company?.website && (
                <div className="flex items-center gap-2">
                  <GlobeAltIcon className="h-4 w-4 text-gray-400" />
                  <a href={company.website} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                    {company.website}
                  </a>
                </div>
              )}
              {(company?.address_line1 || company?.city) && (
                <div className="flex items-start gap-2">
                  <MapPinIcon className="h-4 w-4 text-gray-400 mt-0.5" />
                  <div>
                    {company.address_line1 && <p>{company.address_line1}</p>}
                    {company.address_line2 && <p>{company.address_line2}</p>}
                    <p>
                      {[company.city, company.state, company.postcode].filter(Boolean).join(', ')}
                    </p>
                    {company.country && <p>{company.country}</p>}
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* Practice Owner */}
          <Card>
            <CardHeader title="Practice Owner" />
            {company?.owner ? (
              <div className="flex items-center">
                <div className="h-12 w-12 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center mr-3">
                  <span className="text-white font-semibold text-lg">
                    {company.owner.first_name?.[0] || company.owner.email?.[0]?.toUpperCase()}
                  </span>
                </div>
                <div>
                  <p className="font-medium text-gray-900">{company.owner.full_name || 'N/A'}</p>
                  <p className="text-sm text-gray-500">{company.owner.email}</p>
                  {company.owner.phone && (
                    <p className="text-sm text-gray-500">{company.owner.phone}</p>
                  )}
                </div>
              </div>
            ) : (
              <p className="text-gray-500">No owner assigned</p>
            )}

            <div className="mt-6 pt-4 border-t">
              <h4 className="font-medium text-gray-700 mb-3">Statistics</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Users</span>
                    <UserGroupIcon className="h-4 w-4 text-gray-400" />
                  </div>
                  <p className="text-xl font-bold mt-1">
                    {company?.user_count || 0}
                  </p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Clients</span>
                    <UserGroupIcon className="h-4 w-4 text-gray-400" />
                  </div>
                  <p className="text-xl font-bold mt-1">
                    {company?.client_count || 0}
                  </p>
                </div>
              </div>
            </div>
          </Card>
        </div>

        {/* Company Users */}
        <Card>
          <CardHeader
            title="Company Users"
            subtitle="Users belonging to this practice"
            action={
              canInviteUsers && (
                <Button icon={PlusIcon} onClick={() => setIsAddUserModalOpen(true)}>
                  Add User
                </Button>
              )
            }
          />
          <DataTable
            columns={userColumns}
            data={users}
            pagination={userPagination}
            onPageChange={fetchUsers}
            emptyMessage="No users in this company"
          />
        </Card>

        {/* Company Contacts */}
        <Card>
          <CardHeader
            title="Company Contacts"
            subtitle="Key contacts for this company with role-based classifications"
            action={
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowHistoricalContacts(!showHistoricalContacts)}
                  className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900"
                  title={showHistoricalContacts ? 'Hide historical contacts' : 'Show historical contacts'}
                >
                  {showHistoricalContacts ? (
                    <>
                      <EyeSlashIcon className="h-4 w-4" />
                      <span>Hide History</span>
                    </>
                  ) : (
                    <>
                      <EyeIcon className="h-4 w-4" />
                      <span>Show History</span>
                    </>
                  )}
                </button>
                <Button icon={PlusIcon} onClick={handleOpenAddContact}>
                  Add Contact
                </Button>
              </div>
            }
          />

          {contacts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <UserIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
              <p>No contacts found for this company</p>
              <p className="text-sm mt-1">Add a contact to get started</p>
            </div>
          ) : (
            <div className="divide-y">
              {contacts.map((contact) => (
                <div
                  key={contact.id}
                  className={`p-4 flex items-start justify-between ${
                    !contact.is_active ? 'opacity-60 bg-gray-50' : ''
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className="h-12 w-12 rounded-full bg-gradient-to-br from-indigo-400 to-indigo-600 flex items-center justify-center flex-shrink-0">
                      <span className="text-white font-semibold text-lg">
                        {contact.first_name?.[0]?.toUpperCase() || 'C'}
                      </span>
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-gray-900">{contact.full_name}</h4>
                        {contact.is_primary && (
                          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                            <StarIconSolid className="h-3 w-3" />
                            Primary
                          </span>
                        )}
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getContactTypeBadgeColor(contact.contact_type)}`}>
                          {getContactTypeLabel(contact.contact_type)}
                        </span>
                        {!contact.is_active && (
                          <span className="px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            Inactive
                          </span>
                        )}
                      </div>
                      {contact.position && (
                        <p className="text-sm text-gray-500">{contact.position}</p>
                      )}
                      <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
                        {contact.email && (
                          <span className="flex items-center gap-1">
                            <EnvelopeIcon className="h-4 w-4 text-gray-400" />
                            {contact.email}
                          </span>
                        )}
                        {contact.phone && (
                          <span className="flex items-center gap-1">
                            <PhoneIcon className="h-4 w-4 text-gray-400" />
                            {contact.phone}
                          </span>
                        )}
                      </div>
                      {(contact.effective_from || contact.effective_to) && (
                        <p className="text-xs text-gray-400 mt-1 flex items-center gap-1">
                          <ClockIcon className="h-3 w-3" />
                          {contact.effective_from && `From ${contact.effective_from}`}
                          {contact.effective_from && contact.effective_to && ' - '}
                          {contact.effective_to && `Until ${contact.effective_to}`}
                        </p>
                      )}
                    </div>
                  </div>
                  {contact.is_active && (
                    <div className="flex items-center gap-2">
                      {!contact.is_primary && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleSetPrimaryContact(contact)}
                          title="Set as primary contact"
                        >
                          <StarIcon className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleOpenEditContact(contact)}
                        title="Edit contact"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteContact(contact)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        title="Remove contact"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </Card>

        {/* Branding Settings */}
        <Card>
          <CardHeader
            title="Branding Settings"
            subtitle="Customize the company's logo and theme colors"
          />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Logo */}
            <div>
              <h4 className="font-medium text-gray-700 mb-3">Company Logo</h4>
              <div className="flex items-center gap-4">
                <div className="w-24 h-24 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50 overflow-hidden">
                  {company?.logo_url ? (
                    <img
                      src={company.logo_url}
                      alt="Company Logo"
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <div className="text-center text-gray-400">
                      <PhotoIcon className="h-8 w-8 mx-auto mb-1" />
                      <p className="text-xs">No logo</p>
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-500 mb-2">
                    Recommended: 200x200px. Max 5MB. PNG, JPG, SVG.
                  </p>
                  <div className="flex gap-2">
                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleLogoUpload}
                      accept="image/png,image/jpeg,image/gif,image/webp,image/svg+xml"
                      className="hidden"
                    />
                    <Button
                      variant="secondary"
                      size="sm"
                      icon={ArrowUpTrayIcon}
                      onClick={() => fileInputRef.current?.click()}
                      loading={isUploadingLogo}
                    >
                      {company?.logo_url ? 'Change' : 'Upload'}
                    </Button>
                    {company?.logo_url && (
                      <Button
                        variant="ghost"
                        size="sm"
                        icon={TrashIcon}
                        onClick={handleDeleteLogo}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        Remove
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Theme Colors */}
            <div>
              <h4 className="font-medium text-gray-700 mb-3">Theme Colors</h4>
              <div className="flex gap-4">
                <div className="flex-1">
                  <label className="block text-xs text-gray-500 mb-1">Primary</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={editData.primary_color || '#4F46E5'}
                      onChange={(e) => setEditData({ ...editData, primary_color: e.target.value })}
                      className="w-10 h-10 rounded cursor-pointer border border-gray-300"
                    />
                    <Input
                      value={editData.primary_color || '#4F46E5'}
                      onChange={(e) => setEditData({ ...editData, primary_color: e.target.value })}
                      className="flex-1 text-sm"
                    />
                  </div>
                </div>
                <div className="flex-1">
                  <label className="block text-xs text-gray-500 mb-1">Secondary</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={editData.secondary_color || '#10B981'}
                      onChange={(e) => setEditData({ ...editData, secondary_color: e.target.value })}
                      className="w-10 h-10 rounded cursor-pointer border border-gray-300"
                    />
                    <Input
                      value={editData.secondary_color || '#10B981'}
                      onChange={(e) => setEditData({ ...editData, secondary_color: e.target.value })}
                      className="flex-1 text-sm"
                    />
                  </div>
                </div>
                <div className="flex-1">
                  <label className="block text-xs text-gray-500 mb-1">Tertiary</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="color"
                      value={editData.tertiary_color || '#6366F1'}
                      onChange={(e) => setEditData({ ...editData, tertiary_color: e.target.value })}
                      className="w-10 h-10 rounded cursor-pointer border border-gray-300"
                    />
                    <Input
                      value={editData.tertiary_color || '#6366F1'}
                      onChange={(e) => setEditData({ ...editData, tertiary_color: e.target.value })}
                      className="flex-1 text-sm"
                    />
                  </div>
                </div>
              </div>
              <div className="mt-4">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={async () => {
                    try {
                      await companiesAPI.update(id, {
                        primary_color: editData.primary_color,
                        secondary_color: editData.secondary_color,
                        tertiary_color: editData.tertiary_color,
                      });
                      toast.success('Theme colors updated');
                      fetchCompany();
                    } catch (error) {
                      toast.error('Failed to update theme colors');
                    }
                  }}
                >
                  Save Colors
                </Button>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Edit Company Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Company"
        size="lg"
      >
        <form onSubmit={handleSave} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Company Name *"
              value={editData.name || ''}
              onChange={(e) => setEditData({ ...editData, name: e.target.value })}
              required
            />
            <Select
              label="Company Type"
              options={companyTypeOptions}
              value={editData.company_type || 'tax_agent'}
              onChange={(e) => setEditData({ ...editData, company_type: e.target.value })}
            />
            <Input
              label="Trading Name"
              value={editData.trading_name || ''}
              onChange={(e) => setEditData({ ...editData, trading_name: e.target.value })}
            />
            <Input
              label="ABN"
              value={editData.abn || ''}
              onChange={(e) => setEditData({ ...editData, abn: e.target.value })}
            />
            <Input
              label="ACN"
              value={editData.acn || ''}
              onChange={(e) => setEditData({ ...editData, acn: e.target.value })}
            />
            <Input
              label="Email"
              type="email"
              value={editData.email || ''}
              onChange={(e) => setEditData({ ...editData, email: e.target.value })}
            />
            <Input
              label="Phone"
              value={editData.phone || ''}
              onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
            />
            <Input
              label="Website"
              value={editData.website || ''}
              onChange={(e) => setEditData({ ...editData, website: e.target.value })}
              className="col-span-2"
            />
          </div>

          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-900 mb-3">Address</h4>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Address Line 1"
                value={editData.address_line1 || ''}
                onChange={(e) => setEditData({ ...editData, address_line1: e.target.value })}
                className="col-span-2"
              />
              <Input
                label="Address Line 2"
                value={editData.address_line2 || ''}
                onChange={(e) => setEditData({ ...editData, address_line2: e.target.value })}
                className="col-span-2"
              />
              <Input
                label="City"
                value={editData.city || ''}
                onChange={(e) => setEditData({ ...editData, city: e.target.value })}
              />
              <Select
                label="State"
                options={stateOptions}
                value={editData.state || ''}
                onChange={(e) => setEditData({ ...editData, state: e.target.value })}
              />
              <Input
                label="Postcode"
                value={editData.postcode || ''}
                onChange={(e) => setEditData({ ...editData, postcode: e.target.value })}
              />
              <Input
                label="Country"
                value={editData.country || ''}
                onChange={(e) => setEditData({ ...editData, country: e.target.value })}
              />
            </div>
          </div>

          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-900 mb-3">Plan Settings</h4>
            <div className="grid grid-cols-1 gap-4">
              <Select
                label="Plan Type"
                options={planOptions}
                value={editData.plan_type || 'standard'}
                onChange={(e) => setEditData({ ...editData, plan_type: e.target.value })}
              />
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button variant="secondary" onClick={() => setIsEditModalOpen(false)} type="button">
              Cancel
            </Button>
            <Button type="submit" loading={isSaving}>
              Save Changes
            </Button>
          </div>
        </form>
      </Modal>

      {/* Add User Modal */}
      <Modal
        isOpen={isAddUserModalOpen}
        onClose={handleCloseUserModal}
        title={tempPassword ? 'User Added' : 'Add User to Company'}
      >
        {tempPassword ? (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-medium text-green-800 mb-2">User added successfully!</h4>
              <p className="text-sm text-green-700">
                The user has been invited. Here are the temporary credentials:
              </p>
            </div>

            <div className="bg-gray-50 rounded-lg p-4 space-y-2">
              <div>
                <span className="text-sm text-gray-500">Email:</span>
                <p className="font-medium">{newUserData.email}</p>
              </div>
              <div>
                <span className="text-sm text-gray-500">Temporary Password:</span>
                <p className="font-mono font-medium text-lg bg-white px-3 py-2 rounded border">
                  {tempPassword}
                </p>
              </div>
            </div>

            <p className="text-sm text-gray-600">
              An invitation email has been sent to the user with these credentials.
            </p>

            <div className="flex justify-end pt-4">
              <Button onClick={handleCloseUserModal}>
                Done
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleAddUser} className="space-y-4">
            <Input
              label="Email *"
              type="email"
              value={newUserData.email}
              onChange={(e) => setNewUserData({ ...newUserData, email: e.target.value })}
              placeholder="user@example.com"
              required
            />

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="First Name"
                value={newUserData.first_name}
                onChange={(e) => setNewUserData({ ...newUserData, first_name: e.target.value })}
                placeholder="John"
              />
              <Input
                label="Last Name"
                value={newUserData.last_name}
                onChange={(e) => setNewUserData({ ...newUserData, last_name: e.target.value })}
                placeholder="Doe"
              />
            </div>

            <Input
              label="Phone"
              value={newUserData.phone}
              onChange={(e) => setNewUserData({ ...newUserData, phone: e.target.value })}
              placeholder="+61 400 123 456"
            />

            <Select
              label="Role"
              options={roleOptions}
              value={newUserData.role}
              onChange={(e) => setNewUserData({ ...newUserData, role: e.target.value })}
            />

            <div className="flex justify-end space-x-3 pt-4">
              <Button variant="secondary" onClick={handleCloseUserModal} type="button">
                Cancel
              </Button>
              <Button type="submit" loading={isAddingUser}>
                Add User
              </Button>
            </div>
          </form>
        )}
      </Modal>

      {/* Add/Edit Contact Modal */}
      <Modal
        isOpen={isContactModalOpen}
        onClose={handleCloseContactModal}
        title={editingContact ? 'Edit Contact' : 'Add Contact'}
        size="lg"
      >
        <form onSubmit={handleSaveContact} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="First Name *"
              value={contactFormData.first_name}
              onChange={(e) => setContactFormData({ ...contactFormData, first_name: e.target.value })}
              placeholder="John"
              required
            />
            <Input
              label="Last Name *"
              value={contactFormData.last_name}
              onChange={(e) => setContactFormData({ ...contactFormData, last_name: e.target.value })}
              placeholder="Doe"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Email"
              type="email"
              value={contactFormData.email}
              onChange={(e) => setContactFormData({ ...contactFormData, email: e.target.value })}
              placeholder="john@example.com"
            />
            <Input
              label="Phone"
              value={contactFormData.phone}
              onChange={(e) => setContactFormData({ ...contactFormData, phone: e.target.value })}
              placeholder="+61 400 123 456"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Position / Job Title"
              value={contactFormData.position}
              onChange={(e) => setContactFormData({ ...contactFormData, position: e.target.value })}
              placeholder="Financial Controller"
            />
            <Select
              label="Contact Type"
              options={contactTypeOptions}
              value={contactFormData.contact_type}
              onChange={(e) => setContactFormData({ ...contactFormData, contact_type: e.target.value })}
            />
          </div>

          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-900 mb-3">Effective Period (Optional)</h4>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Effective From"
                type="date"
                value={contactFormData.effective_from}
                onChange={(e) => setContactFormData({ ...contactFormData, effective_from: e.target.value })}
              />
              <Input
                label="Effective To"
                type="date"
                value={contactFormData.effective_to}
                onChange={(e) => setContactFormData({ ...contactFormData, effective_to: e.target.value })}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              value={contactFormData.notes}
              onChange={(e) => setContactFormData({ ...contactFormData, notes: e.target.value })}
              placeholder="Additional notes about this contact..."
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <input
                type="checkbox"
                id="is_primary_contact"
                checked={contactFormData.is_primary}
                onChange={(e) => setContactFormData({ ...contactFormData, is_primary: e.target.checked })}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <div>
                <label htmlFor="is_primary_contact" className="text-sm font-medium text-gray-900 cursor-pointer">
                  Set as Primary Contact
                </label>
                <p className="text-xs text-gray-500 mt-1">
                  The primary contact will be used as the default contact for this company.
                </p>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button variant="secondary" onClick={handleCloseContactModal} type="button">
              Cancel
            </Button>
            <Button type="submit" loading={isSavingContact}>
              {editingContact ? 'Save Changes' : 'Add Contact'}
            </Button>
          </div>
        </form>
      </Modal>
    </DashboardLayout>
  );
}
