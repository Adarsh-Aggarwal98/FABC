import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  BuildingOffice2Icon,
  MapPinIcon,
  CurrencyDollarIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { TextArea } from '../../components/common/Input';
import { Select } from '../../components/common/Input';
import { companiesAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import useCompanyStore from '../../store/companyStore';

export default function CompanySettings() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { fetchCompany: refreshCompanyStore } = useCompanyStore();
  const [company, setCompany] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [currencies, setCurrencies] = useState([]);
  const [taxTypes, setTaxTypes] = useState([]);

  const [formData, setFormData] = useState({
    name: '',
    trading_name: '',
    abn: '',
    acn: '',
    email: '',
    phone: '',
    website: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postcode: '',
    country: 'Australia',
    currency: 'AUD',
    currency_symbol: '$',
    tax_type: 'GST',
    tax_label: 'GST',
    default_tax_rate: '10',
  });

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'senior_accountant';

  useEffect(() => {
    if (!isAdmin) {
      navigate('/dashboard');
      return;
    }
    fetchCompany();
    fetchCurrenciesAndTaxTypes();
  }, [isAdmin]);

  const fetchCurrenciesAndTaxTypes = async () => {
    try {
      const [currenciesRes, taxTypesRes] = await Promise.all([
        companiesAPI.getCurrencies(),
        companiesAPI.getTaxTypes(),
      ]);
      setCurrencies(currenciesRes.data.currencies || []);
      setTaxTypes(taxTypesRes.data.tax_types || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch currencies/tax types');
    }
  };

  const fetchCompany = async () => {
    setIsLoading(true);
    try {
      const response = await companiesAPI.getMyCompany();
      const companyData = response.data.company;
      setCompany(companyData);

      setFormData({
        name: companyData.name || '',
        trading_name: companyData.trading_name || '',
        abn: companyData.abn || '',
        acn: companyData.acn || '',
        email: companyData.email || '',
        phone: companyData.phone || '',
        website: companyData.website || '',
        address_line1: companyData.address_line1 || '',
        address_line2: companyData.address_line2 || '',
        city: companyData.city || '',
        state: companyData.state || '',
        postcode: companyData.postcode || '',
        country: companyData.country || 'Australia',
        currency: companyData.currency || 'AUD',
        currency_symbol: companyData.currency_symbol || '$',
        tax_type: companyData.tax_type || 'GST',
        tax_label: companyData.tax_label || 'GST',
        default_tax_rate: companyData.default_tax_rate?.toString() || '10',
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
      await companiesAPI.update(company.id, {
        ...formData,
        default_tax_rate: parseFloat(formData.default_tax_rate) || 0,
      });
      toast.success('Company settings saved successfully');
      // Refresh the company store
      await refreshCompanyStore();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleCurrencyChange = (currency) => {
    const currencyData = currencies.find((c) => c.code === currency);
    setFormData((prev) => ({
      ...prev,
      currency,
      currency_symbol: currencyData?.symbol || '$',
    }));
  };

  const handleTaxTypeChange = (taxType) => {
    const taxData = taxTypes.find((t) => t.code === taxType);
    setFormData((prev) => ({
      ...prev,
      tax_type: taxType,
      tax_label: taxType === 'NONE' ? '' : taxType,
      default_tax_rate: taxData?.default_rate?.toString() || prev.default_tax_rate,
    }));
  };

  if (isLoading) {
    return (
      <DashboardLayout title="Company Settings">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Company Settings">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            icon={ArrowLeftIcon}
            onClick={() => navigate('/dashboard')}
          >
            Back to Dashboard
          </Button>
          <Button onClick={handleSave} loading={isSaving}>
            Save Settings
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Company Details */}
          <Card>
            <CardHeader
              title="Company Details"
              subtitle="Basic information about your company"
              icon={BuildingOffice2Icon}
            />
            <div className="space-y-4">
              <Input
                label="Company Name"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="Your Company Pty Ltd"
                required
              />
              <Input
                label="Trading Name"
                value={formData.trading_name}
                onChange={(e) => handleChange('trading_name', e.target.value)}
                placeholder="Trading As..."
                helper="Optional - shown in sidebar if set"
              />
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="ABN"
                  value={formData.abn}
                  onChange={(e) => handleChange('abn', e.target.value)}
                  placeholder="12 345 678 901"
                />
                <Input
                  label="ACN"
                  value={formData.acn}
                  onChange={(e) => handleChange('acn', e.target.value)}
                  placeholder="123 456 789"
                />
              </div>
              <Input
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                placeholder="contact@company.com"
              />
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Phone"
                  value={formData.phone}
                  onChange={(e) => handleChange('phone', e.target.value)}
                  placeholder="+61 2 1234 5678"
                />
                <Input
                  label="Website"
                  value={formData.website}
                  onChange={(e) => handleChange('website', e.target.value)}
                  placeholder="https://www.company.com"
                />
              </div>
            </div>
          </Card>

          {/* Address */}
          <Card>
            <CardHeader
              title="Business Address"
              subtitle="Your company's registered address"
              icon={MapPinIcon}
            />
            <div className="space-y-4">
              <Input
                label="Address Line 1"
                value={formData.address_line1}
                onChange={(e) => handleChange('address_line1', e.target.value)}
                placeholder="123 Business Street"
              />
              <Input
                label="Address Line 2"
                value={formData.address_line2}
                onChange={(e) => handleChange('address_line2', e.target.value)}
                placeholder="Suite 100"
              />
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="City"
                  value={formData.city}
                  onChange={(e) => handleChange('city', e.target.value)}
                  placeholder="Sydney"
                />
                <Input
                  label="State"
                  value={formData.state}
                  onChange={(e) => handleChange('state', e.target.value)}
                  placeholder="NSW"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Postcode"
                  value={formData.postcode}
                  onChange={(e) => handleChange('postcode', e.target.value)}
                  placeholder="2000"
                />
                <Input
                  label="Country"
                  value={formData.country}
                  onChange={(e) => handleChange('country', e.target.value)}
                  placeholder="Australia"
                />
              </div>
            </div>
          </Card>

          {/* Currency & Tax Settings */}
          <Card className="lg:col-span-2">
            <CardHeader
              title="Currency & Tax Settings"
              subtitle="Configure your currency and tax defaults for invoicing"
              icon={CurrencyDollarIcon}
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Currency
                </label>
                <Select
                  options={currencies.map((c) => ({ value: c.code, label: c.label }))}
                  value={formData.currency}
                  onChange={(e) => handleCurrencyChange(e.target.value)}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Symbol: {formData.currency_symbol}
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tax Type
                </label>
                <Select
                  options={taxTypes.map((t) => ({ value: t.code, label: t.label }))}
                  value={formData.tax_type}
                  onChange={(e) => handleTaxTypeChange(e.target.value)}
                />
              </div>
              <div>
                <Input
                  label="Default Tax Rate (%)"
                  type="number"
                  value={formData.default_tax_rate}
                  onChange={(e) => handleChange('default_tax_rate', e.target.value)}
                  placeholder="10"
                  min="0"
                  max="100"
                  step="0.01"
                  disabled={formData.tax_type === 'NONE'}
                />
              </div>
            </div>
            {formData.tax_type !== 'NONE' && (
              <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                <p className="text-sm text-gray-600">
                  Tax will be displayed as "{formData.tax_label}" at {formData.default_tax_rate}% on invoices.
                </p>
              </div>
            )}
          </Card>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm">
          <p className="font-medium text-blue-800 mb-2">About Company Settings</p>
          <ul className="text-blue-700 space-y-1">
            <li>Company name and address appear on invoices and documents</li>
            <li>Currency and tax settings affect how prices are displayed throughout the system</li>
            <li>For branding (logo and colors), use the Branding settings page</li>
          </ul>
        </div>
      </div>
    </DashboardLayout>
  );
}
