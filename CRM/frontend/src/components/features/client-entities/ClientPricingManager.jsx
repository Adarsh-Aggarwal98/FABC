import React, { useState, useEffect } from 'react';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  CurrencyDollarIcon,
  PercentBadgeIcon,
} from '@heroicons/react/24/outline';
import Card, { CardHeader } from '../../common/Card';
import Button from '../../common/Button';
import Modal from '../../common/Modal';
import Input, { TextArea, Select } from '../../common/Input';
import Badge from '../../common/Badge';
import { clientPricingAPI, servicesAPI } from '../../../services/api';
import useCompanyStore from '../../../store/companyStore';

/**
 * ClientPricingManager - Component for managing client-specific pricing
 *
 * Can be used for both individual users and client entities.
 *
 * @param {Object} props
 * @param {string} props.userId - User ID (for individual client pricing)
 * @param {string} props.entityId - Client Entity ID (for entity pricing)
 * @param {string} props.clientName - Display name of the client/entity
 */
export default function ClientPricingManager({
  userId = null,
  entityId = null,
  clientName = 'Client',
}) {
  const { formatPrice, getCurrencySettings } = useCompanyStore();
  const currencySettings = getCurrencySettings();

  const [pricingRecords, setPricingRecords] = useState([]);
  const [services, setServices] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRecord, setEditingRecord] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    service_id: '',
    custom_price: '',
    discount_percentage: '',
    notes: '',
    valid_from: '',
    valid_until: '',
  });

  useEffect(() => {
    fetchData();
  }, [userId, entityId]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [pricingRes, servicesRes] = await Promise.all([
        userId
          ? clientPricingAPI.getForUser(userId)
          : clientPricingAPI.getForEntity(entityId),
        servicesAPI.list({ active_only: true }),
      ]);

      setPricingRecords(pricingRes.data.data?.pricing || []);
      setServices(servicesRes.data.data?.services || []);
    } catch (error) {
      console.error('Failed to fetch pricing data:', error);
      toast.error('Failed to load pricing data');
    } finally {
      setIsLoading(false);
    }
  };

  const openCreateModal = () => {
    setEditingRecord(null);
    setFormData({
      service_id: '',
      custom_price: '',
      discount_percentage: '',
      notes: '',
      valid_from: '',
      valid_until: '',
    });
    setIsModalOpen(true);
  };

  const openEditModal = (record) => {
    setEditingRecord(record);
    setFormData({
      service_id: record.service_id,
      custom_price: record.custom_price || '',
      discount_percentage: record.discount_percentage || '',
      notes: record.notes || '',
      valid_from: record.valid_from || '',
      valid_until: record.valid_until || '',
    });
    setIsModalOpen(true);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const data = {
        service_id: parseInt(formData.service_id),
        custom_price: formData.custom_price ? parseFloat(formData.custom_price) : null,
        discount_percentage: formData.discount_percentage
          ? parseFloat(formData.discount_percentage)
          : null,
        notes: formData.notes || null,
        valid_from: formData.valid_from || null,
        valid_until: formData.valid_until || null,
      };

      // Add client reference
      if (userId) {
        data.user_id = userId;
      } else if (entityId) {
        data.client_entity_id = entityId;
      }

      if (editingRecord) {
        await clientPricingAPI.update(editingRecord.id, data);
        toast.success('Pricing updated successfully');
      } else {
        await clientPricingAPI.create(data);
        toast.success('Pricing created successfully');
      }

      setIsModalOpen(false);
      fetchData();
    } catch (error) {
      const message = error.response?.data?.error || 'Failed to save pricing';
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (recordId) => {
    if (!window.confirm('Are you sure you want to delete this pricing record?')) {
      return;
    }

    try {
      await clientPricingAPI.delete(recordId);
      toast.success('Pricing deleted successfully');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete pricing');
    }
  };

  // Get services that don't already have pricing
  const availableServices = services.filter(
    (service) =>
      !editingRecord &&
      !pricingRecords.find((p) => p.service_id === service.id && p.is_active)
  );

  // For editing, include the current service
  const serviceOptions = editingRecord
    ? services
    : availableServices;

  if (isLoading) {
    return (
      <Card>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader
        title="Custom Pricing"
        subtitle={`Manage custom service prices for ${clientName}`}
        action={
          <Button size="sm" icon={PlusIcon} onClick={openCreateModal}>
            Add Pricing
          </Button>
        }
      />

      {pricingRecords.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CurrencyDollarIcon className="h-12 w-12 mx-auto mb-3 text-gray-300" />
          <p className="mb-2">No custom pricing set</p>
          <p className="text-sm">
            Add custom prices or discounts for specific services
          </p>
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {pricingRecords.map((record) => (
            <div
              key={record.id}
              className={`py-4 flex items-center justify-between ${
                !record.is_valid_now ? 'opacity-50' : ''
              }`}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900">
                    {record.service?.name || `Service #${record.service_id}`}
                  </span>
                  {!record.is_active && (
                    <Badge status="error">Inactive</Badge>
                  )}
                  {record.is_active && !record.is_valid_now && (
                    <Badge status="warning">Expired</Badge>
                  )}
                </div>

                <div className="flex items-center gap-4 mt-1 text-sm text-gray-500">
                  {record.custom_price && (
                    <span className="flex items-center gap-1">
                      <CurrencyDollarIcon className="h-4 w-4" />
                      Custom: {formatPrice(record.custom_price)}
                    </span>
                  )}
                  {record.discount_percentage && (
                    <span className="flex items-center gap-1">
                      <PercentBadgeIcon className="h-4 w-4" />
                      {record.discount_percentage}% off
                    </span>
                  )}
                  {record.service?.base_price && (
                    <span className="text-gray-400">
                      (Base: {formatPrice(record.service.base_price)})
                    </span>
                  )}
                </div>

                {(record.valid_from || record.valid_until) && (
                  <p className="text-xs text-gray-400 mt-1">
                    Valid:{' '}
                    {record.valid_from
                      ? new Date(record.valid_from).toLocaleDateString()
                      : 'No start'}{' '}
                    -{' '}
                    {record.valid_until
                      ? new Date(record.valid_until).toLocaleDateString()
                      : 'No end'}
                  </p>
                )}

                {record.notes && (
                  <p className="text-xs text-gray-500 mt-1">{record.notes}</p>
                )}
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  icon={PencilSquareIcon}
                  onClick={() => openEditModal(record)}
                />
                <Button
                  variant="ghost"
                  size="sm"
                  icon={TrashIcon}
                  onClick={() => handleDelete(record.id)}
                  className="text-red-600 hover:text-red-700"
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingRecord ? 'Edit Custom Pricing' : 'Add Custom Pricing'}
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <Select
            label="Service"
            value={formData.service_id}
            onChange={(e) =>
              setFormData({ ...formData, service_id: e.target.value })
            }
            options={[
              { value: '', label: 'Select a service' },
              ...serviceOptions.map((s) => ({
                value: s.id,
                label: `${s.name}${s.base_price ? ` (Base: ${formatPrice(s.base_price)})` : ''}`,
              })),
            ]}
            required
            disabled={!!editingRecord}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label={`Custom Price (${currencySettings.currency_symbol})`}
              type="number"
              step="0.01"
              min="0"
              value={formData.custom_price}
              onChange={(e) =>
                setFormData({ ...formData, custom_price: e.target.value })
              }
              placeholder="0.00"
              helper="Fixed price for this client"
            />
            <Input
              label="Discount (%)"
              type="number"
              step="0.1"
              min="0"
              max="100"
              value={formData.discount_percentage}
              onChange={(e) =>
                setFormData({ ...formData, discount_percentage: e.target.value })
              }
              placeholder="0"
              helper="Percentage off base price"
            />
          </div>

          <p className="text-xs text-gray-500">
            Set either a custom price OR a discount percentage (not both).
            Custom price takes precedence if both are set.
          </p>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Valid From"
              type="date"
              value={formData.valid_from}
              onChange={(e) =>
                setFormData({ ...formData, valid_from: e.target.value })
              }
            />
            <Input
              label="Valid Until"
              type="date"
              value={formData.valid_until}
              onChange={(e) =>
                setFormData({ ...formData, valid_until: e.target.value })
              }
            />
          </div>

          <TextArea
            label="Notes"
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            placeholder="Optional notes about this pricing..."
            rows={2}
          />

          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button
              type="button"
              variant="secondary"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit" loading={isSubmitting}>
              {editingRecord ? 'Update' : 'Create'} Pricing
            </Button>
          </div>
        </form>
      </Modal>
    </Card>
  );
}
