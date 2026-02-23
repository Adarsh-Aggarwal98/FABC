import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  EnvelopeIcon,
  CloudIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
  Cog6ToothIcon,
  PaperAirplaneIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import { Select } from '../../components/common/Input';
import { companiesAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import useCompanyStore from '../../store/companyStore';

export default function EmailStorageSettings() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { company, fetchCompany } = useCompanyStore();
  const [activeTab, setActiveTab] = useState('email');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [testEmail, setTestEmail] = useState('');

  // Email config state
  const [emailConfig, setEmailConfig] = useState(null);
  const [providerOptions, setProviderOptions] = useState([]);
  const [providerSettings, setProviderSettings] = useState({});
  const [emailFormData, setEmailFormData] = useState({
    provider: 'GMAIL',
    is_enabled: false,
    smtp_host: '',
    smtp_port: 587,
    smtp_username: '',
    smtp_password: '',
    smtp_use_tls: true,
    smtp_use_ssl: false,
    sender_email: '',
    sender_name: '',
    reply_to_email: '',
  });

  // Storage config state
  const [storageConfig, setStorageConfig] = useState(null);
  const [storageProviderOptions, setStorageProviderOptions] = useState([]);
  const [storageFormData, setStorageFormData] = useState({
    provider: 'AZURE_BLOB',
    is_enabled: false,
    sharepoint_site_id: '',
    sharepoint_drive_id: '',
    sharepoint_root_folder: 'CRM_Documents',
    zoho_client_id: '',
    zoho_client_secret: '',
    zoho_root_folder_id: '',
    zoho_org_id: '',
    google_client_id: '',
    google_client_secret: '',
    google_root_folder_id: '',
    azure_connection_string: '',
    azure_container_name: '',
  });

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin';
  const isSuperAdmin = user?.role === 'super_admin';
  const companyId = company?.id;

  useEffect(() => {
    if (!isAdmin) {
      navigate('/dashboard');
      return;
    }

    // Fetch company if not loaded
    if (!company) {
      fetchCompany().catch(() => {
        toast.error('Failed to load company data');
      });
    }
  }, [isAdmin]);

  useEffect(() => {
    if (companyId) {
      fetchEmailConfig();
      fetchStorageConfig();
    } else if (company === null && !isLoading) {
      // Company explicitly null (not loading) - stop loading spinner
      setIsLoading(false);
    }
  }, [companyId]);

  const fetchEmailConfig = async () => {
    try {
      const response = await companiesAPI.getCompanyEmailConfig(companyId);
      const { config, provider_options, provider_settings } = response.data;

      setProviderOptions(provider_options || []);
      setProviderSettings(provider_settings || {});

      if (config) {
        setEmailConfig(config);
        setEmailFormData({
          provider: config.provider || 'GMAIL',
          is_enabled: config.is_enabled || false,
          smtp_host: config.smtp_host || '',
          smtp_port: config.smtp_port || 587,
          smtp_username: config.smtp_username || '',
          smtp_password: '',
          smtp_use_tls: config.smtp_use_tls !== false,
          smtp_use_ssl: config.smtp_use_ssl || false,
          sender_email: config.sender_email || '',
          sender_name: config.sender_name || '',
          reply_to_email: config.reply_to_email || '',
        });
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch email configuration');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStorageConfig = async () => {
    try {
      const response = await companiesAPI.getCompanyStorageConfig(companyId);
      const { config, provider_options } = response.data;

      setStorageProviderOptions(provider_options || []);

      if (config) {
        setStorageConfig(config);
        setStorageFormData({
          provider: config.provider || 'AZURE_BLOB',
          is_enabled: config.is_enabled || false,
          sharepoint_site_id: config.sharepoint_site_id || '',
          sharepoint_drive_id: config.sharepoint_drive_id || '',
          sharepoint_root_folder: config.sharepoint_root_folder || 'CRM_Documents',
          zoho_client_id: config.zoho_client_id || '',
          zoho_client_secret: '',
          zoho_root_folder_id: config.zoho_root_folder_id || '',
          zoho_org_id: config.zoho_org_id || '',
          google_client_id: config.google_client_id || '',
          google_client_secret: '',
          google_root_folder_id: config.google_root_folder_id || '',
          azure_connection_string: '',
          azure_container_name: config.azure_container_name || '',
        });
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch storage configuration');
    }
  };

  const handleProviderChange = (provider) => {
    const settings = providerSettings[provider] || {};
    setEmailFormData((prev) => ({
      ...prev,
      provider,
      smtp_host: settings.smtp_host || prev.smtp_host,
      smtp_port: settings.smtp_port || prev.smtp_port,
      smtp_use_tls: settings.smtp_use_tls !== undefined ? settings.smtp_use_tls : prev.smtp_use_tls,
      smtp_use_ssl: settings.smtp_use_ssl !== undefined ? settings.smtp_use_ssl : prev.smtp_use_ssl,
    }));
  };

  const saveEmailConfig = async () => {
    setIsSaving(true);
    try {
      const dataToSave = { ...emailFormData };
      // Only send password if it was changed
      if (!dataToSave.smtp_password) {
        delete dataToSave.smtp_password;
      }

      await companiesAPI.updateCompanyEmailConfig(companyId, dataToSave);
      toast.success('Email configuration saved successfully');
      fetchEmailConfig();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save email configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const testEmailConnection = async () => {
    setIsTesting(true);
    try {
      const response = await companiesAPI.testCompanyEmailConfig(companyId);
      if (response.data.success) {
        toast.success('Connection test successful!');
      } else {
        toast.error(response.data.message || 'Connection test failed');
      }
      fetchEmailConfig();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Connection test failed');
    } finally {
      setIsTesting(false);
    }
  };

  const sendTestEmailHandler = async () => {
    if (!testEmail) {
      toast.error('Please enter an email address');
      return;
    }
    setIsTesting(true);
    try {
      const response = await companiesAPI.sendTestEmail(companyId, { email: testEmail });
      if (response.data.success) {
        toast.success(response.data.message);
      } else {
        toast.error(response.data.error || 'Failed to send test email');
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to send test email');
    } finally {
      setIsTesting(false);
    }
  };

  const saveStorageConfig = async () => {
    setIsSaving(true);
    try {
      const dataToSave = { ...storageFormData };
      // Only send secrets if they were changed
      if (!dataToSave.zoho_client_secret) {
        delete dataToSave.zoho_client_secret;
      }
      if (!dataToSave.google_client_secret) {
        delete dataToSave.google_client_secret;
      }
      if (!dataToSave.azure_connection_string) {
        delete dataToSave.azure_connection_string;
      }

      await companiesAPI.updateCompanyStorageConfig(companyId, dataToSave);
      toast.success('Storage configuration saved successfully');
      fetchStorageConfig();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save storage configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const testStorageConnection = async () => {
    setIsTesting(true);
    try {
      const response = await companiesAPI.testCompanyStorageConfig(companyId);
      if (response.data.success) {
        toast.success(response.data.message || 'Connection test successful!');
      } else {
        toast.error(response.data.message || 'Connection test failed');
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Connection test failed');
    } finally {
      setIsTesting(false);
    }
  };

  const connectZohoDrive = async () => {
    try {
      const response = await companiesAPI.getZohoAuthUrl(companyId);
      if (response.data.success && response.data.auth_url) {
        window.location.href = response.data.auth_url;
      } else {
        toast.error('Failed to get Zoho authorization URL');
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to initiate Zoho connection');
    }
  };

  const connectGoogleDrive = async () => {
    try {
      const response = await companiesAPI.getGoogleAuthUrl(companyId);
      if (response.data.success && response.data.auth_url) {
        window.location.href = response.data.auth_url;
      } else {
        toast.error('Failed to get Google authorization URL');
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to initiate Google connection');
    }
  };

  const disconnectGoogleDrive = async () => {
    try {
      const response = await companiesAPI.disconnectGoogleDrive(companyId);
      if (response.data.success) {
        toast.success('Google Drive disconnected');
        fetchStorageConfig();
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to disconnect Google Drive');
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout title="Email & Storage Settings">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!companyId) {
    return (
      <DashboardLayout title="Email & Storage Settings">
        <div className="flex flex-col items-center justify-center h-64">
          <ExclamationTriangleIcon className="h-12 w-12 text-yellow-500 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Company Selected</h3>
          <p className="text-gray-500 text-center max-w-md">
            Email and storage settings are configured per company.
            {isSuperAdmin
              ? ' As a super admin, please go to Companies and select a company to configure.'
              : ' Please contact your administrator.'}
          </p>
          {isSuperAdmin && (
            <Button
              className="mt-4"
              onClick={() => navigate('/companies')}
            >
              Go to Companies
            </Button>
          )}
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      title="Email & Storage Settings"
      subtitle="Configure SMTP email and document storage providers"
    >
      {/* Back button */}
      <div className="mb-6">
        <Button
          variant="ghost"
          icon={ArrowLeftIcon}
          onClick={() => navigate('/settings')}
        >
          Back to Settings
        </Button>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('email')}
            className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === 'email'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <EnvelopeIcon className="h-5 w-5" />
            Email Configuration
          </button>
          <button
            onClick={() => setActiveTab('storage')}
            className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === 'storage'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <CloudIcon className="h-5 w-5" />
            Storage Configuration
          </button>
        </nav>
      </div>

      {/* Email Configuration Tab */}
      {activeTab === 'email' && (
        <div className="space-y-6">
          <Card>
            <CardHeader
              title="SMTP Email Configuration"
              subtitle="Configure Gmail, Outlook, or custom SMTP server for sending emails"
            />

            <div className="p-6 space-y-6">
              {/* Status indicator */}
              {emailConfig && (
                <div className={`p-4 rounded-lg flex items-center gap-3 ${
                  emailConfig.last_test_success
                    ? 'bg-green-50 border border-green-200'
                    : emailConfig.last_test_at
                    ? 'bg-red-50 border border-red-200'
                    : 'bg-gray-50 border border-gray-200'
                }`}>
                  {emailConfig.last_test_success ? (
                    <CheckCircleIcon className="h-6 w-6 text-green-600" />
                  ) : emailConfig.last_test_at ? (
                    <XCircleIcon className="h-6 w-6 text-red-600" />
                  ) : (
                    <ExclamationTriangleIcon className="h-6 w-6 text-gray-400" />
                  )}
                  <div>
                    <p className="font-medium">
                      {emailConfig.last_test_success
                        ? 'Configuration Verified'
                        : emailConfig.last_test_at
                        ? 'Configuration Error'
                        : 'Not Tested'}
                    </p>
                    {emailConfig.last_test_at && (
                      <p className="text-sm text-gray-600">
                        Last tested: {new Date(emailConfig.last_test_at).toLocaleString()}
                      </p>
                    )}
                    {emailConfig.last_error && (
                      <p className="text-sm text-red-600 mt-1">{emailConfig.last_error}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Enable toggle */}
              <div className="flex items-center justify-between">
                <div>
                  <label className="font-medium text-gray-900">Enable SMTP Email</label>
                  <p className="text-sm text-gray-500">
                    Use your own SMTP server instead of the system default
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailFormData.is_enabled}
                    onChange={(e) =>
                      setEmailFormData({ ...emailFormData, is_enabled: e.target.checked })
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              {/* Provider selection */}
              <Select
                label="Email Provider"
                value={emailFormData.provider}
                onChange={(e) => handleProviderChange(e.target.value)}
                options={[
                  { value: '', label: 'Select Provider' },
                  ...providerOptions,
                ]}
              />

              {/* SMTP Settings */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="SMTP Host"
                  value={emailFormData.smtp_host}
                  onChange={(e) =>
                    setEmailFormData({ ...emailFormData, smtp_host: e.target.value })
                  }
                  placeholder="smtp.gmail.com"
                />
                <Input
                  label="SMTP Port"
                  type="number"
                  value={emailFormData.smtp_port}
                  onChange={(e) =>
                    setEmailFormData({ ...emailFormData, smtp_port: parseInt(e.target.value) })
                  }
                  placeholder="587"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  label="Username / Email"
                  value={emailFormData.smtp_username}
                  onChange={(e) =>
                    setEmailFormData({ ...emailFormData, smtp_username: e.target.value })
                  }
                  placeholder="your-email@gmail.com"
                />
                <Input
                  label="Password / App Password"
                  type="password"
                  value={emailFormData.smtp_password}
                  onChange={(e) =>
                    setEmailFormData({ ...emailFormData, smtp_password: e.target.value })
                  }
                  placeholder="Enter password to change"
                />
              </div>

              {/* Security options */}
              <div className="flex items-center gap-6">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailFormData.smtp_use_tls}
                    onChange={(e) =>
                      setEmailFormData({ ...emailFormData, smtp_use_tls: e.target.checked })
                    }
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm">Use TLS (STARTTLS)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={emailFormData.smtp_use_ssl}
                    onChange={(e) =>
                      setEmailFormData({ ...emailFormData, smtp_use_ssl: e.target.checked })
                    }
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm">Use SSL</span>
                </label>
              </div>

              {/* Sender info */}
              <div className="border-t pt-4">
                <h4 className="font-medium text-gray-900 mb-4">Sender Information</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Sender Email"
                    type="email"
                    value={emailFormData.sender_email}
                    onChange={(e) =>
                      setEmailFormData({ ...emailFormData, sender_email: e.target.value })
                    }
                    placeholder="noreply@yourcompany.com"
                  />
                  <Input
                    label="Sender Name"
                    value={emailFormData.sender_name}
                    onChange={(e) =>
                      setEmailFormData({ ...emailFormData, sender_name: e.target.value })
                    }
                    placeholder="Your Company Name"
                  />
                </div>
                <div className="mt-4">
                  <Input
                    label="Reply-To Email (Optional)"
                    type="email"
                    value={emailFormData.reply_to_email}
                    onChange={(e) =>
                      setEmailFormData({ ...emailFormData, reply_to_email: e.target.value })
                    }
                    placeholder="support@yourcompany.com"
                  />
                </div>
              </div>

              {/* Gmail App Password Note */}
              {emailFormData.provider === 'GMAIL' && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h5 className="font-medium text-blue-800 mb-2">Gmail App Password Required</h5>
                  <p className="text-sm text-blue-700">
                    To use Gmail SMTP, you need to generate an App Password:
                  </p>
                  <ol className="text-sm text-blue-700 mt-2 list-decimal list-inside space-y-1">
                    <li>Enable 2-Step Verification on your Google Account</li>
                    <li>Go to Google Account &gt; Security &gt; App passwords</li>
                    <li>Generate a new app password for "Mail"</li>
                    <li>Use that 16-character password in the password field above</li>
                  </ol>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t">
                <div className="flex items-center gap-3">
                  <Button
                    variant="secondary"
                    icon={Cog6ToothIcon}
                    onClick={testEmailConnection}
                    loading={isTesting}
                    disabled={!emailFormData.smtp_host || !emailFormData.smtp_username}
                  >
                    Test Connection
                  </Button>
                </div>
                <Button onClick={saveEmailConfig} loading={isSaving}>
                  Save Configuration
                </Button>
              </div>

              {/* Send test email */}
              {emailConfig?.is_enabled && emailConfig?.last_test_success && (
                <div className="border-t pt-4">
                  <h4 className="font-medium text-gray-900 mb-4">Send Test Email</h4>
                  <div className="flex items-end gap-3">
                    <div className="flex-1">
                      <Input
                        label="Recipient Email"
                        type="email"
                        value={testEmail}
                        onChange={(e) => setTestEmail(e.target.value)}
                        placeholder="Enter email to send test"
                      />
                    </div>
                    <Button
                      icon={PaperAirplaneIcon}
                      onClick={sendTestEmailHandler}
                      loading={isTesting}
                      disabled={!testEmail}
                    >
                      Send Test
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Storage Configuration Tab */}
      {activeTab === 'storage' && (
        <div className="space-y-6">
          <Card>
            <CardHeader
              title="Document Storage Configuration"
              subtitle="Configure where documents are stored - Google Drive, SharePoint, Zoho Drive, or Azure Blob"
            />

            <div className="p-6 space-y-6">
              {/* Enable toggle */}
              <div className="flex items-center justify-between">
                <div>
                  <label className="font-medium text-gray-900">Enable Custom Storage</label>
                  <p className="text-sm text-gray-500">
                    Use your own storage provider for documents (default: Azure Blob Storage)
                  </p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={storageFormData.is_enabled}
                    onChange={(e) =>
                      setStorageFormData({ ...storageFormData, is_enabled: e.target.checked })
                    }
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>

              {/* Show provider options only when custom storage is enabled */}
              {storageFormData.is_enabled && (
                <>
                  {/* Provider selection */}
                  <Select
                    label="Storage Provider"
                    value={storageFormData.provider}
                    onChange={(e) =>
                      setStorageFormData({ ...storageFormData, provider: e.target.value })
                    }
                    options={[
                      { value: '', label: 'Select Provider' },
                      ...storageProviderOptions,
                    ]}
                  />

                  {/* Google Drive Settings */}
                  {storageFormData.provider === 'GOOGLE_DRIVE' && (
                    <div className="space-y-4 border-t pt-4">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-gray-900">Google Drive Settings</h4>
                        {storageConfig?.google_connected && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <CheckCircleIcon className="w-4 h-4 mr-1" />
                            Connected
                          </span>
                        )}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                          label="Client ID"
                          value={storageFormData.google_client_id}
                          onChange={(e) =>
                            setStorageFormData({ ...storageFormData, google_client_id: e.target.value })
                          }
                          placeholder="Google OAuth Client ID"
                        />
                        <Input
                          label="Client Secret"
                          type="password"
                          value={storageFormData.google_client_secret}
                          onChange={(e) =>
                            setStorageFormData({ ...storageFormData, google_client_secret: e.target.value })
                          }
                          placeholder="Enter to change"
                        />
                      </div>
                      <Input
                        label="Root Folder ID (Optional)"
                        value={storageFormData.google_root_folder_id}
                        onChange={(e) =>
                          setStorageFormData({ ...storageFormData, google_root_folder_id: e.target.value })
                        }
                        placeholder="Leave empty for root folder"
                        helperText="The folder ID where documents will be stored. Leave empty to use root."
                      />

                      {/* Google Drive Connect/Disconnect Button */}
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        {storageConfig?.google_connected ? (
                          <>
                            <p className="text-sm text-green-700 mb-3">
                              Google Drive is connected. You can disconnect and reconnect if needed.
                            </p>
                            <div className="flex gap-3">
                              <Button
                                variant="secondary"
                                onClick={connectGoogleDrive}
                                disabled={!storageConfig?.google_client_id}
                              >
                                Reconnect
                              </Button>
                              <Button
                                variant="danger"
                                onClick={disconnectGoogleDrive}
                              >
                                Disconnect
                              </Button>
                            </div>
                          </>
                        ) : (
                          <>
                            <p className="text-sm text-blue-700 mb-3">
                              Save your Client ID and Secret first, then click below to authorize access to your Google Drive account.
                            </p>
                            <Button
                              variant="secondary"
                              onClick={connectGoogleDrive}
                              disabled={!storageConfig?.google_client_id}
                            >
                              Connect Google Drive
                            </Button>
                          </>
                        )}
                      </div>

                      {/* Setup instructions */}
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <h5 className="font-medium text-gray-800 mb-2">Setup Instructions</h5>
                        <ol className="text-sm text-gray-600 list-decimal list-inside space-y-1">
                          <li>Go to <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Google Cloud Console</a></li>
                          <li>Create a new project or select an existing one</li>
                          <li>Enable the Google Drive API</li>
                          <li>Go to Credentials and create an OAuth 2.0 Client ID</li>
                          <li>Add your redirect URI: <code className="bg-gray-100 px-1 rounded">{window.location.origin}/settings/integrations/google/callback</code></li>
                          <li>Copy the Client ID and Client Secret here</li>
                        </ol>
                      </div>
                    </div>
                  )}

                  {/* SharePoint Settings */}
                  {storageFormData.provider === 'SHAREPOINT' && (
                    <div className="space-y-4 border-t pt-4">
                      <h4 className="font-medium text-gray-900">SharePoint Settings</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                          label="Site ID"
                          value={storageFormData.sharepoint_site_id}
                          onChange={(e) =>
                            setStorageFormData({ ...storageFormData, sharepoint_site_id: e.target.value })
                          }
                          placeholder="Enter SharePoint Site ID"
                        />
                        <Input
                          label="Drive ID"
                          value={storageFormData.sharepoint_drive_id}
                          onChange={(e) =>
                            setStorageFormData({ ...storageFormData, sharepoint_drive_id: e.target.value })
                          }
                          placeholder="Enter SharePoint Drive ID"
                        />
                      </div>
                      <Input
                        label="Root Folder"
                        value={storageFormData.sharepoint_root_folder}
                        onChange={(e) =>
                          setStorageFormData({ ...storageFormData, sharepoint_root_folder: e.target.value })
                        }
                        placeholder="CRM_Documents"
                      />

                      {/* Setup instructions */}
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <h5 className="font-medium text-gray-800 mb-2">How to find your IDs</h5>
                        <ol className="text-sm text-gray-600 list-decimal list-inside space-y-1">
                          <li>Go to your SharePoint site</li>
                          <li>Site ID can be found in the URL after /sites/</li>
                          <li>Use Microsoft Graph Explorer to find your Drive ID</li>
                        </ol>
                      </div>
                    </div>
                  )}

                  {/* Zoho Drive Settings */}
                  {storageFormData.provider === 'ZOHO_DRIVE' && (
                    <div className="space-y-4 border-t pt-4">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium text-gray-900">Zoho WorkDrive Settings</h4>
                        {storageConfig?.zoho_connected && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            <CheckCircleIcon className="w-4 h-4 mr-1" />
                            Connected
                          </span>
                        )}
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                          label="Client ID"
                          value={storageFormData.zoho_client_id}
                          onChange={(e) =>
                            setStorageFormData({ ...storageFormData, zoho_client_id: e.target.value })
                          }
                          placeholder="Zoho OAuth Client ID"
                        />
                        <Input
                          label="Client Secret"
                          type="password"
                          value={storageFormData.zoho_client_secret}
                          onChange={(e) =>
                            setStorageFormData({ ...storageFormData, zoho_client_secret: e.target.value })
                          }
                          placeholder="Enter to change"
                        />
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Input
                          label="Root Folder ID"
                          value={storageFormData.zoho_root_folder_id}
                          onChange={(e) =>
                            setStorageFormData({ ...storageFormData, zoho_root_folder_id: e.target.value })
                          }
                          placeholder="Zoho folder ID for documents"
                        />
                        <Input
                          label="Organization ID (Optional)"
                          value={storageFormData.zoho_org_id}
                          onChange={(e) =>
                            setStorageFormData({ ...storageFormData, zoho_org_id: e.target.value })
                          }
                          placeholder="Zoho Org ID"
                        />
                      </div>

                      {/* Zoho Connect Button */}
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        {storageConfig?.zoho_connected ? (
                          <p className="text-sm text-green-700 mb-3">
                            Zoho WorkDrive is connected. You can reconnect if needed.
                          </p>
                        ) : (
                          <p className="text-sm text-blue-700 mb-3">
                            Save your Client ID and Secret first, then click below to authorize access to your Zoho WorkDrive account.
                          </p>
                        )}
                        <Button
                          variant="secondary"
                          onClick={connectZohoDrive}
                          disabled={!storageConfig?.zoho_client_id}
                        >
                          {storageConfig?.zoho_connected ? 'Reconnect' : 'Connect'} Zoho WorkDrive
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Azure Blob Settings */}
                  {storageFormData.provider === 'AZURE_BLOB' && (
                    <div className="space-y-4 border-t pt-4">
                      <h4 className="font-medium text-gray-900">Azure Blob Storage Settings</h4>
                      <p className="text-sm text-gray-500">
                        Configure your own Azure Blob Storage account for document storage.
                      </p>
                      <Input
                        label="Connection String"
                        type="password"
                        value={storageFormData.azure_connection_string}
                        onChange={(e) =>
                          setStorageFormData({ ...storageFormData, azure_connection_string: e.target.value })
                        }
                        placeholder="Enter connection string to change"
                        helperText="Found in Azure Portal → Storage Account → Access Keys"
                      />
                      <Input
                        label="Container Name"
                        value={storageFormData.azure_container_name}
                        onChange={(e) =>
                          setStorageFormData({ ...storageFormData, azure_container_name: e.target.value })
                        }
                        placeholder="e.g., crm-documents"
                        helperText="The container will be created if it doesn't exist"
                      />

                      {/* Setup instructions */}
                      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <h5 className="font-medium text-gray-800 mb-2">Setup Instructions</h5>
                        <ol className="text-sm text-gray-600 list-decimal list-inside space-y-1">
                          <li>Go to <a href="https://portal.azure.com/" target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">Azure Portal</a></li>
                          <li>Create a Storage Account or use an existing one</li>
                          <li>Go to Access Keys and copy the Connection String</li>
                          <li>Enter the connection string and desired container name above</li>
                        </ol>
                      </div>
                    </div>
                  )}
                </>
              )}

              {/* Info when custom storage is disabled */}
              {!storageFormData.is_enabled && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <p className="text-sm text-gray-600">
                    Custom storage is disabled. Documents will be stored using the default Azure Blob Storage configured by your administrator.
                  </p>
                </div>
              )}

              {/* Actions */}
              <div className="flex items-center justify-between pt-4 border-t">
                {storageFormData.is_enabled && (
                  <Button
                    variant="secondary"
                    icon={Cog6ToothIcon}
                    onClick={testStorageConnection}
                    loading={isTesting}
                    disabled={!storageFormData.provider}
                  >
                    Test Connection
                  </Button>
                )}
                {!storageFormData.is_enabled && <div />}
                <Button onClick={saveStorageConfig} loading={isSaving}>
                  Save Configuration
                </Button>
              </div>
            </div>
          </Card>
        </div>
      )}
    </DashboardLayout>
  );
}
