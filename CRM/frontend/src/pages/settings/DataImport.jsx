import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
  XCircleIcon,
  InformationCircleIcon,
  BuildingOfficeIcon,
  UsersIcon,
  ClipboardDocumentListIcon,
  CubeIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import { Select } from '../../components/common/Input';
import { importsAPI, companiesAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

const DATA_TYPE_ICONS = {
  clients: UsersIcon,
  service_requests: ClipboardDocumentListIcon,
  services: CubeIcon,
  companies: BuildingOfficeIcon,
};

export default function DataImport() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const fileInputRef = useRef(null);

  const [importTypes, setImportTypes] = useState([]);
  const [selectedType, setSelectedType] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [importResults, setImportResults] = useState(null);
  const [companies, setCompanies] = useState([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [isLoadingCompanies, setIsLoadingCompanies] = useState(false);
  const [isLoadingTypes, setIsLoadingTypes] = useState(true);

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin';
  const isSuperAdmin = user?.role === 'super_admin';

  // Fetch available import types
  useEffect(() => {
    fetchImportTypes();
  }, []);

  // Fetch companies for super admin
  useEffect(() => {
    if (isSuperAdmin) {
      fetchCompanies();
    }
  }, [isSuperAdmin]);

  const fetchImportTypes = async () => {
    setIsLoadingTypes(true);
    try {
      const response = await importsAPI.getTypes();
      // API returns { success, data: { types: [...] } }
      const types = response.data.data?.types || response.data.types || [];
      setImportTypes(types);
      if (types.length > 0) {
        setSelectedType(types[0].id);
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load import types');
    } finally {
      setIsLoadingTypes(false);
    }
  };

  const fetchCompanies = async () => {
    setIsLoadingCompanies(true);
    try {
      const response = await companiesAPI.list({ per_page: 100 });
      // Handle both response structures
      const companiesData = response.data.data?.companies || response.data.companies || [];
      setCompanies(companiesData);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load companies');
    } finally {
      setIsLoadingCompanies(false);
    }
  };

  if (!isAdmin) {
    navigate('/dashboard');
    return null;
  }

  const selectedTypeInfo = importTypes.find(t => t.id === selectedType);

  const handleDownloadTemplate = async () => {
    if (!selectedType) {
      toast.error('Please select a data type first');
      return;
    }

    try {
      const response = await importsAPI.downloadTemplate(selectedType);
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${selectedType}_import_template.csv`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      toast.success('Template downloaded successfully');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to download template');
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.csv')) {
      toast.error('Please select a CSV file');
      return;
    }

    setSelectedFile(file);
    setImportResults(null);
  };

  const handleImport = async () => {
    if (!selectedFile) {
      toast.error('Please select a file first');
      return;
    }

    if (!selectedType) {
      toast.error('Please select a data type');
      return;
    }

    // Company selection required for certain types when super admin
    const requiresCompany = ['clients', 'service_requests'].includes(selectedType);
    if (isSuperAdmin && requiresCompany && !selectedCompanyId) {
      toast.error('Please select a company to import data into');
      return;
    }

    setIsUploading(true);
    setImportResults(null);

    try {
      let response;
      const companyId = isSuperAdmin ? selectedCompanyId : null;

      switch (selectedType) {
        case 'clients':
          response = await importsAPI.importClients(selectedFile, companyId);
          break;
        case 'service_requests':
          response = await importsAPI.importServiceRequests(selectedFile, companyId);
          break;
        case 'services':
          response = await importsAPI.importServices(selectedFile);
          break;
        case 'companies':
          response = await importsAPI.importCompanies(selectedFile);
          break;
        default:
          throw new Error('Unknown import type');
      }

      // API returns { success, data: { results, message, ... } }
      const resultData = response.data.data || response.data;
      setImportResults(resultData);

      if (resultData.results?.imported > 0 || resultData.results?.updated > 0) {
        toast.success(resultData.message);
      } else {
        toast.error('No records were imported. Check the errors below.');
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Import failed');
    } finally {
      setIsUploading(false);
    }
  };

  const handleClearFile = () => {
    setSelectedFile(null);
    setImportResults(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const TypeIcon = selectedType ? DATA_TYPE_ICONS[selectedType] || DocumentTextIcon : DocumentTextIcon;

  return (
    <DashboardLayout title="Import Data">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            icon={ArrowLeftIcon}
            onClick={() => navigate('/users')}
          >
            Back to Users
          </Button>
        </div>

        {/* Data Type Selection */}
        <Card>
          <CardHeader
            title="Select Data Type"
            subtitle="Choose what type of data you want to import"
          />

          {isLoadingTypes ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {importTypes.map((type) => {
                const Icon = DATA_TYPE_ICONS[type.id] || DocumentTextIcon;
                const isSelected = selectedType === type.id;
                return (
                  <button
                    key={type.id}
                    onClick={() => {
                      setSelectedType(type.id);
                      setSelectedFile(null);
                      setImportResults(null);
                    }}
                    className={`p-4 rounded-lg border-2 text-left transition-all ${
                      isSelected
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Icon className={`h-8 w-8 mb-2 ${isSelected ? 'text-primary-600' : 'text-gray-400'}`} />
                    <h3 className={`font-medium ${isSelected ? 'text-primary-900' : 'text-gray-900'}`}>
                      {type.name}
                    </h3>
                    <p className="text-sm text-gray-500 mt-1">{type.description}</p>
                  </button>
                );
              })}
            </div>
          )}
        </Card>

        {selectedTypeInfo && (
          <>
            {/* Instructions Card */}
            <Card>
              <CardHeader
                title={`Import ${selectedTypeInfo.name}`}
                subtitle={selectedTypeInfo.description}
              />

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <div className="flex gap-3">
                  <InformationCircleIcon className="h-6 w-6 text-blue-600 flex-shrink-0" />
                  <div className="text-sm text-blue-800">
                    <p className="font-medium mb-2">How to import {selectedTypeInfo.name.toLowerCase()}:</p>
                    <ol className="list-decimal list-inside space-y-1">
                      <li>Download the CSV template below</li>
                      <li>Fill in your data following the template format</li>
                      <li>Save the file and upload it here</li>
                      <li>Review the results and fix any errors</li>
                    </ol>
                  </div>
                </div>
              </div>

              {/* Template Download */}
              <div className="border rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <TypeIcon className="h-6 w-6 text-green-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">Download CSV Template</p>
                      <p className="text-sm text-gray-500">
                        Get the template with sample data and all supported columns
                      </p>
                    </div>
                  </div>
                  <Button
                    variant="secondary"
                    icon={ArrowDownTrayIcon}
                    onClick={handleDownloadTemplate}
                  >
                    Download Template
                  </Button>
                </div>
              </div>

              {/* Supported Fields */}
              <div className="mb-6">
                <p className="text-sm font-medium text-gray-700 mb-2">Required Fields:</p>
                <div className="flex flex-wrap gap-2 mb-3">
                  {selectedTypeInfo.required_columns.map((col) => (
                    <code key={col} className="bg-red-50 text-red-700 px-2 py-1 rounded text-sm">
                      {col} *
                    </code>
                  ))}
                </div>
                <p className="text-sm font-medium text-gray-700 mb-2">Optional Fields:</p>
                <div className="flex flex-wrap gap-2">
                  {selectedTypeInfo.optional_columns.map((col) => (
                    <code key={col} className="bg-gray-100 px-2 py-1 rounded text-sm">
                      {col}
                    </code>
                  ))}
                </div>
              </div>
            </Card>

            {/* Company Selection for Super Admin (for client and request imports) */}
            {isSuperAdmin && ['clients', 'service_requests'].includes(selectedType) && (
              <Card>
                <CardHeader
                  title="Select Target Company"
                  subtitle="Choose which company to import data into"
                />
                <div className="flex items-center gap-4">
                  <BuildingOfficeIcon className="h-8 w-8 text-gray-400" />
                  <div className="flex-1">
                    <Select
                      value={selectedCompanyId}
                      onChange={(e) => setSelectedCompanyId(e.target.value)}
                      disabled={isLoadingCompanies}
                      options={[
                        { value: '', label: 'Select a company...' },
                        ...companies.map((company) => ({
                          value: company.id,
                          label: `${company.name}${company.trading_name ? ` (${company.trading_name})` : ''}`
                        }))
                      ]}
                    />
                    {!selectedCompanyId && (
                      <p className="text-sm text-amber-600 mt-2">
                        You must select a company before importing
                      </p>
                    )}
                  </div>
                </div>
              </Card>
            )}

            {/* Upload Card */}
            <Card>
              <CardHeader
                title="Upload CSV File"
                subtitle="Select your completed CSV file to import"
              />

              <div className="space-y-4">
                {/* File Input */}
                <div
                  className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                    selectedFile
                      ? 'border-primary-300 bg-primary-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    accept=".csv"
                    className="hidden"
                  />

                  {selectedFile ? (
                    <div className="space-y-3">
                      <div className="flex items-center justify-center gap-2">
                        <DocumentTextIcon className="h-8 w-8 text-primary-600" />
                        <span className="font-medium text-gray-900">{selectedFile.name}</span>
                      </div>
                      <p className="text-sm text-gray-500">
                        {(selectedFile.size / 1024).toFixed(1)} KB
                      </p>
                      <div className="flex items-center justify-center gap-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={handleClearFile}
                        >
                          Remove
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => fileInputRef.current?.click()}
                        >
                          Change File
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      <ArrowUpTrayIcon className="h-12 w-12 text-gray-400 mx-auto" />
                      <div>
                        <Button
                          variant="secondary"
                          onClick={() => fileInputRef.current?.click()}
                        >
                          Select CSV File
                        </Button>
                      </div>
                      <p className="text-sm text-gray-500">
                        or drag and drop your file here
                      </p>
                    </div>
                  )}
                </div>

                {/* Import Button */}
                {selectedFile && !importResults && (
                  <div className="flex justify-end">
                    <Button
                      onClick={handleImport}
                      loading={isUploading}
                      icon={ArrowUpTrayIcon}
                    >
                      Import {selectedTypeInfo.name}
                    </Button>
                  </div>
                )}
              </div>
            </Card>

            {/* Results Card */}
            {importResults && (
              <Card>
                <CardHeader
                  title="Import Results"
                  subtitle="Summary of the import operation"
                />

                {/* Summary Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-50 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-gray-900">
                      {importResults.results.total}
                    </p>
                    <p className="text-sm text-gray-500">Total Rows</p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {importResults.results.imported}
                    </p>
                    <p className="text-sm text-green-600">Imported</p>
                  </div>
                  {importResults.results.updated !== undefined && (
                    <div className="bg-blue-50 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-blue-600">
                        {importResults.results.updated}
                      </p>
                      <p className="text-sm text-blue-600">Updated</p>
                    </div>
                  )}
                  <div className="bg-red-50 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-red-600">
                      {importResults.results.skipped}
                    </p>
                    <p className="text-sm text-red-600">Skipped</p>
                  </div>
                </div>

                {/* Success Message */}
                {(importResults.results.imported > 0 || importResults.results.updated > 0) && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
                    <div className="flex items-center gap-2">
                      <CheckCircleIcon className="h-5 w-5 text-green-600" />
                      <p className="text-green-800 font-medium">
                        {importResults.message}
                      </p>
                    </div>

                    {/* Show imported items */}
                    {importResults.imported_users?.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm text-green-700 mb-2">Imported clients:</p>
                        <div className="bg-white rounded border border-green-200 divide-y divide-green-100 max-h-40 overflow-y-auto">
                          {importResults.imported_users.map((user, idx) => (
                            <div key={idx} className="px-3 py-2 text-sm">
                              <span className="font-medium">{user.email}</span>
                              {user.name && <span className="text-gray-500"> - {user.name}</span>}
                              <span className="text-gray-400 ml-2">
                                (temp password: <code className="bg-gray-100 px-1 rounded">{user.temp_password}</code>)
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {importResults.imported_requests?.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm text-green-700 mb-2">Imported requests:</p>
                        <div className="bg-white rounded border border-green-200 divide-y divide-green-100 max-h-40 overflow-y-auto">
                          {importResults.imported_requests.map((req, idx) => (
                            <div key={idx} className="px-3 py-2 text-sm">
                              <span className="font-medium">{req.request_number}</span>
                              <span className="text-gray-500"> - {req.service}</span>
                              <span className="text-gray-400 ml-2">({req.status})</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {importResults.imported_companies?.length > 0 && (
                      <div className="mt-3">
                        <p className="text-sm text-green-700 mb-2">Imported companies:</p>
                        <div className="bg-white rounded border border-green-200 divide-y divide-green-100 max-h-40 overflow-y-auto">
                          {importResults.imported_companies.map((company, idx) => (
                            <div key={idx} className="px-3 py-2 text-sm">
                              <span className="font-medium">{company.company}</span>
                              <span className="text-gray-500"> - Admin: {company.admin_email}</span>
                              <span className="text-gray-400 ml-2">
                                (temp password: <code className="bg-gray-100 px-1 rounded">{company.temp_password}</code>)
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Errors */}
                {importResults.results.errors?.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <ExclamationCircleIcon className="h-5 w-5 text-red-600" />
                      <p className="text-red-800 font-medium">
                        {importResults.results.errors.length} errors occurred
                      </p>
                    </div>
                    <div className="bg-white rounded border border-red-200 divide-y divide-red-100 max-h-60 overflow-y-auto">
                      {importResults.results.errors.map((error, idx) => (
                        <div key={idx} className="px-3 py-2 text-sm flex items-start gap-2">
                          <XCircleIcon className="h-4 w-4 text-red-500 flex-shrink-0 mt-0.5" />
                          <div>
                            <span className="font-medium">Row {error.row}</span>
                            {error.email && (
                              <span className="text-gray-500"> ({error.email})</span>
                            )}
                            {error.service && (
                              <span className="text-gray-500"> ({error.service})</span>
                            )}
                            {error.company && (
                              <span className="text-gray-500"> ({error.company})</span>
                            )}
                            <span className="text-red-600">: {error.error}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Import More Button */}
                <div className="mt-6 flex justify-end">
                  <Button
                    variant="secondary"
                    onClick={handleClearFile}
                  >
                    Import More Data
                  </Button>
                </div>
              </Card>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
