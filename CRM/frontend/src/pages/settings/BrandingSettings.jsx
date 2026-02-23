import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  PhotoIcon,
  TrashIcon,
  ArrowUpTrayIcon,
  SwatchIcon,
  EyeIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';
import { companiesAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import useThemeStore from '../../store/themeStore';

export default function BrandingSettings() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { fetchTheme, applyTheme } = useThemeStore();
  const [company, setCompany] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingLogo, setIsUploadingLogo] = useState(false);
  const fileInputRef = useRef(null);

  const [formData, setFormData] = useState({
    primary_color: '#4F46E5',
    secondary_color: '#10B981',
    tertiary_color: '#6366F1',
    sidebar_bg_color: '#0f172a',
    sidebar_text_color: '#ffffff',
    sidebar_hover_bg_color: '#334155',
  });

  const [previewColors, setPreviewColors] = useState({
    primary_color: '#4F46E5',
    secondary_color: '#10B981',
    tertiary_color: '#6366F1',
    sidebar_bg_color: '#0f172a',
    sidebar_text_color: '#ffffff',
    sidebar_hover_bg_color: '#334155',
  });

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'senior_accountant';

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

      const colors = {
        primary_color: companyData.primary_color || '#4F46E5',
        secondary_color: companyData.secondary_color || '#10B981',
        tertiary_color: companyData.tertiary_color || '#6366F1',
        sidebar_bg_color: companyData.sidebar_bg_color || '#0f172a',
        sidebar_text_color: companyData.sidebar_text_color || '#ffffff',
        sidebar_hover_bg_color: companyData.sidebar_hover_bg_color || '#334155',
      };
      setFormData(colors);
      setPreviewColors(colors);
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
      toast.success('Branding settings saved successfully');
      // Refresh the theme
      await fetchTheme();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleColorChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setPreviewColors((prev) => ({ ...prev, [field]: value }));
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
      const response = await companiesAPI.uploadLogo(file);
      toast.success('Logo uploaded successfully');
      setCompany((prev) => ({ ...prev, logo_url: response.data.logo_url }));
      // Refresh the theme
      await fetchTheme();
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
      // Refresh the theme
      await fetchTheme();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete logo');
    }
  };

  const handlePreview = () => {
    try {
      // Helper to convert hex to HSL
      const hexToHSL = (hex) => {
        hex = hex.replace('#', '');
        const r = parseInt(hex.substring(0, 2), 16) / 255;
        const g = parseInt(hex.substring(2, 4), 16) / 255;
        const b = parseInt(hex.substring(4, 6), 16) / 255;
        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
          h = s = 0;
        } else {
          const d = max - min;
          s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
          switch (max) {
            case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
            case g: h = ((b - r) / d + 2) / 6; break;
            case b: h = ((r - g) / d + 4) / 6; break;
            default: h = 0;
          }
        }
        return { h: Math.round(h * 360), s: Math.round(s * 100), l: Math.round(l * 100) };
      };

      // Generate shades from hex color
      const generateShades = (hex) => {
        const hsl = hexToHSL(hex);
        return {
          50: `${hsl.h} ${hsl.s}% 97%`,
          100: `${hsl.h} ${hsl.s}% 94%`,
          200: `${hsl.h} ${hsl.s}% 86%`,
          300: `${hsl.h} ${hsl.s}% 74%`,
          400: `${hsl.h} ${hsl.s}% 62%`,
          500: `${hsl.h} ${hsl.s}% 50%`,
          600: `${hsl.h} ${hsl.s}% 42%`,
          700: `${hsl.h} ${hsl.s}% 34%`,
          800: `${hsl.h} ${hsl.s}% 26%`,
          900: `${hsl.h} ${hsl.s}% 18%`,
          950: `${hsl.h} ${hsl.s}% 10%`,
        };
      };

      const root = document.documentElement;

      // Apply primary color shades
      const primaryShades = generateShades(previewColors.primary_color);
      Object.entries(primaryShades).forEach(([shade, value]) => {
        root.style.setProperty(`--color-primary-${shade}`, value);
      });

      // Apply secondary color shades
      const secondaryShades = generateShades(previewColors.secondary_color);
      Object.entries(secondaryShades).forEach(([shade, value]) => {
        root.style.setProperty(`--color-secondary-${shade}`, value);
      });

      // Apply tertiary color shades
      const tertiaryShades = generateShades(previewColors.tertiary_color);
      Object.entries(tertiaryShades).forEach(([shade, value]) => {
        root.style.setProperty(`--color-tertiary-${shade}`, value);
      });

      // Also set raw hex values
      root.style.setProperty('--primary-color', previewColors.primary_color);
      root.style.setProperty('--secondary-color', previewColors.secondary_color);
      root.style.setProperty('--tertiary-color', previewColors.tertiary_color);

      // Apply sidebar colors
      root.style.setProperty('--sidebar-bg-color', previewColors.sidebar_bg_color);
      root.style.setProperty('--sidebar-text-color', previewColors.sidebar_text_color);
      root.style.setProperty('--sidebar-hover-bg-color', previewColors.sidebar_hover_bg_color);

      toast.success('Preview applied! Save to keep changes.');
    } catch (error) {
      console.error('Preview error:', error);
      toast.error('Failed to apply preview');
    }
  };

  const handleReset = () => {
    const defaultColors = {
      primary_color: '#4F46E5',
      secondary_color: '#10B981',
      tertiary_color: '#6366F1',
      sidebar_bg_color: '#0f172a',
      sidebar_text_color: '#ffffff',
      sidebar_hover_bg_color: '#334155',
    };
    setFormData(defaultColors);
    setPreviewColors(defaultColors);
  };

  if (isLoading) {
    return (
      <DashboardLayout title="Branding Settings">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Branding Settings">
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
          <div className="flex gap-2">
            <Button variant="secondary" icon={EyeIcon} onClick={handlePreview}>
              Preview
            </Button>
            <Button onClick={handleSave} loading={isSaving}>
              Save Settings
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Company Logo */}
          <Card>
            <CardHeader
              title="Company Logo"
              subtitle="Upload your company logo to appear in the sidebar and on invoices"
            />
            <div className="flex items-center gap-6">
              <div className="w-24 h-24 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50">
                {company?.logo_url ? (
                  <img
                    src={company.logo_url}
                    alt="Company Logo"
                    className="max-w-full max-h-full object-contain rounded-lg"
                  />
                ) : (
                  <div className="text-center text-gray-400">
                    <PhotoIcon className="h-8 w-8 mx-auto mb-1" />
                    <p className="text-xs">No logo</p>
                  </div>
                )}
              </div>

              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-3">
                  Recommended size: 200x200 pixels. Supported formats: PNG, JPG, SVG (max 5MB).
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
          </Card>

          {/* Color Preview */}
          <Card>
            <CardHeader
              title="Color Preview"
              subtitle="Preview how your colors will look"
            />
            <div className="space-y-4">
              {/* Color Swatches */}
              <div className="flex gap-4">
                <div className="flex-1">
                  <p className="text-xs text-gray-500 mb-2">Primary</p>
                  <div
                    className="h-16 rounded-lg shadow-inner"
                    style={{ backgroundColor: previewColors.primary_color }}
                  />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-500 mb-2">Secondary</p>
                  <div
                    className="h-16 rounded-lg shadow-inner"
                    style={{ backgroundColor: previewColors.secondary_color }}
                  />
                </div>
                <div className="flex-1">
                  <p className="text-xs text-gray-500 mb-2">Tertiary</p>
                  <div
                    className="h-16 rounded-lg shadow-inner"
                    style={{ backgroundColor: previewColors.tertiary_color }}
                  />
                </div>
              </div>

              {/* Sample UI Elements */}
              <div className="pt-4 border-t">
                <p className="text-xs text-gray-500 mb-3">Sample Elements</p>
                <div className="flex flex-wrap gap-2">
                  <button
                    className="px-4 py-2 rounded-lg text-white text-sm font-medium"
                    style={{ backgroundColor: previewColors.primary_color }}
                  >
                    Primary Button
                  </button>
                  <button
                    className="px-4 py-2 rounded-lg text-white text-sm font-medium"
                    style={{ backgroundColor: previewColors.secondary_color }}
                  >
                    Secondary Button
                  </button>
                  <span
                    className="px-3 py-1 rounded-full text-white text-xs font-medium"
                    style={{ backgroundColor: previewColors.tertiary_color }}
                  >
                    Badge
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Theme Colors */}
          <Card className="lg:col-span-2">
            <CardHeader
              title="Theme Colors"
              subtitle="Customize your practice's color scheme"
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Primary Color */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Primary Color
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Used for main buttons, links, and key UI elements.
                </p>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={formData.primary_color}
                    onChange={(e) => handleColorChange('primary_color', e.target.value)}
                    className="w-12 h-12 rounded-lg cursor-pointer border border-gray-300"
                  />
                  <Input
                    value={formData.primary_color}
                    onChange={(e) => handleColorChange('primary_color', e.target.value)}
                    placeholder="#4F46E5"
                    className="flex-1"
                  />
                </div>
              </div>

              {/* Secondary Color */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Secondary Color
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Used for success states, secondary buttons, and accents.
                </p>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={formData.secondary_color}
                    onChange={(e) => handleColorChange('secondary_color', e.target.value)}
                    className="w-12 h-12 rounded-lg cursor-pointer border border-gray-300"
                  />
                  <Input
                    value={formData.secondary_color}
                    onChange={(e) => handleColorChange('secondary_color', e.target.value)}
                    placeholder="#10B981"
                    className="flex-1"
                  />
                </div>
              </div>

              {/* Tertiary Color */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tertiary Color
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Used for badges, highlights, and decorative elements.
                </p>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={formData.tertiary_color}
                    onChange={(e) => handleColorChange('tertiary_color', e.target.value)}
                    className="w-12 h-12 rounded-lg cursor-pointer border border-gray-300"
                  />
                  <Input
                    value={formData.tertiary_color}
                    onChange={(e) => handleColorChange('tertiary_color', e.target.value)}
                    placeholder="#6366F1"
                    className="flex-1"
                  />
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t flex justify-between items-center">
              <Button variant="ghost" onClick={handleReset}>
                Reset to Defaults
              </Button>
              <p className="text-xs text-gray-500">
                Changes will apply to all users in your practice after saving.
              </p>
            </div>
          </Card>

          {/* Sidebar Colors */}
          <Card className="lg:col-span-2">
            <CardHeader
              title="Sidebar Colors"
              subtitle="Customize your sidebar appearance"
            />
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Sidebar Background Color */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Background Color
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Main background color of the sidebar.
                </p>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={formData.sidebar_bg_color}
                    onChange={(e) => handleColorChange('sidebar_bg_color', e.target.value)}
                    className="w-12 h-12 rounded-lg cursor-pointer border border-gray-300"
                  />
                  <Input
                    value={formData.sidebar_bg_color}
                    onChange={(e) => handleColorChange('sidebar_bg_color', e.target.value)}
                    placeholder="#0f172a"
                    className="flex-1"
                  />
                </div>
              </div>

              {/* Sidebar Text Color */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Text Color
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Color of text and icons in the sidebar.
                </p>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={formData.sidebar_text_color}
                    onChange={(e) => handleColorChange('sidebar_text_color', e.target.value)}
                    className="w-12 h-12 rounded-lg cursor-pointer border border-gray-300"
                  />
                  <Input
                    value={formData.sidebar_text_color}
                    onChange={(e) => handleColorChange('sidebar_text_color', e.target.value)}
                    placeholder="#ffffff"
                    className="flex-1"
                  />
                </div>
              </div>

              {/* Sidebar Hover Color */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Hover Color
                </label>
                <p className="text-xs text-gray-500 mb-3">
                  Background color when hovering over menu items.
                </p>
                <div className="flex items-center gap-3">
                  <input
                    type="color"
                    value={formData.sidebar_hover_bg_color}
                    onChange={(e) => handleColorChange('sidebar_hover_bg_color', e.target.value)}
                    className="w-12 h-12 rounded-lg cursor-pointer border border-gray-300"
                  />
                  <Input
                    value={formData.sidebar_hover_bg_color}
                    onChange={(e) => handleColorChange('sidebar_hover_bg_color', e.target.value)}
                    placeholder="#334155"
                    className="flex-1"
                  />
                </div>
              </div>
            </div>

            {/* Sidebar Preview */}
            <div className="mt-6 pt-4 border-t">
              <p className="text-xs text-gray-500 mb-3">Sidebar Preview</p>
              <div
                className="w-full max-w-xs h-40 rounded-lg p-4"
                style={{ backgroundColor: previewColors.sidebar_bg_color }}
              >
                <div className="space-y-2">
                  <div
                    className="h-8 rounded flex items-center px-3 text-sm"
                    style={{
                      backgroundColor: previewColors.sidebar_hover_bg_color,
                      color: previewColors.sidebar_text_color
                    }}
                  >
                    Active Item
                  </div>
                  <div
                    className="h-8 rounded flex items-center px-3 text-sm"
                    style={{ color: `${previewColors.sidebar_text_color}cc` }}
                  >
                    Menu Item
                  </div>
                  <div
                    className="h-8 rounded flex items-center px-3 text-sm"
                    style={{ color: `${previewColors.sidebar_text_color}cc` }}
                  >
                    Menu Item
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
