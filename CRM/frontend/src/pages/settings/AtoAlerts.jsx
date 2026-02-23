import React, { useState, useEffect } from 'react';
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  XMarkIcon,
  BellAlertIcon,
} from '@heroicons/react/24/outline';
import { atoAlertsAPI } from '../../services/api';
import DashboardLayout from '../../components/layout/DashboardLayout';
import toast from 'react-hot-toast';

const TYPE_OPTIONS = [
  { value: 'update', label: 'Update', color: 'bg-blue-100 text-blue-700' },
  { value: 'alert',  label: 'Alert',  color: 'bg-red-100 text-red-700'  },
  { value: 'reminder', label: 'Reminder', color: 'bg-yellow-100 text-yellow-700' },
];

const emptyForm = {
  title: '', type: 'update', link: '', active: true, priority: 0, expiresAt: '',
};

export default function AtoAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(null);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const res = await atoAlertsAPI.adminList();
      setAlerts(res.data?.alerts || []);
    } catch {
      toast.error('Failed to load ATO alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAlerts(); }, []);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyForm);
    setShowModal(true);
  };

  const openEdit = (alert) => {
    setEditing(alert);
    setForm({
      title: alert.title || '',
      type: alert.type || 'update',
      link: alert.link || '',
      active: alert.active !== false,
      priority: alert.priority ?? 0,
      expiresAt: alert.expiresAt ? alert.expiresAt.substring(0, 10) : '',
    });
    setShowModal(true);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    if (!form.title || !form.type || !form.link) {
      toast.error('Title, type, and link are required');
      return;
    }
    const payload = {
      ...form,
      priority: Number(form.priority) || 0,
      expiresAt: form.expiresAt || null,
    };
    try {
      setSaving(true);
      if (editing) {
        await atoAlertsAPI.update(editing.id, payload);
        toast.success('Alert updated');
      } else {
        await atoAlertsAPI.create(payload);
        toast.success('Alert created');
      }
      setShowModal(false);
      fetchAlerts();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Save failed');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this ATO alert?')) return;
    try {
      setDeleting(id);
      await atoAlertsAPI.delete(id);
      toast.success('Alert deleted');
      fetchAlerts();
    } catch {
      toast.error('Delete failed');
    } finally {
      setDeleting(null);
    }
  };

  const toggleActive = async (alert) => {
    try {
      await atoAlertsAPI.update(alert.id, { active: !alert.active });
      fetchAlerts();
    } catch {
      toast.error('Failed to update');
    }
  };

  const typeColor = (type) =>
    TYPE_OPTIONS.find(t => t.value === type)?.color || 'bg-gray-100 text-gray-600';

  const inputCls = 'w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500';
  const labelCls = 'block text-xs font-medium text-gray-600 mb-1';

  return (
    <DashboardLayout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">ATO Alerts</h1>
            <p className="text-sm text-gray-500 mt-1">Manage regulatory notices shown on the AusSuperSource website</p>
          </div>
          <button
            onClick={openCreate}
            className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
          >
            <PlusIcon className="h-4 w-4" />
            New Alert
          </button>
        </div>

        {/* Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          {loading ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
            </div>
          ) : alerts.length === 0 ? (
            <div className="text-center py-16 text-gray-400">
              <BellAlertIcon className="h-10 w-10 mx-auto mb-3 opacity-30" />
              <p>No ATO alerts yet. Create your first one!</p>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 font-semibold text-gray-600">Title</th>
                  <th className="text-center px-4 py-3 font-semibold text-gray-600">Type</th>
                  <th className="text-center px-4 py-3 font-semibold text-gray-600">Priority</th>
                  <th className="text-center px-4 py-3 font-semibold text-gray-600">Status</th>
                  <th className="text-left px-4 py-3 font-semibold text-gray-600">Expires</th>
                  <th className="text-right px-4 py-3 font-semibold text-gray-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {alerts.map(alert => (
                  <tr key={alert.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="font-medium text-gray-900">{alert.title}</div>
                      <a href={alert.link} target="_blank" rel="noopener noreferrer"
                        className="text-xs text-blue-500 hover:underline truncate block max-w-xs">
                        {alert.link}
                      </a>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${typeColor(alert.type)}`}>
                        {alert.type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center text-gray-600">{alert.priority}</td>
                    <td className="px-4 py-3 text-center">
                      <button
                        onClick={() => toggleActive(alert)}
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          alert.active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                        }`}
                      >
                        {alert.active ? 'Active' : 'Inactive'}
                      </button>
                    </td>
                    <td className="px-4 py-3 text-gray-500 text-xs">
                      {alert.expiresAt ? new Date(alert.expiresAt).toLocaleDateString() : '—'}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button onClick={() => openEdit(alert)}
                          className="text-gray-400 hover:text-primary-600 transition-colors" title="Edit">
                          <PencilSquareIcon className="h-4 w-4" />
                        </button>
                        <button onClick={() => handleDelete(alert.id)} disabled={deleting === alert.id}
                          className="text-gray-400 hover:text-red-500 transition-colors disabled:opacity-40" title="Delete">
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-start justify-center p-4 overflow-y-auto">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg my-6">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between rounded-t-2xl z-10">
              <h2 className="text-lg font-bold text-gray-900">
                {editing ? 'Edit ATO Alert' : 'New ATO Alert'}
              </h2>
              <button onClick={() => setShowModal(false)}>
                <XMarkIcon className="h-6 w-6 text-gray-400 hover:text-gray-600" />
              </button>
            </div>

            <form onSubmit={handleSave} className="p-6 space-y-4">
              <div>
                <label className={labelCls}>Title *</label>
                <input className={inputCls} value={form.title}
                  onChange={e => setForm(f => ({ ...f, title: e.target.value }))} required />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className={labelCls}>Type *</label>
                  <select className={inputCls} value={form.type}
                    onChange={e => setForm(f => ({ ...f, type: e.target.value }))} required>
                    {TYPE_OPTIONS.map(t => (
                      <option key={t.value} value={t.value}>{t.label}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className={labelCls}>Priority (0 = highest)</label>
                  <input type="number" className={inputCls} value={form.priority} min={0}
                    onChange={e => setForm(f => ({ ...f, priority: e.target.value }))} />
                </div>
              </div>
              <div>
                <label className={labelCls}>Link (ATO URL) *</label>
                <input className={inputCls} value={form.link} type="url"
                  onChange={e => setForm(f => ({ ...f, link: e.target.value }))}
                  placeholder="https://www.ato.gov.au/..." required />
              </div>
              <div>
                <label className={labelCls}>Expires At (optional)</label>
                <input type="date" className={inputCls} value={form.expiresAt}
                  onChange={e => setForm(f => ({ ...f, expiresAt: e.target.value }))} />
              </div>
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="rounded" checked={form.active}
                  onChange={e => setForm(f => ({ ...f, active: e.target.checked }))} />
                <span className="text-sm text-gray-700">Active (shown on website)</span>
              </label>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                <button type="button" onClick={() => setShowModal(false)}
                  className="px-5 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50">
                  Cancel
                </button>
                <button type="submit" disabled={saving}
                  className="px-6 py-2 bg-primary-600 text-white rounded-lg text-sm font-semibold hover:bg-primary-700 disabled:opacity-50">
                  {saving ? 'Saving...' : (editing ? 'Update Alert' : 'Create Alert')}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
