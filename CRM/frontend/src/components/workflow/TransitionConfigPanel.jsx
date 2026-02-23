import { useState, useEffect } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';

const roleOptions = [
  { value: 'super_admin', label: 'Super Admin' },
  { value: 'admin', label: 'Admin' },
  { value: 'accountant', label: 'Accountant' },
  { value: 'user', label: 'Client' },
];

export default function TransitionConfigPanel({ transition, onSave, onClose, onDelete }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    requires_invoice_raised: false,
    requires_invoice_paid: false,
    requires_assignment: false,
    allowed_roles: [],
    send_notification: true,
    notification_template: '',
  });

  useEffect(() => {
    if (transition) {
      setFormData({
        name: transition.name || '',
        description: transition.description || '',
        requires_invoice_raised: transition.requires_invoice_raised || false,
        requires_invoice_paid: transition.requires_invoice_paid || false,
        requires_assignment: transition.requires_assignment || false,
        allowed_roles: transition.allowed_roles || [],
        send_notification: transition.send_notification !== false,
        notification_template: transition.notification_template || '',
      });
    }
  }, [transition]);

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleRoleToggle = (role) => {
    setFormData(prev => {
      const current = prev.allowed_roles || [];
      if (current.includes(role)) {
        return { ...prev, allowed_roles: current.filter(r => r !== role) };
      }
      return { ...prev, allowed_roles: [...current, role] };
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  if (!transition) return null;

  return (
    <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl border-l border-gray-200 z-50 overflow-y-auto">
      <div className="sticky top-0 bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Configure Transition</h3>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-100 rounded"
        >
          <XMarkIcon className="w-5 h-5" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="p-4 space-y-4">
        {/* Transition Name (Button Label) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Button Label
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => handleChange('name', e.target.value)}
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
            placeholder="e.g., Approve, Start Processing"
          />
          <p className="mt-1 text-xs text-gray-500">
            This text appears on the action button
          </p>
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
            placeholder="Optional description"
          />
        </div>

        {/* Conditions */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Conditions
          </h4>
          <p className="text-xs text-gray-500 mb-3">
            Requirements that must be met before this transition can be triggered
          </p>

          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.requires_invoice_raised}
                onChange={(e) => handleChange('requires_invoice_raised', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm">Invoice must be raised</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.requires_invoice_paid}
                onChange={(e) => handleChange('requires_invoice_paid', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm">Invoice must be paid</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.requires_assignment}
                onChange={(e) => handleChange('requires_assignment', e.target.checked)}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="text-sm">Request must be assigned</span>
            </label>
          </div>
        </div>

        {/* Allowed Roles */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Allowed Roles
          </h4>
          <p className="text-xs text-gray-500 mb-3">
            Who can trigger this transition
          </p>
          <div className="space-y-2">
            {roleOptions.map((role) => (
              <label key={role.value} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.allowed_roles.includes(role.value)}
                  onChange={() => handleRoleToggle(role.value)}
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

          <label className="flex items-center gap-2 mb-3">
            <input
              type="checkbox"
              checked={formData.send_notification}
              onChange={(e) => handleChange('send_notification', e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm">Send notification when triggered</span>
          </label>

          {formData.send_notification && (
            <div>
              <label className="block text-sm text-gray-600 mb-1">
                Custom notification message (optional):
              </label>
              <textarea
                value={formData.notification_template}
                onChange={(e) => handleChange('notification_template', e.target.value)}
                className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                rows={3}
                placeholder="Leave empty to use default message"
              />
            </div>
          )}
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
