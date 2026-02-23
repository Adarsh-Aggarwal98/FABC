import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  BriefcaseIcon,
  CalendarIcon,
  DocumentTextIcon,
  BanknotesIcon,
  CheckBadgeIcon,
  PlusIcon,
  PencilSquareIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { Select, TextArea } from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import Badge, { RoleBadge } from '../../components/common/Badge';
import { userAPI, servicesAPI, requestsAPI, documentsAPI } from '../../services/api';
import DocumentViewer from '../../components/common/DocumentViewer';
import useAuthStore from '../../store/authStore';

export default function UserDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuthStore();
  const [userData, setUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Create request modal state
  const [isCreateRequestModalOpen, setIsCreateRequestModalOpen] = useState(false);
  const [services, setServices] = useState([]);
  const [selectedServices, setSelectedServices] = useState([]);
  const [isCreatingRequest, setIsCreatingRequest] = useState(false);

  // Edit user modal state
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editData, setEditData] = useState({});
  const [isEditing, setIsEditing] = useState(false);

  // Document upload/view state
  const [isUploadingDoc, setIsUploadingDoc] = useState(null);
  const [viewingDoc, setViewingDoc] = useState(null);

  const isAdmin = currentUser?.role === 'super_admin' || currentUser?.role === 'admin';
  const isStaff = isAdmin || currentUser?.role === 'accountant';

  useEffect(() => {
    fetchUser();
    if (isAdmin) {
      fetchServices();
    }
  }, [id, isAdmin]);

  const fetchUser = async () => {
    setIsLoading(true);
    try {
      const response = await userAPI.get(id);
      setUserData(response.data.data.user);
    } catch (error) {
      toast.error('Failed to fetch user details');
      navigate('/users');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchServices = async () => {
    try {
      // Pass user_id to filter services by the user's company type
      const response = await servicesAPI.list({ active_only: true, user_id: id });
      // Handle both response structures: response.data.data.services or response.data.services
      const servicesList = response.data.data?.services || response.data.services || [];
      setServices(servicesList);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch services');
    }
  };

  const openEditModal = () => {
    setEditData({
      first_name: userData?.first_name || '',
      last_name: userData?.last_name || '',
      phone: userData?.phone || '',
      address: userData?.address || '',
      date_of_birth: userData?.date_of_birth || '',
      occupation: userData?.occupation || '',
      company_name: userData?.company_name || '',
      personal_email: userData?.personal_email || '',
      tfn: userData?.tfn || '',
      visa_status: userData?.visa_status || '',
      bsb: userData?.bsb || '',
      bank_account_number: userData?.bank_account_number || '',
      bank_account_holder_name: userData?.bank_account_holder_name || '',
    });
    setIsEditModalOpen(true);
  };

  const handleEditSubmit = async () => {
    setIsEditing(true);
    try {
      await userAPI.update(id, editData);
      toast.success('User details updated successfully');
      setIsEditModalOpen(false);
      fetchUser();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update user');
    } finally {
      setIsEditing(false);
    }
  };

  const handleServiceToggle = (serviceId) => {
    setSelectedServices((prev) =>
      prev.includes(serviceId)
        ? prev.filter((id) => id !== serviceId)
        : [...prev, serviceId]
    );
  };

  const handleCreateRequest = async () => {
    if (selectedServices.length === 0) {
      toast.error('Please select at least one service');
      return;
    }

    setIsCreatingRequest(true);
    try {
      await requestsAPI.createForUser(selectedServices, id);
      toast.success(`${selectedServices.length} request(s) created successfully`);
      setIsCreateRequestModalOpen(false);
      setSelectedServices([]);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create request');
    } finally {
      setIsCreatingRequest(false);
    }
  };

  const handleDocumentUpload = async (docType, file) => {
    if (!file) return;

    setIsUploadingDoc(docType);
    try {
      // Upload the document
      const uploadResponse = await documentsAPI.upload(file, null, docType, `${docType} for user ${userData?.full_name}`);
      const docUrl = uploadResponse.data.document?.id || uploadResponse.data.document?.file_url;

      // Update the user's document URL field
      const updateField = `${docType}_url`;
      await userAPI.update(id, { [updateField]: docUrl });

      // Refresh user data
      await fetchUser();
      toast.success(`${docType.replace('_', ' ')} uploaded successfully`);
    } catch (error) {
      toast.error(`Failed to upload ${docType.replace('_', ' ')}`);
    } finally {
      setIsUploadingDoc(null);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not provided';
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const maskSensitiveData = (value, showLastN = 4) => {
    if (!value) return 'Not provided';
    if (value.length <= showLastN) return value;
    return '*'.repeat(value.length - showLastN) + value.slice(-showLastN);
  };

  const visaStatusLabels = {
    citizen: 'Australian Citizen',
    permanent_resident: 'Permanent Resident',
    temporary_resident: 'Temporary Resident',
    working_holiday: 'Working Holiday Visa',
    student: 'Student Visa',
    other: 'Other Visa',
  };

  if (isLoading) {
    return (
      <DashboardLayout title="User Details">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  if (!userData) {
    return (
      <DashboardLayout title="User Details">
        <div className="text-center py-12">
          <p className="text-gray-500">User not found</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="User Details">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            icon={ArrowLeftIcon}
            onClick={() => navigate('/users')}
          >
            Back to Users
          </Button>
          {isStaff && (userData?.role === 'user' || userData?.role === 'external_accountant') && (
            <Button
              variant="secondary"
              icon={PencilSquareIcon}
              onClick={openEditModal}
            >
              Edit Details
            </Button>
          )}
        </div>

        {/* User Header Card */}
        <Card>
          <div className="flex items-start gap-6">
            <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center">
              <UserIcon className="w-8 h-8 text-primary-600" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3">
                <h2 className="text-2xl font-semibold text-gray-900">
                  {userData.full_name || 'No Name'}
                </h2>
                <RoleBadge role={userData.role} />
                <Badge status={userData.is_active ? 'active' : 'inactive'}>
                  {userData.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              <p className="text-gray-500 mt-1">{userData.email}</p>
              <div className="flex gap-4 mt-3 text-sm text-gray-500">
                <span>Joined: {formatDate(userData.created_at)}</span>
                {userData.last_login && (
                  <span>Last login: {formatDate(userData.last_login)}</span>
                )}
              </div>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Personal Information */}
          <Card>
            <CardHeader title="Personal Information" />
            <div className="space-y-4">
              <InfoRow
                icon={UserIcon}
                label="Full Name"
                value={`${userData.first_name || ''} ${userData.last_name || ''}`.trim() || 'Not provided'}
              />
              <InfoRow
                icon={EnvelopeIcon}
                label="Email"
                value={userData.email}
              />
              <InfoRow
                icon={EnvelopeIcon}
                label="Personal Email"
                value={userData.personal_email || 'Not provided'}
              />
              <InfoRow
                icon={PhoneIcon}
                label="Phone"
                value={userData.phone || 'Not provided'}
              />
              <InfoRow
                icon={MapPinIcon}
                label="Address"
                value={userData.address || 'Not provided'}
              />
              <InfoRow
                icon={CalendarIcon}
                label="Date of Birth"
                value={formatDate(userData.date_of_birth)}
              />
              <InfoRow
                icon={BriefcaseIcon}
                label="Occupation"
                value={userData.occupation || 'Not provided'}
              />
              <InfoRow
                icon={BriefcaseIcon}
                label="Company/Business Name"
                value={userData.company_name || 'Not provided'}
              />
            </div>
          </Card>

          {/* Right column - different content based on user role */}
          {userData.role === 'user' ? (
            <Card>
              <CardHeader title="Tax & Visa Information" />
              <div className="space-y-4">
                <InfoRow
                  icon={DocumentTextIcon}
                  label="Visa Status"
                  value={visaStatusLabels[userData.visa_status] || userData.visa_status || 'Not provided'}
                />
                <InfoRow
                  icon={DocumentTextIcon}
                  label="Tax File Number (TFN)"
                  value={userData.tfn ? maskSensitiveData(userData.tfn, 3) : 'Not provided'}
                  sensitive
                />
                <InfoRow
                  icon={CheckBadgeIcon}
                  label="Terms Accepted"
                  value={userData.terms_accepted ? `Yes (${formatDate(userData.terms_accepted_at)})` : 'No'}
                />
                <InfoRow
                  icon={CheckBadgeIcon}
                  label="Onboarding Completed"
                  value={userData.is_first_login ? 'No' : 'Yes'}
                />
              </div>
            </Card>
          ) : (
            <Card>
              <CardHeader title="Account Status" />
              <div className="space-y-4">
                <InfoRow
                  icon={CheckBadgeIcon}
                  label="Account Status"
                  value={userData.is_active ? 'Active' : 'Inactive'}
                />
                <InfoRow
                  icon={CheckBadgeIcon}
                  label="Onboarding Completed"
                  value={userData.is_first_login ? 'No' : 'Yes'}
                />
                <InfoRow
                  icon={CheckBadgeIcon}
                  label="2FA Enabled"
                  value={userData.two_factor_enabled ? 'Yes' : 'No'}
                />
                <InfoRow
                  icon={CalendarIcon}
                  label="Last Login"
                  value={userData.last_login ? formatDate(userData.last_login) : 'Never'}
                />
                {userData.role === 'external_accountant' && (
                  <div className="mt-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
                    <p className="text-sm font-medium text-purple-800">B2B Client</p>
                    <p className="text-xs text-purple-600 mt-1">
                      External accountant receiving white-labeled services. No onboarding or tax documents required.
                    </p>
                  </div>
                )}
                {(userData.role === 'admin' || userData.role === 'accountant') && (
                  <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-sm font-medium text-blue-800">Staff Member</p>
                    <p className="text-xs text-blue-600 mt-1">
                      {userData.role === 'admin' ? 'Full administrative access to manage the company.' : 'Can manage client requests and provide services.'}
                    </p>
                  </div>
                )}
              </div>
            </Card>
          )}

          {/* Bank Details */}
          {isAdmin && (userData.bsb || userData.bank_account_number) && (
            <Card>
              <CardHeader title="Bank Account Details" />
              <div className="space-y-4">
                <InfoRow
                  icon={BanknotesIcon}
                  label="Account Holder Name"
                  value={userData.bank_account_holder_name || 'Not provided'}
                />
                <InfoRow
                  icon={BanknotesIcon}
                  label="BSB"
                  value={userData.bsb || 'Not provided'}
                />
                <InfoRow
                  icon={BanknotesIcon}
                  label="Account Number"
                  value={userData.bank_account_number ? maskSensitiveData(userData.bank_account_number, 4) : 'Not provided'}
                  sensitive
                />
              </div>
            </Card>
          )}

          {/* Onboarding Documents - Only show for client users */}
          {isStaff && userData.role === 'user' && (
            <Card>
              <CardHeader title="Onboarding Documents" />
              <div className="space-y-4">
                <DocumentRow
                  label="Passport"
                  url={userData.passport_url}
                  docType="passport"
                  isAdmin={isAdmin}
                  isUploading={isUploadingDoc === 'passport'}
                  onUpload={handleDocumentUpload}
                  onView={(url, label) => setViewingDoc({ url, label })}
                />
                <DocumentRow
                  label="Driving Licence"
                  url={userData.driving_licence_url}
                  docType="driving_licence"
                  isAdmin={isAdmin}
                  isUploading={isUploadingDoc === 'driving_licence'}
                  onUpload={handleDocumentUpload}
                  onView={(url, label) => setViewingDoc({ url, label })}
                />
                <DocumentRow
                  label="Bank Statement"
                  url={userData.bank_statement_url}
                  docType="bank_statement"
                  isAdmin={isAdmin}
                  isUploading={isUploadingDoc === 'bank_statement'}
                  onUpload={handleDocumentUpload}
                  onView={(url, label) => setViewingDoc({ url, label })}
                />
                <DocumentRow
                  label="ID Document"
                  url={userData.id_document_url}
                  docType="id_document"
                  isAdmin={isAdmin}
                  isUploading={isUploadingDoc === 'id_document'}
                  onUpload={handleDocumentUpload}
                  onView={(url, label) => setViewingDoc({ url, label })}
                />
              </div>
            </Card>
          )}
        </div>

        {/* Service Requests Link - Show for clients and external accountants (B2B clients) */}
        {(userData.role === 'user' || userData.role === 'external_accountant') && (
          <Card>
            <CardHeader title="Service Requests" />
            <p className="text-gray-600 mb-4">
              {userData.role === 'external_accountant'
                ? 'View all service requests for this external accountant (B2B client) or create a new request on their behalf.'
                : 'View all service requests submitted by this client or create a new request on their behalf.'}
            </p>
            <div className="flex gap-3">
              <Link to={`/requests?search=${encodeURIComponent(userData.email)}`}>
                <Button variant="secondary">
                  View Service Requests
                </Button>
              </Link>
              {isAdmin && (
                <Button
                  icon={PlusIcon}
                  onClick={() => setIsCreateRequestModalOpen(true)}
                >
                  Create Request
                </Button>
              )}
            </div>
          </Card>
        )}
      </div>

      {/* Create Request Modal */}
      <Modal
        isOpen={isCreateRequestModalOpen}
        onClose={() => {
          setIsCreateRequestModalOpen(false);
          setSelectedServices([]);
        }}
        title={`Create Request for ${userData?.full_name || 'User'}`}
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Select one or more services to create requests for this client.
          </p>

          <div className="max-h-80 overflow-y-auto space-y-2">
            {services.map((service) => (
              <label
                key={service.id}
                className={`flex items-center p-3 border rounded-lg cursor-pointer transition-colors ${
                  selectedServices.includes(service.id)
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <input
                  type="checkbox"
                  checked={selectedServices.includes(service.id)}
                  onChange={() => handleServiceToggle(service.id)}
                  className="h-4 w-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                />
                <div className="ml-3 flex-1">
                  <p className="font-medium text-gray-900">{service.name}</p>
                  {service.description && (
                    <p className="text-sm text-gray-500">{service.description}</p>
                  )}
                </div>
                {service.base_price && (
                  <span className="text-sm font-medium text-gray-600">
                    ${service.base_price}
                  </span>
                )}
              </label>
            ))}
          </div>

          {services.length === 0 && (
            <p className="text-center text-gray-500 py-4">No services available</p>
          )}

          <div className="flex justify-end gap-3 pt-4 border-t">
            <Button
              variant="secondary"
              onClick={() => {
                setIsCreateRequestModalOpen(false);
                setSelectedServices([]);
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleCreateRequest}
              loading={isCreatingRequest}
              disabled={selectedServices.length === 0}
            >
              Create {selectedServices.length > 0 ? `${selectedServices.length} Request(s)` : 'Request'}
            </Button>
          </div>
        </div>
      </Modal>

      {/* Edit User Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit User Details"
        size="lg"
      >
        <div className="space-y-4 max-h-[60vh] overflow-y-auto">
          <h3 className="font-medium text-gray-900">Personal Information</h3>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="First Name"
              value={editData.first_name}
              onChange={(e) => setEditData({ ...editData, first_name: e.target.value })}
            />
            <Input
              label="Last Name"
              value={editData.last_name}
              onChange={(e) => setEditData({ ...editData, last_name: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Phone"
              value={editData.phone}
              onChange={(e) => setEditData({ ...editData, phone: e.target.value })}
            />
            <Input
              label="Personal Email"
              value={editData.personal_email}
              onChange={(e) => setEditData({ ...editData, personal_email: e.target.value })}
            />
          </div>
          <Input
            label="Address"
            value={editData.address}
            onChange={(e) => setEditData({ ...editData, address: e.target.value })}
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              type="date"
              label="Date of Birth"
              value={editData.date_of_birth}
              onChange={(e) => setEditData({ ...editData, date_of_birth: e.target.value })}
            />
            <Input
              label="Occupation"
              value={editData.occupation}
              onChange={(e) => setEditData({ ...editData, occupation: e.target.value })}
            />
          </div>
          <Input
            label="Company/Business Name"
            value={editData.company_name}
            onChange={(e) => setEditData({ ...editData, company_name: e.target.value })}
          />

          {/* Tax & Visa Information - Only show for client users */}
          {userData.role === 'user' && (
            <>
              <h3 className="font-medium text-gray-900 pt-4 border-t">Tax & Visa Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Tax File Number (TFN)"
                  value={editData.tfn}
                  onChange={(e) => setEditData({ ...editData, tfn: e.target.value })}
                />
                <Select
                  label="Visa Status"
                  options={[
                    { value: '', label: 'Select...' },
                    { value: 'citizen', label: 'Australian Citizen' },
                    { value: 'permanent_resident', label: 'Permanent Resident' },
                    { value: 'temporary_resident', label: 'Temporary Resident' },
                    { value: 'working_holiday', label: 'Working Holiday Visa' },
                    { value: 'student', label: 'Student Visa' },
                    { value: 'other', label: 'Other Visa' },
                  ]}
                  value={editData.visa_status}
                  onChange={(e) => setEditData({ ...editData, visa_status: e.target.value })}
                />
              </div>

              <h3 className="font-medium text-gray-900 pt-4 border-t">Bank Account Details</h3>
              <Input
                label="Account Holder Name"
                value={editData.bank_account_holder_name}
                onChange={(e) => setEditData({ ...editData, bank_account_holder_name: e.target.value })}
              />
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="BSB"
                  value={editData.bsb}
                  onChange={(e) => setEditData({ ...editData, bsb: e.target.value })}
                />
                <Input
                  label="Account Number"
                  value={editData.bank_account_number}
                  onChange={(e) => setEditData({ ...editData, bank_account_number: e.target.value })}
                />
              </div>
            </>
          )}
        </div>

        <div className="flex justify-end gap-2 pt-4 mt-4 border-t">
          <Button variant="secondary" onClick={() => setIsEditModalOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleEditSubmit} loading={isEditing}>
            Save Changes
          </Button>
        </div>
      </Modal>

      {/* Document Viewer Modal */}
      {viewingDoc && (
        <DocumentViewer
          docUrl={viewingDoc.url}
          label={viewingDoc.label}
          onClose={() => setViewingDoc(null)}
        />
      )}
    </DashboardLayout>
  );
}

function InfoRow({ icon: Icon, label, value, sensitive = false }) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
        <Icon className="w-4 h-4 text-gray-500" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-500">{label}</p>
        <p className={`font-medium ${sensitive ? 'font-mono' : ''} ${value === 'Not provided' ? 'text-gray-400' : 'text-gray-900'}`}>
          {value}
        </p>
      </div>
    </div>
  );
}

function DocumentRow({ label, url, docType, isAdmin, isUploading, onUpload, onView }) {
  const fileInputRef = React.useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onUpload(docType, file);
    }
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-3">
        <DocumentTextIcon className="w-5 h-5 text-gray-500" />
        <span className="font-medium text-gray-700">{label}</span>
      </div>
      <div className="flex items-center gap-2">
        {url ? (
          <button
            onClick={() => onView(url, label)}
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            View
          </button>
        ) : (
          <span className="text-gray-400 text-sm">Not uploaded</span>
        )}
        {isAdmin && (
          <>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="text-sm text-primary-600 hover:text-primary-700 font-medium disabled:opacity-50"
            >
              {isUploading ? 'Uploading...' : url ? 'Replace' : 'Upload'}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
