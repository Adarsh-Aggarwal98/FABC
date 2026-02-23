import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  TrashIcon,
  ArrowDownTrayIcon,
  EyeIcon,
  XMarkIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  PhoneIcon,
  EnvelopeIcon,
  CalendarDaysIcon,
  ChatBubbleLeftIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Modal from '../../components/common/Modal';
import { leadsAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

const STATUS_COLORS = {
  new: 'bg-blue-100 text-blue-700',
  contacted: 'bg-yellow-100 text-yellow-700',
  converted: 'bg-green-100 text-green-700',
  closed: 'bg-gray-100 text-gray-600',
};

const FORM_TYPE_COLORS = {
  contact: 'bg-purple-100 text-purple-700',
  appointment: 'bg-indigo-100 text-indigo-700',
};

export default function Leads() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [leads, setLeads] = useState([]);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [pagination, setPagination] = useState({ page: 1, per_page: 20, total: 0, pages: 1 });

  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [formTypeFilter, setFormTypeFilter] = useState('');
  const [search, setSearch] = useState('');

  // Modal states
  const [viewingLead, setViewingLead] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [editingStatus, setEditingStatus] = useState('');
  const [editingNotes, setEditingNotes] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin';

  useEffect(() => {
    if (!isAdmin) {
      navigate('/dashboard');
      return;
    }
    fetchLeads();
    fetchStats();
  }, [isAdmin, pagination.page, statusFilter, formTypeFilter]);

  const fetchLeads = async () => {
    setIsLoading(true);
    try {
      const params = {
        page: pagination.page,
        per_page: pagination.per_page,
      };
      if (statusFilter) params.status = statusFilter;
      if (formTypeFilter) params.form_type = formTypeFilter;
      if (search) params.search = search;

      const response = await leadsAPI.getLeads(params);
      setLeads(response.data.leads || []);
      if (response.data.pagination) {
        setPagination(prev => ({ ...prev, ...response.data.pagination }));
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch leads');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await leadsAPI.getStats();
      setStats(response.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch lead stats');
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    setPagination(prev => ({ ...prev, page: 1 }));
    fetchLeads();
  };

  const handleExport = async () => {
    try {
      const response = await leadsAPI.exportLeads();
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `leads-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success('Export downloaded');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to export leads');
    }
  };

  const handleDelete = async (id) => {
    setIsDeleting(true);
    try {
      await leadsAPI.deleteLead(id);
      toast.success('Lead deleted');
      setShowDeleteConfirm(null);
      fetchLeads();
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete lead');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleViewLead = (lead) => {
    setViewingLead(lead);
    setEditingStatus(lead.status);
    setEditingNotes(lead.notes || '');
  };

  const handleSaveLead = async () => {
    if (!viewingLead) return;
    setIsSaving(true);
    try {
      const response = await leadsAPI.updateLead(viewingLead.id, {
        status: editingStatus,
        notes: editingNotes,
      });
      toast.success('Lead updated');
      setViewingLead(response.data.lead);
      fetchLeads();
      fetchStats();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update lead');
    } finally {
      setIsSaving(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    return new Date(dateStr).toLocaleDateString('en-AU', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Website Leads</h1>
            <p className="text-gray-600">Contact form and appointment submissions from the website</p>
          </div>
          <Button variant="outline" onClick={handleExport}>
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            Export JSON
          </Button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <Card className="p-4">
              <div className="text-sm text-gray-500">Total Leads</div>
              <div className="text-2xl font-bold">{stats.total || 0}</div>
            </Card>
            <Card className="p-4">
              <div className="text-sm text-gray-500">New</div>
              <div className="text-2xl font-bold text-blue-600">{stats.new || 0}</div>
            </Card>
            <Card className="p-4">
              <div className="text-sm text-gray-500">This Week</div>
              <div className="text-2xl font-bold">{stats.thisWeek || 0}</div>
            </Card>
            <Card className="p-4">
              <div className="text-sm text-gray-500">Contact Forms</div>
              <div className="text-2xl font-bold text-purple-600">{stats.contactCount || 0}</div>
            </Card>
            <Card className="p-4">
              <div className="text-sm text-gray-500">Appointments</div>
              <div className="text-2xl font-bold text-indigo-600">{stats.appointmentCount || 0}</div>
            </Card>
          </div>
        )}

        {/* Filters */}
        <Card className="p-4">
          <div className="flex flex-wrap items-center gap-3">
            <form onSubmit={handleSearch} className="flex-1 min-w-[200px]">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by name, email, phone..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  onBlur={() => { setPagination(prev => ({ ...prev, page: 1 })); fetchLeads(); }}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </form>
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPagination(prev => ({ ...prev, page: 1 })); }}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            >
              <option value="">All Statuses</option>
              <option value="new">New</option>
              <option value="contacted">Contacted</option>
              <option value="converted">Converted</option>
              <option value="closed">Closed</option>
            </select>
            <select
              value={formTypeFilter}
              onChange={(e) => { setFormTypeFilter(e.target.value); setPagination(prev => ({ ...prev, page: 1 })); }}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            >
              <option value="">All Types</option>
              <option value="contact">Contact Form</option>
              <option value="appointment">Appointment</option>
            </select>
          </div>
        </Card>

        {/* Leads Table */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold">All Leads</h2>
          </CardHeader>

          {isLoading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-gray-500">Loading leads...</p>
            </div>
          ) : leads.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <ChatBubbleLeftIcon className="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>No leads found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Type</th>
                    <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {lead.first_name} {lead.last_name}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">{lead.email}</td>
                      <td className="px-4 py-3 text-sm text-gray-600">{lead.phone || '-'}</td>
                      <td className="px-4 py-3 text-center">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${FORM_TYPE_COLORS[lead.form_type] || ''}`}>
                          {lead.form_type}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-center">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${STATUS_COLORS[lead.status] || ''}`}>
                          {lead.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {formatDate(lead.submitted_at)}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => handleViewLead(lead)}
                            className="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded"
                            title="View details"
                          >
                            <EyeIcon className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => setShowDeleteConfirm(lead.id)}
                            className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded"
                            title="Delete"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {pagination.total > pagination.per_page && (
            <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Showing {((pagination.page - 1) * pagination.per_page) + 1} to {Math.min(pagination.page * pagination.per_page, pagination.total)} of {pagination.total}
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPagination(p => ({ ...p, page: p.page - 1 }))}
                  disabled={pagination.page <= 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPagination(p => ({ ...p, page: p.page + 1 }))}
                  disabled={pagination.page >= pagination.pages}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </Card>

        {/* View/Edit Lead Modal */}
        <Modal
          isOpen={viewingLead !== null}
          onClose={() => setViewingLead(null)}
          title="Lead Details"
          size="lg"
        >
          {viewingLead && (
            <div className="space-y-4">
              {/* Contact Info */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <div className="text-xs text-gray-500">Name</div>
                  <div className="font-medium">{viewingLead.first_name} {viewingLead.last_name}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Email</div>
                  <div className="font-medium">
                    <a href={`mailto:${viewingLead.email}`} className="text-blue-600 hover:underline">{viewingLead.email}</a>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Phone</div>
                  <div className="font-medium">
                    {viewingLead.phone ? (
                      <a href={`tel:${viewingLead.phone}`} className="text-blue-600 hover:underline">{viewingLead.phone}</a>
                    ) : '-'}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Submitted</div>
                  <div className="font-medium">{formatDate(viewingLead.submitted_at)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">Form Type</div>
                  <div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${FORM_TYPE_COLORS[viewingLead.form_type] || ''}`}>
                      {viewingLead.form_type}
                    </span>
                  </div>
                </div>
                <div>
                  <div className="text-xs text-gray-500">IP Address</div>
                  <div className="font-medium text-sm">{viewingLead.ip_address || '-'}</div>
                </div>
              </div>

              {/* Appointment Details */}
              {viewingLead.form_type === 'appointment' && (
                <div className="p-4 bg-indigo-50 rounded-lg">
                  <h4 className="font-medium text-indigo-800 mb-2">Appointment Details</h4>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    {viewingLead.service && (
                      <div>
                        <span className="text-indigo-600">Service:</span> {viewingLead.service}
                      </div>
                    )}
                    {viewingLead.appointment_date && (
                      <div>
                        <span className="text-indigo-600">Date:</span> {viewingLead.appointment_date}
                      </div>
                    )}
                    {viewingLead.appointment_time && (
                      <div>
                        <span className="text-indigo-600">Time:</span> {viewingLead.appointment_time}
                      </div>
                    )}
                    {viewingLead.hear_about_us && (
                      <div>
                        <span className="text-indigo-600">Heard about us:</span> {viewingLead.hear_about_us}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Message */}
              {viewingLead.message && (
                <div>
                  <div className="text-xs text-gray-500 mb-1">Message</div>
                  <div className="p-3 bg-gray-50 rounded-lg text-sm whitespace-pre-wrap">{viewingLead.message}</div>
                </div>
              )}

              {/* Status & Notes */}
              <div className="border-t pt-4 space-y-3">
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Status</label>
                  <select
                    value={editingStatus}
                    onChange={(e) => setEditingStatus(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  >
                    <option value="new">New</option>
                    <option value="contacted">Contacted</option>
                    <option value="converted">Converted</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs text-gray-500 mb-1">Admin Notes</label>
                  <textarea
                    value={editingNotes}
                    onChange={(e) => setEditingNotes(e.target.value)}
                    rows={3}
                    placeholder="Add internal notes about this lead..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <Button variant="outline" onClick={() => setViewingLead(null)}>
                  Close
                </Button>
                <Button
                  onClick={handleSaveLead}
                  disabled={isSaving}
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </div>
          )}
        </Modal>

        {/* Delete Confirm Modal */}
        <Modal
          isOpen={showDeleteConfirm !== null}
          onClose={() => setShowDeleteConfirm(null)}
          title="Delete Lead"
        >
          <p className="text-gray-600 mb-4">
            Are you sure you want to delete this lead? This action cannot be undone.
          </p>
          <div className="flex justify-end gap-3">
            <Button variant="outline" onClick={() => setShowDeleteConfirm(null)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={() => handleDelete(showDeleteConfirm)} disabled={isDeleting}>
              {isDeleting ? 'Deleting...' : 'Delete'}
            </Button>
          </div>
        </Modal>
      </div>
    </DashboardLayout>
  );
}
