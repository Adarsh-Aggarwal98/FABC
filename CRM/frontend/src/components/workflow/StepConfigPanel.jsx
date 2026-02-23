import { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

const stepTypes = [
  { value: 'START', label: 'Start', description: 'Initial step for new requests' },
  { value: 'NORMAL', label: 'Normal', description: 'Regular workflow step' },
  { value: 'QUERY', label: 'Query', description: 'Waiting for client input' },
  { value: 'END', label: 'End', description: 'Terminal step (completed, cancelled)' },
];

const stepColors = [
  { value: 'gray', label: 'Gray', className: 'bg-gray-400' },
  { value: 'blue', label: 'Blue', className: 'bg-blue-400' },
  { value: 'green', label: 'Green', className: 'bg-green-400' },
  { value: 'yellow', label: 'Yellow', className: 'bg-yellow-400' },
  { value: 'orange', label: 'Orange', className: 'bg-orange-400' },
  { value: 'red', label: 'Red', className: 'bg-red-400' },
  { value: 'purple', label: 'Purple', className: 'bg-purple-400' },
  { value: 'indigo', label: 'Indigo', className: 'bg-indigo-400' },
  { value: 'pink', label: 'Pink', className: 'bg-pink-400' },
];

const roleOptions = [
  { value: 'super_admin', label: 'Super Admin' },
  { value: 'admin', label: 'Admin' },
  { value: 'accountant', label: 'Accountant' },
  { value: 'user', label: 'Client' },
];

export default function StepConfigPanel({ step, onSave, onClose, onDelete }) {
  const [formData, setFormData] = useState({
    name: '',
    display_name: '',
    description: '',
    step_type: 'NORMAL',
    color: 'blue',
    allowed_roles: [],
    required_fields: [],
    auto_assign: false,
    notify_roles: [],
    notify_client: false,
  });

  useEffect(() => {
    if (step) {
      setFormData({
        name: step.name || '',
        display_name: step.display_name || '',
        description: step.description || '',
        step_type: step.step_type || 'NORMAL',
        color: step.color || 'blue',
        allowed_roles: step.allowed_roles || [],
        required_fields: step.required_fields || [],
        auto_assign: step.auto_assign || false,
        notify_roles: step.notify_roles || [],
        notify_client: step.notify_client || false,
      });
    }
  }, [step]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleRoleToggle = (field, role) => {
    setFormData(prev => {
      const current = prev[field] || [];
      if (current.includes(role)) {
        return { ...prev, [field]: current.filter(r => r !== role) };
      }
      return { ...prev, [field]: [...current, role] };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  if (!step) return null;

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl border-l border-gray-200 z-50 overflow-y-auto">
      <div className="sticky top-0 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Configure Step</h3>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-100 rounded"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="p-4 space-y-4">
        {/* Name (internal) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Internal Name
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value.toLowerCase().replace(/\s+/g, '_'))}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., pending, processing"
            required
          />
          <p className="mt-1 text-xs text-gray-500">
            Used internally for status tracking
          </p>
        </div>

        {/* Display Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Display Name
          </label>
          <input
            type="text"
            value={formData.display_name}
            onChange={(e) => handleChange('display_name', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., Pending Review"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
            rows={2}
            placeholder="Brief description of this step"
          />
        </div>

        {/* Step Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Step Type
          </label>
          <div className="grid grid-cols-2 gap-2">
            {stepTypes.map((type) => (
              <button
                key={type.value}
                type="button"
                onClick={() => handleChange('step_type', type.value)}
                className={`
                  p-2 text-left rounded-lg border-2 transition-colors
                  ${formData.step_type === type.value
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                  }
                `}
              >
                <div className="text-sm font-medium">{type.label}</div>
                <div className="text-xs text-gray-500">{type.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Color */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Color
          </label>
          <div className="flex flex-wrap gap-2">
            {stepColors.map((color) => (
              <button
                key={color.value}
                type="button"
                onClick={() => handleChange('color', color.value)}
                className={`
                  w-8 h-8 rounded-full ${color.className}
                  ${formData.color === color.value
                    ? 'ring-2 ring-offset-2 ring-gray-600'
                    : ''
                  }
                `}
                title={color.label}
              />
            ))}
          </div>
        </div>

        {/* Allowed Roles */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Allowed Roles
          </label>
          <p className="text-xs text-gray-500 mb-2">
            Who can trigger transitions from this step
          </p>
          <div className="space-y-2">
            {roleOptions.map((role) => (
              <label key={role.value} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.allowed_roles.includes(role.value)}
                  onChange={() => handleRoleToggle('allowed_roles', role.value)}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-sm">{role.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Notifications */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Notifications
          </h4>

          <label className="flex items-center gap-2 mb-2">
            <input
              type="checkbox"
              checked={formData.notify_client}
              onChange={(e) => handleChange('notify_client', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Notify client when entering this step</span>
          </label>

          <div>
            <label className="block text-sm text-gray-600 mb-1">
              Notify roles:
            </label>
            <div className="space-y-1">
              {roleOptions.filter(r => r.value !== 'user').map((role) => (
                <label key={role.value} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={formData.notify_roles.includes(role.value)}
                    onChange={() => handleRoleToggle('notify_roles', role.value)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm">{role.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Auto-assign */}
        <div className="border-t pt-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.auto_assign}
              onChange={(e) => handleChange('auto_assign', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm font-medium">Auto-assign to accountant</span>
          </label>
          <p className="mt-1 text-xs text-gray-500 ml-6">
            Automatically assign request to the least busy accountant when entering this step
          </p>
        </div>

        {/* Actions */}
        <div className="border-t pt-4 flex gap-2">
          <button
            type="submit"
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
          >
            Save Changes
          </button>
          {onDelete && (
            <button
              type="button"
              onClick={onDelete}
              className="px-4 py-2 border border-red-300 text-red-600 rounded-md text-sm font-medium hover:bg-red-50"
            >
              Delete
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
