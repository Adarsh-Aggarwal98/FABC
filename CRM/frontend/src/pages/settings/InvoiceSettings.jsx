import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  DocumentTextIcon,
  EyeIcon,
  EyeSlashIcon,
  PhotoIcon,
  TrashIcon,
  ArrowUpTrayIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { TextArea } from '../../components/common/Input';
import { companiesAPI, requestsAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

export default function InvoiceSettings() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [company, setCompany] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingLogo, setIsUploadingLogo] = useState(false);
  const fileInputRef = useRef(null);

  const [formData, setFormData] = useState({
    invoice_prefix: 'INV',
    invoice_payment_terms: 'Due within 14 days',
    invoice_bank_details: '',
    invoice_notes: '',
    invoice_footer: '',
    // Section visibility toggles
    invoice_show_logo: true,
    invoice_show_company_details: true,
    invoice_show_client_details: true,
    invoice_show_bank_details: true,
    invoice_show_payment_terms: true,
    invoice_show_notes: true,
    invoice_show_footer: true,
    invoice_show_tax: true,
  });

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin';

  useEffect(() => {
    if (!isAdmin) {
      navigate('/dashboard');
      return;
    }
    fetchCompany();
  }, [isAdmin]);

  const fetchCompany = async () => {
    setIsLoading(true);
    try {
      const response = await companiesAPI.getMyCompany();
      const companyData = response.data.company;
      setCompany(companyData);

      // Set form data from company invoice settings
      const settings = companyData.invoice_settings || {};
      setFormData({
        invoice_prefix: settings.prefix || 'INV',
        invoice_payment_terms: settings.payment_terms || 'Due within 14 days',
        invoice_bank_details: settings.bank_details || '',
        invoice_notes: settings.notes || '',
        invoice_footer: settings.footer || '',
        // Section visibility (default to true if not set)
        invoice_show_logo: settings.show_logo !== false,
        invoice_show_company_details: settings.show_company_details !== false,
        invoice_show_client_details: settings.show_client_details !== false,
        invoice_show_bank_details: settings.show_bank_details !== false,
        invoice_show_payment_terms: settings.show_payment_terms !== false,
        invoice_show_notes: settings.show_notes !== false,
        invoice_show_footer: settings.show_footer !== false,
        invoice_show_tax: settings.show_tax !== false,
      });
    } catch (error) {
      toast.error('Failed to fetch company settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!company) return;

    setIsSaving(true);
    try {
      await companiesAPI.update(company.id, formData);
      toast.success('Invoice settings saved successfully');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleToggle = (field) => {
    setFormData((prev) => ({ ...prev, [field]: !prev[field] }));
  };

  const handleLogoUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/svg+xml'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Please upload a valid image file (PNG, JPG, GIF, WebP, or SVG)');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB');
      return;
    }

    setIsUploadingLogo(true);
    try {
      const response = await companiesAPI.uploadLogo(file);
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
      await companiesAPI.deleteLogo();
      toast.success('Logo deleted successfully');
      setCompany((prev) => ({ ...prev, logo_url: null }));
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete logo');
    }
  };

  const handlePreviewPdf = async () => {
    try {
      // First save the settings to ensure preview uses latest values
      await handleSave();
      const response = await requestsAPI.previewSampleInvoice();
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to preview invoice PDF');
    }
  };

  // Toggle component for section visibility
  const SectionToggle = ({ label, description, field, icon: Icon }) => (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
      <div className="flex items-center gap-3">
        {Icon && <Icon className="h-5 w-5 text-gray-400" />}
        <div>
          <p className="text-sm font-medium text-gray-900">{label}</p>
          {description && <p className="text-xs text-gray-500">{description}</p>}
        </div>
      </div>
      <button
        type="button"
        onClick={() => handleToggle(field)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
          formData[field] ? 'bg-primary-600' : 'bg-gray-200'
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            formData[field] ? 'translate-x-6' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  );

  if (isLoading) {
    return (
      <DashboardLayout title="Invoice Settings">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Invoice Settings">
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            icon={ArrowLeftIcon}
            onClick={() => navigate('/dashboard')}
          >
            Back to Dashboard
          </Button>
          <div className="flex gap-2">
            <Button variant="secondary" icon={EyeIcon} onClick={handlePreviewPdf}>
              Preview PDF
            </Button>
            <Button onClick={handleSave} loading={isSaving}>
              Save Settings
            </Button>
          </div>
        </div>

        {/* Company Logo */}
        <Card>
          <CardHeader
            title="Company Logo"
            subtitle="Upload your company logo to appear on invoices"
          />
          <div className="flex items-center gap-6">
            {/* Logo Preview */}
            <div className="w-32 h-32 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50">
              {company?.logo_url ? (
                <img
                  src={company.logo_url}
                  alt="Company Logo"
                  className="max-w-full max-h-full object-contain rounded-lg"
                />
              ) : (
                <div className="text-center text-gray-400">
                  <PhotoIcon className="h-10 w-10 mx-auto mb-1" />
                  <p className="text-xs">No logo</p>
                </div>
              )}
            </div>

            {/* Upload Controls */}
            <div className="flex-1">
              <p className="text-sm text-gray-600 mb-3">
                Upload a logo to display on your invoices. Recommended size: 300x100 pixels.
                Supported formats: PNG, JPG, GIF, WebP, SVG (max 5MB).
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
                  icon={ArrowUpTrayIcon}
                  onClick={() => fileInputRef.current?.click()}
                  loading={isUploadingLogo}
                >
                  {company?.logo_url ? 'Change Logo' : 'Upload Logo'}
                </Button>
                {company?.logo_url && (
                  <Button
                    variant="ghost"
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
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Invoice Details */}
          <Card>
            <CardHeader
              title="Invoice Details"
              subtitle="Customize how your invoices appear"
            />
            <div className="space-y-4">
              <Input
                label="Invoice Prefix"
                value={formData.invoice_prefix}
                onChange={(e) => handleChange('invoice_prefix', e.target.value)}
                placeholder="INV"
                helper="Prefix for invoice numbers (e.g., INV-001)"
              />

              <Input
                label="Payment Terms"
                value={formData.invoice_payment_terms}
                onChange={(e) => handleChange('invoice_payment_terms', e.target.value)}
                placeholder="Due within 14 days"
              />

              <TextArea
                label="Bank Details"
                value={formData.invoice_bank_details}
                onChange={(e) => handleChange('invoice_bank_details', e.target.value)}
                placeholder="Bank: ANZ&#10;BSB: 012-345&#10;Account: 1234567890&#10;Account Name: Your Business Pty Ltd"
                rows={4}
                helper="Bank account details for payment"
              />

              <TextArea
                label="Invoice Notes / Terms"
                value={formData.invoice_notes}
                onChange={(e) => handleChange('invoice_notes', e.target.value)}
                placeholder="Payment is due within 14 days. Late payments may incur additional fees."
                rows={3}
                helper="Default terms and conditions"
              />

              <TextArea
                label="Invoice Footer"
                value={formData.invoice_footer}
                onChange={(e) => handleChange('invoice_footer', e.target.value)}
                placeholder="Thank you for your business!"
                rows={2}
              />
            </div>
          </Card>

          {/* Invoice Section Visibility */}
          <Card>
            <CardHeader
              title="Invoice Sections"
              subtitle="Choose which sections to display on your invoices"
            />
            <div className="space-y-1">
              <SectionToggle
                label="Company Logo"
                description="Display your company logo at the top"
                field="invoice_show_logo"
              />
              <SectionToggle
                label="Company Details"
                description="Show company name, ABN, address, and contact info"
                field="invoice_show_company_details"
              />
              <SectionToggle
                label="Client Details"
                description="Show client name, email, and address"
                field="invoice_show_client_details"
              />
              <SectionToggle
                label="Tax Calculation"
                description="Show tax breakdown (GST/VAT) in totals"
                field="invoice_show_tax"
              />
              <SectionToggle
                label="Payment Terms"
                description="Show payment terms (e.g., Due within 14 days)"
                field="invoice_show_payment_terms"
              />
              <SectionToggle
                label="Bank Details"
                description="Show bank account details for payment"
                field="invoice_show_bank_details"
              />
              <SectionToggle
                label="Notes & Terms"
                description="Show terms and conditions section"
                field="invoice_show_notes"
              />
              <SectionToggle
                label="Footer"
                description="Show footer message at the bottom"
                field="invoice_show_footer"
              />
            </div>

            <div className="mt-4 pt-4 border-t">
              <p className="text-xs text-gray-500">
                Toggle sections on or off to customize your invoice layout.
                Use the "Preview PDF" button to see your changes.
              </p>
            </div>
          </Card>
        </div>

        {/* Currency & Tax Info */}
        <Card>
          <CardHeader
            title="Currency & Tax Settings"
            subtitle="Configure currency and tax settings for your invoices"
          />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">
                Your current settings: <strong>{company?.currency || 'AUD'}</strong> with{' '}
                <strong>{company?.tax_label || 'GST'}</strong> at{' '}
                <strong>{company?.default_tax_rate || 10}%</strong>
              </p>
              <p className="text-xs text-gray-500 mt-1">
                To change currency or tax settings, go to Company Settings.
              </p>
            </div>
            <Button
              variant="secondary"
              onClick={() => navigate('/settings/company')}
            >
              Company Settings
            </Button>
          </div>
        </Card>
      </div>
    </DashboardLayout>
  );
}
