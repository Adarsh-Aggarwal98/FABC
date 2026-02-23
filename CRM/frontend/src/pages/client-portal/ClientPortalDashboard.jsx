/**
 * ClientPortalDashboard — for 'user' role (SMSF clients)
 * Shows: linked fund info, audit request status, assignee, stage, time elapsed,
 *         query raised, and allows submitting the SMSF Basic Data Sheet.
 */
import React, { useEffect, useState } from 'react';
import {
  BuildingOffice2Icon,
  ClockIcon,
  UserCircleIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  ArrowUpTrayIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';
import { clientPortalAPI, smsfDataSheetAPI } from '../../services/api';
import DashboardLayout from '../../components/layout/DashboardLayout';
import useAuthStore from '../../store/authStore';
import toast from 'react-hot-toast';
import SMSFDataSheetForm from './SMSFDataSheetForm';

const STATUS_COLORS = {
  pending:      'bg-yellow-100 text-yellow-800',
  processing:   'bg-blue-100 text-blue-800',
  query_raised: 'bg-red-100 text-red-800',
  completed:    'bg-green-100 text-green-800',
  cancelled:    'bg-gray-100 text-gray-600',
};

export default function ClientPortalDashboard() {
  const { user } = useAuthStore();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showDataSheet, setShowDataSheet] = useState(false);
  const [uploading, setUploading] = useState(false);

  const fetchPortal = async () => {
    try {
      setLoading(true);
      const res = await clientPortalAPI.myPortal();
      setData(res.data);
    } catch (err) {
      toast.error('Failed to load portal data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortal();
  }, []);

  const handleDownloadPdf = async () => {
    try {
      const res = await clientPortalAPI.myPdf(true);
      const url = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const a = document.createElement('a');
      a.href = url;
      a.download = 'SMSF_DataSheet.pdf';
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      toast.error('Could not download PDF');
    }
  };

  const handleUploadSigned = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      setUploading(true);
      await clientPortalAPI.uploadSigned(file);
      toast.success('Signed document uploaded successfully');
    } catch {
      toast.error('Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDataSheetSubmitted = () => {
    setShowDataSheet(false);
    fetchPortal();
    toast.success('SMSF Data Sheet submitted! A PDF has been emailed to you.');
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  const { entity, request, data_sheet } = data || {};

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto py-8 px-4 space-y-6">

        {/* Welcome Banner */}
        <div className="bg-gradient-to-r from-[#1A2E5A] to-[#1B72BE] rounded-xl p-6 text-white">
          <h1 className="text-2xl font-bold mb-1">
            Welcome, {user?.first_name || user?.email}
          </h1>
          <p className="text-blue-200 text-sm">AusSuperSource Client Portal</p>
        </div>

        {/* Fund Details */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center gap-3 mb-4">
            <BuildingOffice2Icon className="h-6 w-6 text-[#1B72BE]" />
            <h2 className="text-lg font-semibold text-gray-900">Your SMSF Fund</h2>
          </div>
          {entity ? (
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Fund Name</span>
                <p className="font-semibold text-gray-900">{entity.name}</p>
              </div>
              <div>
                <span className="text-gray-500">ABN</span>
                <p className="font-semibold text-gray-900">{entity.abn || '—'}</p>
              </div>
              <div>
                <span className="text-gray-500">TFN</span>
                <p className="font-semibold text-gray-900">{entity.tfn || '—'}</p>
              </div>
              <div>
                <span className="text-gray-500">Address</span>
                <p className="font-semibold text-gray-900">{entity.address || '—'}</p>
              </div>
            </div>
          ) : (
            <p className="text-gray-400 italic">No fund linked to your account. Please contact your accountant.</p>
          )}
        </div>

        {/* Audit Request Status */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
          <div className="flex items-center gap-3 mb-4">
            <DocumentTextIcon className="h-6 w-6 text-[#1B72BE]" />
            <h2 className="text-lg font-semibold text-gray-900">SMSF Annual Audit</h2>
          </div>

          {request ? (
            <div className="space-y-4">
              {/* Status row */}
              <div className="flex items-center gap-3 flex-wrap">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${STATUS_COLORS[request.status] || 'bg-gray-100 text-gray-600'}`}>
                  {request.status?.replace(/_/g, ' ').toUpperCase()}
                </span>
                {request.request_number && (
                  <span className="text-xs text-gray-500">Ref: {request.request_number}</span>
                )}
                {request.priority && (
                  <span className="text-xs text-gray-500 capitalize">Priority: {request.priority}</span>
                )}
              </div>

              {/* Query raised alert */}
              {request.query_raised && (
                <div className="flex items-start gap-3 bg-red-50 border border-red-200 rounded-lg p-4">
                  <ExclamationTriangleIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-semibold text-red-700">Query Raised — Response Required</p>
                    {request.internal_notes && (
                      <p className="text-sm text-red-600 mt-1">{request.internal_notes}</p>
                    )}
                    <p className="text-xs text-red-500 mt-1">Please contact your accountant to respond.</p>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="flex items-start gap-2">
                  <UserCircleIcon className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-gray-500 block">Assigned To</span>
                    <span className="font-semibold text-gray-900">{request.assigned_to || 'Unassigned'}</span>
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <ClockIcon className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="text-gray-500 block">Time Elapsed</span>
                    <span className="font-semibold text-gray-900">{request.time_elapsed}</span>
                  </div>
                </div>
                <div>
                  <span className="text-gray-500 block">Current Stage</span>
                  <span className="font-semibold text-gray-900">{request.stage || 'Intake'}</span>
                </div>
              </div>

              {request.status === 'completed' && (
                <div className="flex items-center gap-2 text-green-600 text-sm">
                  <CheckCircleIcon className="h-5 w-5" />
                  <span>Your audit has been completed.</span>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-6">
              <p className="text-gray-500 mb-4">You haven't started your SMSF Annual Audit yet.</p>
              {entity && (
                <button
                  onClick={() => setShowDataSheet(true)}
                  className="bg-[#1B72BE] text-white px-6 py-2.5 rounded-lg font-medium hover:bg-[#1A2E5A] transition-colors"
                >
                  Start SMSF Annual Audit
                </button>
              )}
            </div>
          )}
        </div>

        {/* Data Sheet / Documents */}
        {data_sheet && (
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <DocumentTextIcon className="h-6 w-6 text-[#1B72BE]" />
                <h2 className="text-lg font-semibold text-gray-900">SMSF Basic Data Sheet</h2>
              </div>
              <span className="text-xs text-gray-500">FY{data_sheet.financial_year}</span>
            </div>

            <div className="flex gap-3 flex-wrap">
              <button
                onClick={handleDownloadPdf}
                className="flex items-center gap-2 border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm hover:bg-gray-50 transition-colors"
              >
                <ArrowDownTrayIcon className="h-4 w-4" />
                Download PDF
              </button>

              <label className="flex items-center gap-2 border border-[#1B72BE] text-[#1B72BE] px-4 py-2 rounded-lg text-sm hover:bg-blue-50 transition-colors cursor-pointer">
                <ArrowUpTrayIcon className="h-4 w-4" />
                {uploading ? 'Uploading...' : 'Upload Signed Document'}
                <input
                  type="file"
                  accept=".pdf,.jpg,.jpeg,.png"
                  className="hidden"
                  onChange={handleUploadSigned}
                  disabled={uploading}
                />
              </label>
            </div>
            <p className="text-xs text-gray-400 mt-3">
              Download the data sheet PDF, sign it, and upload the signed copy above.
            </p>
          </div>
        )}
      </div>

      {/* SMSF Data Sheet Modal */}
      {showDataSheet && (
        <SMSFDataSheetForm
          entity={entity}
          onClose={() => setShowDataSheet(false)}
          onSubmitted={handleDataSheetSubmitted}
        />
      )}
    </DashboardLayout>
  );
}
