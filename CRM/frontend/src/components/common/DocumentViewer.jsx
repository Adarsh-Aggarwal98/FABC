import React, { useState, useEffect } from 'react';
import { XMarkIcon, ArrowDownTrayIcon, ArrowTopRightOnSquareIcon } from '@heroicons/react/24/outline';
import { documentsAPI } from '../../services/api';
import toast from 'react-hot-toast';

export default function DocumentViewer({ docUrl, label, onClose }) {
  const [viewUrl, setViewUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fileType, setFileType] = useState(null);

  useEffect(() => {
    if (!docUrl) return;
    fetchViewUrl();
  }, [docUrl]);

  const fetchViewUrl = async () => {
    setLoading(true);
    const isDocumentId = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(docUrl);

    if (isDocumentId) {
      try {
        const response = await documentsAPI.getViewUrl(docUrl);
        if (response.data.success && response.data.view_url) {
          setViewUrl(response.data.view_url);
          const mime = response.data.mime_type || '';
          const filename = response.data.filename || '';
          setFileType(getFileType(mime, filename));
        } else {
          toast.error('Could not load document');
          onClose();
        }
      } catch {
        toast.error('Failed to load document');
        onClose();
      }
    } else {
      setViewUrl(docUrl);
      setFileType(getFileType('', docUrl));
    }
    setLoading(false);
  };

  const getFileType = (mime, filename) => {
    const lower = (filename || '').toLowerCase();
    if (mime.includes('pdf') || lower.endsWith('.pdf')) return 'pdf';
    if (mime.includes('image') || /\.(jpg|jpeg|png|gif|webp|bmp|svg)/.test(lower)) return 'image';
    return 'other';
  };

  // Close on Escape key
  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70" onClick={onClose} />

      {/* Viewer */}
      <div className="relative w-[90vw] h-[90vh] bg-white rounded-lg shadow-2xl flex flex-col overflow-hidden z-10">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b bg-gray-50">
          <h3 className="font-medium text-gray-900 truncate">{label || 'Document'}</h3>
          <div className="flex items-center gap-2">
            {viewUrl && (
              <>
                <a
                  href={viewUrl}
                  download
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                  title="Download"
                >
                  <ArrowDownTrayIcon className="w-5 h-5" />
                </a>
                <a
                  href={viewUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
                  title="Open in new tab"
                >
                  <ArrowTopRightOnSquareIcon className="w-5 h-5" />
                </a>
              </>
            )}
            <button
              onClick={onClose}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto flex items-center justify-center bg-gray-100">
          {loading ? (
            <div className="flex flex-col items-center gap-3">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600" />
              <p className="text-gray-500 text-sm">Loading document...</p>
            </div>
          ) : fileType === 'pdf' ? (
            <iframe
              src={viewUrl}
              className="w-full h-full border-0"
              title={label || 'PDF Document'}
            />
          ) : fileType === 'image' ? (
            <img
              src={viewUrl}
              alt={label || 'Document'}
              className="max-w-full max-h-full object-contain"
            />
          ) : (
            <div className="text-center p-8">
              <p className="text-gray-600 mb-4">This file type cannot be previewed in the browser.</p>
              <a
                href={viewUrl}
                download
                className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
              >
                <ArrowDownTrayIcon className="w-5 h-5" />
                Download File
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
