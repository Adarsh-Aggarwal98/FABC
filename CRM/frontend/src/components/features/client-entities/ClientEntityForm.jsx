import React, { useState, useEffect } from 'react';
import { XMarkIcon, UserIcon } from '@heroicons/react/24/outline';
import Input, { Select, TextArea } from '../../common/Input';
import Button from '../../common/Button';
import { clientEntitiesAPI, userAPI } from '../../../services/api';
import toast from 'react-hot-toast';

const ENTITY_TYPES = [
  { value: 'COMPANY', label: 'Company' },
  { value: 'TRUST', label: 'Trust' },
  { value: 'SMSF', label: 'SMSF (Self-Managed Super Fund)' },
  { value: 'PARTNERSHIP', label: 'Partnership' },
  { value: 'SOLE_TRADER', label: 'Sole Trader' },
  { value: 'INDIVIDUAL', label: 'Individual' },
];

const TRUST_TYPES = [
  { value: 'discretionary', label: 'Discretionary Trust' },
  { value: 'unit', label: 'Unit Trust' },
  { value: 'hybrid', label: 'Hybrid Trust' },
  { value: 'fixed', label: 'Fixed Trust' },
  { value: 'family', label: 'Family Trust' },
  { value: 'testamentary', label: 'Testamentary Trust' },
];

const AUSTRALIAN_STATES = [
  { value: 'NSW', label: 'New South Wales' },
  { value: 'VIC', label: 'Victoria' },
  { value: 'QLD', label: 'Queensland' },
  { value: 'SA', label: 'South Australia' },
  { value: 'WA', label: 'Western Australia' },
  { value: 'TAS', label: 'Tasmania' },
  { value: 'NT', label: 'Northern Territory' },
  { value: 'ACT', label: 'Australian Capital Territory' },
];

/**
 * ClientEntityForm - Form for creating/editing client entities
 *
 * @param {Object} props
 * @param {Object} props.entity - Entity to edit (null for create mode)
 * @param {Function} props.onSave - Callback after successful save
 * @param {Function} props.onCancel - Callback to cancel/close form
 * @param {boolean} props.isModal - Whether form is displayed in a modal
 */
export default function ClientEntityForm({
  entity = null,
  onSave,
  onCancel,
  isModal = false,
  preselectedUser = null, // Optional: pre-select a user when opening from request creation
}) {
  const [formData, setFormData] = useState({
    name: '',
    trading_name: '',
    entity_type: 'COMPANY',
    abn: '',
    acn: '',
    tfn: '',
    trust_type: '',
    trustee_name: '',
    trust_deed_date: '',
    email: '',
    phone: '',
    address_line1: '',
    address_line2: '',
    city: '',
    state: '',
    postcode: '',
    country: 'Australia',
    financial_year_end_month: 6,
    financial_year_end_day: 30,
    notes: '',
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // User selection state
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(preselectedUser);
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);
  const [userSearchQuery, setUserSearchQuery] = useState('');

  const isEditMode = !!entity;

  // Fetch users on mount
  useEffect(() => {
    fetchUsers();
  }, []);

  // Set preselected user
  useEffect(() => {
    if (preselectedUser) {
      setSelectedUser(preselectedUser);
      setFormData(prev => ({
        ...prev,
        email: preselectedUser.email || prev.email,
        phone: preselectedUser.phone || prev.phone,
      }));
    }
  }, [preselectedUser]);

  const fetchUsers = async () => {
    setIsLoadingUsers(true);
    try {
      const response = await userAPI.list({ role: 'user', per_page: 500 });
      setUsers(response.data.data?.users || response.data.users || response.data.data || []);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setIsLoadingUsers(false);
    }
  };

  const handleUserSelect = (e) => {
    const userId = e.target.value;
    if (!userId) {
      setSelectedUser(null);
      return;
    }
    const user = users.find(u => u.id === userId);
    if (user) {
      setSelectedUser(user);
      // Auto-fill email and phone from user
      setFormData(prev => ({
        ...prev,
        email: user.email || prev.email,
        phone: user.phone || prev.phone,
      }));
    }
  };

  // Filter users based on search
  const filteredUsers = users.filter(user => {
    if (!userSearchQuery) return true;
    const query = userSearchQuery.toLowerCase();
    return (
      user.full_name?.toLowerCase().includes(query) ||
      user.email?.toLowerCase().includes(query) ||
      user.first_name?.toLowerCase().includes(query) ||
      user.last_name?.toLowerCase().includes(query)
    );
  });

  useEffect(() => {
    if (entity) {
      setFormData({
        name: entity.name || '',
        trading_name: entity.trading_name || '',
        entity_type: entity.entity_type || 'COMPANY',
        abn: entity.abn || '',
        acn: entity.acn || '',
        tfn: entity.tfn || '',
        trust_type: entity.trust_type || '',
        trustee_name: entity.trustee_name || '',
        trust_deed_date: entity.trust_deed_date || '',
        email: entity.email || '',
        phone: entity.phone || '',
        address_line1: entity.address_line1 || '',
        address_line2: entity.address_line2 || '',
        city: entity.city || '',
        state: entity.state || '',
        postcode: entity.postcode || '',
        country: entity.country || 'Australia',
        financial_year_end_month: entity.financial_year_end_month || 6,
        financial_year_end_day: entity.financial_year_end_day || 30,
        notes: entity.notes || '',
      });
    }
  }, [entity]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear error when field is modified
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Entity name is required';
    }

    if (formData.abn && !/^\d{11}$/.test(formData.abn.replace(/\s/g, ''))) {
      newErrors.abn = 'ABN must be 11 digits';
    }

    if (formData.acn && !/^\d{9}$/.test(formData.acn.replace(/\s/g, ''))) {
      newErrors.acn = 'ACN must be 9 digits';
    }

    if (formData.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email address';
    }

    if (formData.entity_type === 'TRUST' && !formData.trust_type) {
      newErrors.trust_type = 'Trust type is required for trusts';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      toast.error('Please fix the errors before submitting');
      return;
    }

    setIsSubmitting(true);

    try {
      // Clean up data - remove empty strings and format ABN/ACN
      const cleanData = { ...formData };
      cleanData.abn = cleanData.abn.replace(/\s/g, '') || null;
      cleanData.acn = cleanData.acn.replace(/\s/g, '') || null;

      // Remove trust-specific fields if not a trust
      if (cleanData.entity_type !== 'TRUST') {
        cleanData.trust_type = null;
        cleanData.trustee_name = null;
        cleanData.trust_deed_date = null;
      }

      // Remove empty optional fields
      Object.keys(cleanData).forEach((key) => {
        if (cleanData[key] === '') {
          cleanData[key] = null;
        }
      });

      // Add primary contact if user is selected (only for new entities)
      if (!isEditMode && selectedUser) {
        cleanData.primary_contact = {
          user_id: selectedUser.id,
          first_name: selectedUser.first_name || selectedUser.full_name?.split(' ')[0] || 'Primary',
          last_name: selectedUser.last_name || selectedUser.full_name?.split(' ').slice(1).join(' ') || 'Contact',
          email: selectedUser.email,
          phone: selectedUser.phone || null,
          is_primary: true,
          contact_type: 'PRIMARY',
        };
      }

      let response;
      if (isEditMode) {
        response = await clientEntitiesAPI.update(entity.id, cleanData);
        toast.success('Client entity updated successfully');
      } else {
        response = await clientEntitiesAPI.create(cleanData);
        toast.success('Client entity created successfully');
      }

      if (onSave) {
        onSave(response.data.data?.entity || response.data.data);
      }
    } catch (error) {
      const errorMessage =
        error.response?.data?.error || 'Failed to save client entity';
      toast.error(errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  const showTrustFields = formData.entity_type === 'TRUST';

  const formContent = (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Link to User (for new entities only) */}
      {!isEditMode && (
        <div className="space-y-4 bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2">
            <UserIcon className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-medium text-blue-900">Link to Client User</h3>
          </div>
          <p className="text-sm text-blue-700">
            Select a client user to link this entity to. Their email will be auto-filled.
          </p>

          <Select
            label="Select Client User"
            value={selectedUser?.id || ''}
            onChange={handleUserSelect}
            options={[
              { value: '', label: isLoadingUsers ? 'Loading users...' : 'Select a user (optional)...' },
              ...filteredUsers.map(u => ({
                value: u.id,
                label: `${u.full_name || `${u.first_name || ''} ${u.last_name || ''}`.trim() || 'No Name'} (${u.email})`
              }))
            ]}
          />

          {selectedUser && (
            <div className="p-3 bg-white rounded border border-blue-200">
              <p className="text-sm text-gray-700">
                <span className="font-medium">Selected:</span> {selectedUser.full_name || selectedUser.email}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                This user will be set as the primary contact for the entity.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Basic Information */}
      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900">Basic Information</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Entity Name *"
            name="name"
            value={formData.name}
            onChange={handleChange}
            error={errors.name}
            placeholder="e.g., ABC Holdings Pty Ltd"
          />

          <Input
            label="Trading Name"
            name="trading_name"
            value={formData.trading_name}
            onChange={handleChange}
            placeholder="e.g., ABC Services"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Select
            label="Entity Type *"
            name="entity_type"
            value={formData.entity_type}
            onChange={handleChange}
            options={ENTITY_TYPES}
          />

          <Input
            label="ABN"
            name="abn"
            value={formData.abn}
            onChange={handleChange}
            error={errors.abn}
            placeholder="12 345 678 901"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="ACN"
            name="acn"
            value={formData.acn}
            onChange={handleChange}
            error={errors.acn}
            placeholder="123 456 789"
          />

          <Input
            label="TFN"
            name="tfn"
            value={formData.tfn}
            onChange={handleChange}
            placeholder="Tax File Number"
          />
        </div>
      </div>

      {/* Trust-Specific Fields */}
      {showTrustFields && (
        <div className="space-y-4 border-t pt-4">
          <h3 className="text-lg font-medium text-gray-900">Trust Details</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Trust Type *"
              name="trust_type"
              value={formData.trust_type}
              onChange={handleChange}
              options={[{ value: '', label: 'Select trust type...' }, ...TRUST_TYPES]}
              error={errors.trust_type}
            />

            <Input
              label="Trustee Name"
              name="trustee_name"
              value={formData.trustee_name}
              onChange={handleChange}
              placeholder="e.g., John Smith as Trustee"
            />
          </div>

          <Input
            label="Trust Deed Date"
            name="trust_deed_date"
            type="date"
            value={formData.trust_deed_date}
            onChange={handleChange}
          />
        </div>
      )}

      {/* Contact Information */}
      <div className="space-y-4 border-t pt-4">
        <h3 className="text-lg font-medium text-gray-900">Contact Information</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            error={errors.email}
            placeholder="contact@example.com"
          />

          <Input
            label="Phone"
            name="phone"
            value={formData.phone}
            onChange={handleChange}
            placeholder="+61 4XX XXX XXX"
          />
        </div>
      </div>

      {/* Address */}
      <div className="space-y-4 border-t pt-4">
        <h3 className="text-lg font-medium text-gray-900">Address</h3>

        <Input
          label="Address Line 1"
          name="address_line1"
          value={formData.address_line1}
          onChange={handleChange}
          placeholder="Street address"
        />

        <Input
          label="Address Line 2"
          name="address_line2"
          value={formData.address_line2}
          onChange={handleChange}
          placeholder="Suite, unit, building (optional)"
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            label="City/Suburb"
            name="city"
            value={formData.city}
            onChange={handleChange}
          />

          <Select
            label="State"
            name="state"
            value={formData.state}
            onChange={handleChange}
            options={[{ value: '', label: 'Select state...' }, ...AUSTRALIAN_STATES]}
          />

          <Input
            label="Postcode"
            name="postcode"
            value={formData.postcode}
            onChange={handleChange}
            placeholder="2000"
          />
        </div>
      </div>

      {/* Financial Year */}
      <div className="space-y-4 border-t pt-4">
        <h3 className="text-lg font-medium text-gray-900">Financial Year</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Select
            label="FY End Month"
            name="financial_year_end_month"
            value={formData.financial_year_end_month}
            onChange={handleChange}
            options={[
              { value: 1, label: 'January' },
              { value: 2, label: 'February' },
              { value: 3, label: 'March' },
              { value: 4, label: 'April' },
              { value: 5, label: 'May' },
              { value: 6, label: 'June' },
              { value: 7, label: 'July' },
              { value: 8, label: 'August' },
              { value: 9, label: 'September' },
              { value: 10, label: 'October' },
              { value: 11, label: 'November' },
              { value: 12, label: 'December' },
            ]}
          />

          <Input
            label="FY End Day"
            name="financial_year_end_day"
            type="number"
            min="1"
            max="31"
            value={formData.financial_year_end_day}
            onChange={handleChange}
          />
        </div>
      </div>

      {/* Notes */}
      <div className="space-y-4 border-t pt-4">
        <TextArea
          label="Notes"
          name="notes"
          value={formData.notes}
          onChange={handleChange}
          rows={3}
          placeholder="Any additional notes about this entity..."
        />
      </div>

      {/* Form Actions */}
      <div className="flex justify-end gap-3 pt-4 border-t">
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" loading={isSubmitting}>
          {isEditMode ? 'Save Changes' : 'Create Entity'}
        </Button>
      </div>
    </form>
  );

  if (isModal) {
    return (
      <div className="fixed inset-0 z-50 overflow-y-auto">
        <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <div
            className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"
            onClick={onCancel}
          />
          <div className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl">
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <h2 className="text-xl font-semibold text-gray-900">
                {isEditMode ? 'Edit Client Entity' : 'Create Client Entity'}
              </h2>
              {onCancel && (
                <button
                  type="button"
                  onClick={onCancel}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              )}
            </div>
            <div className="px-6 py-4 max-h-[70vh] overflow-y-auto">
              {formContent}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return formContent;
}
