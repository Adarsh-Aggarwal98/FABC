import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  PencilIcon,
  TrashIcon,
  PlusIcon,
  UserIcon,
  DocumentTextIcon,
  BuildingOffice2Icon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Badge from '../../components/common/Badge';
import Modal from '../../components/common/Modal';
import Input, { Select } from '../../components/common/Input';
import { ClientEntityForm, ClientPricingManager } from '../../components/features/client-entities';
import { clientEntitiesAPI, requestsAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

export default function ClientEntityDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuthStore();
  const [entity, setEntity] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [requests, setRequests] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isContactModalOpen, setIsContactModalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('details');

  const isAdmin =
    currentUser?.role === 'admin' ||
    currentUser?.role === 'super_admin';

  useEffect(() => {
    fetchEntityDetails();
  }, [id]);

  const fetchEntityDetails = async () => {
    setIsLoading(true);
    try {
      const [entityRes, contactsRes] = await Promise.all([
        clientEntitiesAPI.get(id),
        clientEntitiesAPI.getContacts(id),
      ]);

      setEntity(entityRes.data.data?.entity || entityRes.data.data);
      setContacts(contactsRes.data.data?.contacts || contactsRes.data.data || []);

      // Also fetch requests for this entity
      try {
        const requestsRes = await clientEntitiesAPI.getRequests(id);
        setRequests(requestsRes.data.data?.requests || requestsRes.data.data || []);
      } catch (e) {
        // Requests endpoint might not exist yet
        console.log('Could not fetch entity requests');
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch entity details');
      navigate('/client-entities');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditSuccess = (updatedEntity) => {
    setEntity(updatedEntity);
    setIsEditModalOpen(false);
    toast.success('Entity updated successfully');
  };

  const handleDelete = async () => {
    try {
      await clientEntitiesAPI.delete(id);
      toast.success('Entity deleted successfully');
      navigate('/client-entities');
    } catch (error) {
      toast.error('Failed to delete entity');
    }
  };

  const getEntityTypeLabel = (type) => {
    const labels = {
      COMPANY: 'Company',
      TRUST: 'Trust',
      SMSF: 'SMSF',
      PARTNERSHIP: 'Partnership',
      SOLE_TRADER: 'Sole Trader',
      INDIVIDUAL: 'Individual',
    };
    return labels[type] || type;
  };

  const getTrustTypeLabel = (type) => {
    const labels = {
      discretionary: 'Discretionary Trust',
      unit: 'Unit Trust',
      hybrid: 'Hybrid Trust',
      fixed: 'Fixed Trust',
      family: 'Family Trust',
      testamentary: 'Testamentary Trust',
    };
    return labels[type] || type;
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  if (!entity) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <p className="text-gray-500">Entity not found</p>
          <Link to="/client-entities">
            <Button variant="secondary" className="mt-4">
              Back to List
            </Button>
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <Link to="/client-entities">
              <Button variant="secondary" size="sm" icon={ArrowLeftIcon}>
                Back
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              <BuildingOffice2Icon className="h-8 w-8 text-gray-400" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {entity.name}
                </h1>
                <div className="flex items-center gap-2 mt-1">
                  <Badge status={entity.is_active ? 'success' : 'error'}>
                    {entity.is_active ? 'Active' : 'Inactive'}
                  </Badge>
                  <Badge>{getEntityTypeLabel(entity.entity_type)}</Badge>
                </div>
              </div>
            </div>
          </div>
          {isAdmin && (
            <div className="flex gap-2">
              <Button
                variant="secondary"
                icon={PencilIcon}
                onClick={() => setIsEditModalOpen(true)}
              >
                Edit
              </Button>
              <Button
                variant="danger"
                icon={TrashIcon}
                onClick={() => setIsDeleteModalOpen(true)}
              >
                Delete
              </Button>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'details', label: 'Details' },
              { id: 'contacts', label: `Contacts (${contacts.length})` },
              { id: 'requests', label: `Requests (${requests.length})` },
              ...(isAdmin ? [{ id: 'pricing', label: 'Pricing' }] : []),
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'details' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Basic Information */}
            <Card>
              <CardHeader title="Basic Information" />
              <dl className="divide-y divide-gray-200">
                <div className="py-3 flex justify-between">
                  <dt className="text-sm text-gray-500">Entity Name</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    {entity.name}
                  </dd>
                </div>
                {entity.trading_name && (
                  <div className="py-3 flex justify-between">
                    <dt className="text-sm text-gray-500">Trading Name</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      {entity.trading_name}
                    </dd>
                  </div>
                )}
                <div className="py-3 flex justify-between">
                  <dt className="text-sm text-gray-500">Entity Type</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    {getEntityTypeLabel(entity.entity_type)}
                  </dd>
                </div>
                {entity.abn && (
                  <div className="py-3 flex justify-between">
                    <dt className="text-sm text-gray-500">ABN</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      {entity.abn}
                    </dd>
                  </div>
                )}
                {entity.acn && (
                  <div className="py-3 flex justify-between">
                    <dt className="text-sm text-gray-500">ACN</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      {entity.acn}
                    </dd>
                  </div>
                )}
                {entity.tfn && (
                  <div className="py-3 flex justify-between">
                    <dt className="text-sm text-gray-500">TFN</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      {entity.tfn}
                    </dd>
                  </div>
                )}
              </dl>
            </Card>

            {/* Trust Details (if applicable) */}
            {entity.entity_type === 'TRUST' && (
              <Card>
                <CardHeader title="Trust Details" />
                <dl className="divide-y divide-gray-200">
                  {entity.trust_type && (
                    <div className="py-3 flex justify-between">
                      <dt className="text-sm text-gray-500">Trust Type</dt>
                      <dd className="text-sm font-medium text-gray-900">
                        {getTrustTypeLabel(entity.trust_type)}
                      </dd>
                    </div>
                  )}
                  {entity.trustee_name && (
                    <div className="py-3 flex justify-between">
                      <dt className="text-sm text-gray-500">Trustee Name</dt>
                      <dd className="text-sm font-medium text-gray-900">
                        {entity.trustee_name}
                      </dd>
                    </div>
                  )}
                  {entity.trust_deed_date && (
                    <div className="py-3 flex justify-between">
                      <dt className="text-sm text-gray-500">Trust Deed Date</dt>
                      <dd className="text-sm font-medium text-gray-900">
                        {new Date(entity.trust_deed_date).toLocaleDateString()}
                      </dd>
                    </div>
                  )}
                </dl>
              </Card>
            )}

            {/* Contact Information */}
            <Card>
              <CardHeader title="Contact Information" />
              <dl className="divide-y divide-gray-200">
                {entity.email && (
                  <div className="py-3 flex justify-between">
                    <dt className="text-sm text-gray-500">Email</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      <a
                        href={`mailto:${entity.email}`}
                        className="text-primary-600 hover:underline"
                      >
                        {entity.email}
                      </a>
                    </dd>
                  </div>
                )}
                {entity.phone && (
                  <div className="py-3 flex justify-between">
                    <dt className="text-sm text-gray-500">Phone</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      <a
                        href={`tel:${entity.phone}`}
                        className="text-primary-600 hover:underline"
                      >
                        {entity.phone}
                      </a>
                    </dd>
                  </div>
                )}
                {(entity.address_line1 || entity.city) && (
                  <div className="py-3">
                    <dt className="text-sm text-gray-500 mb-1">Address</dt>
                    <dd className="text-sm font-medium text-gray-900">
                      {entity.address_line1 && <p>{entity.address_line1}</p>}
                      {entity.address_line2 && <p>{entity.address_line2}</p>}
                      <p>
                        {[entity.city, entity.state, entity.postcode]
                          .filter(Boolean)
                          .join(', ')}
                      </p>
                      {entity.country && entity.country !== 'Australia' && (
                        <p>{entity.country}</p>
                      )}
                    </dd>
                  </div>
                )}
              </dl>
            </Card>

            {/* Financial Year */}
            <Card>
              <CardHeader title="Financial Year" />
              <dl className="divide-y divide-gray-200">
                <div className="py-3 flex justify-between">
                  <dt className="text-sm text-gray-500">FY End Date</dt>
                  <dd className="text-sm font-medium text-gray-900">
                    {entity.financial_year_end_day}/
                    {entity.financial_year_end_month}
                  </dd>
                </div>
              </dl>
            </Card>

            {/* Notes */}
            {entity.notes && (
              <Card className="lg:col-span-2">
                <CardHeader title="Notes" />
                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                  {entity.notes}
                </p>
              </Card>
            )}
          </div>
        )}

        {activeTab === 'contacts' && (
          <Card>
            <CardHeader
              title="Contacts"
              action={
                isAdmin && (
                  <Button
                    size="sm"
                    icon={PlusIcon}
                    onClick={() => setIsContactModalOpen(true)}
                  >
                    Add Contact
                  </Button>
                )
              }
            />
            {contacts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <UserIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>No contacts added yet</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {contacts.map((contact) => (
                  <div
                    key={contact.id}
                    className="py-4 flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center">
                        <UserIcon className="h-5 w-5 text-gray-500" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">
                          {contact.first_name} {contact.last_name}
                        </p>
                        {contact.position && (
                          <p className="text-sm text-gray-500">
                            {contact.position}
                          </p>
                        )}
                        <div className="flex gap-4 text-sm text-gray-500">
                          {contact.email && <span>{contact.email}</span>}
                          {contact.phone && <span>{contact.phone}</span>}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {contact.is_primary && (
                        <Badge status="success">Primary</Badge>
                      )}
                      {contact.effective_to && (
                        <Badge status="error">
                          Ended: {new Date(contact.effective_to).toLocaleDateString()}
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}

        {activeTab === 'requests' && (
          <Card>
            <CardHeader title="Service Requests" />
            {requests.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <DocumentTextIcon className="h-12 w-12 mx-auto mb-2 text-gray-300" />
                <p>No service requests for this entity yet</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {requests.map((request) => (
                  <Link
                    key={request.id}
                    to={`/requests/${request.id}`}
                    className="block py-4 hover:bg-gray-50"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-gray-900">
                          {request.request_number}
                        </p>
                        <p className="text-sm text-gray-500">
                          {request.service?.name}
                        </p>
                      </div>
                      <div className="text-right">
                        <Badge status={request.status}>
                          {request.status?.replace('_', ' ')}
                        </Badge>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(request.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </Card>
        )}

        {activeTab === 'pricing' && isAdmin && (
          <ClientPricingManager
            entityId={entity.id}
            clientName={entity.name}
          />
        )}
      </div>

      {/* Edit Modal */}
      {isEditModalOpen && (
        <ClientEntityForm
          entity={entity}
          isModal
          onSave={handleEditSuccess}
          onCancel={() => setIsEditModalOpen(false)}
        />
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        title="Delete Entity"
      >
        <p className="text-gray-600 mb-4">
          Are you sure you want to delete "{entity.name}"? This action will mark
          the entity as inactive but preserve historical data.
        </p>
        <div className="flex justify-end gap-3">
          <Button
            variant="secondary"
            onClick={() => setIsDeleteModalOpen(false)}
          >
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDelete}>
            Delete
          </Button>
        </div>
      </Modal>
    </DashboardLayout>
  );
}
