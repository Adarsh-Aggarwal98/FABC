import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import {
  UserIcon,
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  BriefcaseIcon,
  CalendarIcon,
  DocumentTextIcon,
  BanknotesIcon,
  PencilSquareIcon,
  CheckIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { Select } from '../../components/common/Input';
import { userAPI, documentsAPI } from '../../services/api';
import DocumentViewer from '../../components/common/DocumentViewer';
import useAuthStore from '../../store/authStore';

export default function MyProfile() {
  const { user: currentUser, updateUser } = useAuthStore();
  const [userData, setUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [editData, setEditData] = useState({});
  const [isUploadingDoc, setIsUploadingDoc] = useState(null);
  const [viewingDoc, setViewingDoc] = useState(null); // { url, label }

  useEffect(() => {
    fetchProfile();
  }, [currentUser?.id]);

  const fetchProfile = async () => {
    if (!currentUser?.id) return;
    setIsLoading(true);
    try {
      const response = await userAPI.get(currentUser.id);
      setUserData(response.data.data.user);
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setIsLoading(false);
    }
  };

  const startEditing = () => {
    setEditData({
      first_name: userData?.first_name || '',
      last_name: userData?.last_name || '',
      phone: userData?.phone || '',
      personal_email: userData?.personal_email || '',
      address: userData?.address || '',
      date_of_birth: userData?.date_of_birth || '',
      occupation: userData?.occupation || '',
      company_name: userData?.company_name || '',
      visa_status: userData?.visa_status || '',
    });
    setIsEditing(true);
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setEditData({});
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await userAPI.updateProfile(editData);
      setUserData(response.data.data.user);
      updateUser(response.data.data.user);
      setIsEditing(false);
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDocumentUpload = async (docType, file) => {
    if (!file) return;
    setIsUploadingDoc(docType);
    try {
      const uploadResponse = await documentsAPI.upload(file, null, docType, `${docType} upload`);
      const docId = uploadResponse.data.document?.id || uploadResponse.data.document?.file_url;

      await userAPI.updateProfile({ [`${docType}_url`]: docId });
      await fetchProfile();
      toast.success(`${docType.replace(/_/g, ' ')} uploaded successfully`);
    } catch (error) {
      toast.error(`Failed to upload ${docType.replace(/_/g, ' ')}`);
    } finally {
      setIsUploadingDoc(null);
    }
  };

  const handleViewDocument = (docUrl, label) => {
    if (!docUrl) return;
    setViewingDoc({ url: docUrl, label });
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Not provided';
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric', month: 'long', day: 'numeric',
    });
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
      <DashboardLayout title="My Profile">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  if (!userData) {
    return (
      <DashboardLayout title="My Profile">
        <div className="text-center py-12">
          <p className="text-gray-500">Could not load profile</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="My Profile">
      <div className="space-y-6">
        {/* Header Card */}
        <Card>
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-6">
              <div className="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center">
                <UserIcon className="w-8 h-8 text-primary-600" />
              </div>
              <div>
                <h2 className="text-2xl font-semibold text-gray-900">
                  {userData.full_name || 'No Name'}
                </h2>
                <p className="text-gray-500 mt-1">{userData.email}</p>
                <p className="text-sm text-gray-400 mt-1 capitalize">
                  {userData.role?.replace(/_/g, ' ')}
                </p>
              </div>
            </div>
            {!isEditing ? (
              <Button variant="secondary" icon={PencilSquareIcon} onClick={startEditing}>
                Edit Profile
              </Button>
            ) : (
              <div className="flex gap-2">
                <Button variant="secondary" icon={XMarkIcon} onClick={cancelEditing}>
                  Cancel
                </Button>
                <Button icon={CheckIcon} onClick={handleSave} loading={isSaving}>
                  Save
                </Button>
              </div>
            )}
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Personal Information */}
          <Card>
            <CardHeader title="Personal Information" />
            {isEditing ? (
              <div className="space-y-4">
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
                {userData.role === 'user' && (
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
                )}
              </div>
            ) : (
              <div className="space-y-4">
                <InfoRow icon={UserIcon} label="Full Name" value={`${userData.first_name || ''} ${userData.last_name || ''}`.trim() || 'Not provided'} />
                <InfoRow icon={EnvelopeIcon} label="Email" value={userData.email} />
                <InfoRow icon={EnvelopeIcon} label="Personal Email" value={userData.personal_email || 'Not provided'} />
                <InfoRow icon={PhoneIcon} label="Phone" value={userData.phone || 'Not provided'} />
                <InfoRow icon={MapPinIcon} label="Address" value={userData.address || 'Not provided'} />
                <InfoRow icon={CalendarIcon} label="Date of Birth" value={formatDate(userData.date_of_birth)} />
                <InfoRow icon={BriefcaseIcon} label="Occupation" value={userData.occupation || 'Not provided'} />
                <InfoRow icon={BriefcaseIcon} label="Company/Business Name" value={userData.company_name || 'Not provided'} />
                {userData.role === 'user' && (
                  <InfoRow icon={DocumentTextIcon} label="Visa Status" value={visaStatusLabels[userData.visa_status] || userData.visa_status || 'Not provided'} />
                )}
              </div>
            )}
          </Card>

          {/* Bank Details - Only for client users */}
          {userData.role === 'user' && (
            <Card>
              <CardHeader title="Bank Account Details" />
              <div className="space-y-4">
                <InfoRow icon={BanknotesIcon} label="Account Holder" value={userData.bank_account_holder_name || 'Not provided'} />
                <InfoRow icon={BanknotesIcon} label="BSB" value={userData.bsb || 'Not provided'} />
                <InfoRow icon={BanknotesIcon} label="Account Number" value={userData.bank_account_number || 'Not provided'} />
              </div>
            </Card>
          )}

          {/* Documents */}
          {userData.role === 'user' && (
            <Card>
              <CardHeader title="My Documents" />
              <div className="space-y-4">
                <DocumentRow
                  label="Passport"
                  url={userData.passport_url}
                  docType="passport"
                  isUploading={isUploadingDoc === 'passport'}
                  onUpload={handleDocumentUpload}
                  onView={handleViewDocument}
                />
                <DocumentRow
                  label="Driving Licence"
                  url={userData.driving_licence_url}
                  docType="driving_licence"
                  isUploading={isUploadingDoc === 'driving_licence'}
                  onUpload={handleDocumentUpload}
                  onView={handleViewDocument}
                />
                <DocumentRow
                  label="Bank Statement"
                  url={userData.bank_statement_url}
                  docType="bank_statement"
                  isUploading={isUploadingDoc === 'bank_statement'}
                  onUpload={handleDocumentUpload}
                  onView={handleViewDocument}
                />
                <DocumentRow
                  label="ID Document"
                  url={userData.id_document_url}
                  docType="id_document"
                  isUploading={isUploadingDoc === 'id_document'}
                  onUpload={handleDocumentUpload}
                  onView={handleViewDocument}
                />
              </div>
            </Card>
          )}

          {/* Account Info */}
          <Card>
            <CardHeader title="Account Information" />
            <div className="space-y-4">
              <InfoRow icon={CalendarIcon} label="Member Since" value={formatDate(userData.created_at)} />
              <InfoRow icon={CalendarIcon} label="Last Login" value={userData.last_login ? formatDate(userData.last_login) : 'N/A'} />
            </div>
          </Card>
        </div>
      </div>

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

function InfoRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-3">
      <div className="w-8 h-8 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
        <Icon className="w-4 h-4 text-gray-500" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-gray-500">{label}</p>
        <p className={`font-medium ${value === 'Not provided' || value === 'N/A' ? 'text-gray-400' : 'text-gray-900'}`}>
          {value}
        </p>
      </div>
    </div>
  );
}

function DocumentRow({ label, url, docType, isUploading, onUpload, onView }) {
  const fileInputRef = React.useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) onUpload(docType, file);
    if (fileInputRef.current) fileInputRef.current.value = '';
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
      </div>
    </div>
  );
}
