import React, { useState } from 'react';
import {
  DocumentIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  EyeIcon,
  ShareIcon,
  DocumentTextIcon,
  PhotoIcon,
  TableCellsIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import Button from '../../common/Button';
import Modal from '../../common/Modal';
import DocumentPreviewPanel from './DocumentPreviewPanel';
import { documentsAPI } from '../../../services/api';

const getFileIcon = (fileType) => {
  const type = fileType?.toLowerCase();
  if (['jpg', 'jpeg', 'png', 'gif'].includes(type)) {
    return PhotoIcon;
  }
  if (['xls', 'xlsx', 'csv'].includes(type)) {
    return TableCellsIcon;
  }
  if (['doc', 'docx', 'pdf', 'txt'].includes(type)) {
    return DocumentTextIcon;
  }
  return DocumentIcon;
};

const getCategoryLabel = (category) => {
  const labels = {
    supporting_document: 'Supporting Doc',
    id_proof: 'ID Proof',
    tax_document: 'Tax Document',
    financial_statement: 'Financial Statement',
    invoice: 'Invoice',
    other: 'Other',
  };
  return labels[category] || category;
};

const getCategoryColor = (category) => {
  const colors = {
    supporting_document: 'bg-blue-100 text-blue-700',
    id_proof: 'bg-purple-100 text-purple-700',
    tax_document: 'bg-green-100 text-green-700',
    financial_statement: 'bg-yellow-100 text-yellow-700',
    invoice: 'bg-orange-100 text-orange-700',
    other: 'bg-gray-100 text-gray-700',
  };
  return colors[category] || 'bg-gray-100 text-gray-700';
};

export default function DocumentList({
  documents,
  onRefresh,
  showUploader = true,
  canDelete = true,
  compact = false,
  usePanel = true, // Use side panel preview by default
}) {
  const [isDeleting, setIsDeleting] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  const handleDownload = async (doc) => {
    try {
      const response = await documentsAPI.getDownloadUrl(doc.id);
      if (response.data.success && response.data.download_url) {
        // Open in new tab or trigger download
        window.open(response.data.download_url, '_blank');
      } else {
        toast.error('Failed to get download URL');
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to download');
    }
  };

  const handlePreview = async (doc) => {
    setSelectedDoc(doc);

    if (usePanel) {
      // Use side panel preview
      setIsPanelOpen(true);
    } else {
      // Use modal preview (legacy)
      try {
        const response = await documentsAPI.getDownloadUrl(doc.id);
        if (response.data.success) {
          // Use web URL for preview if available, otherwise download URL
          setPreviewUrl(response.data.web_url || response.data.download_url);
          setIsPreviewOpen(true);
        }
      } catch (error) {
        toast.error('Failed to load preview');
      }
    }
  };

  const handlePanelDocumentChange = (doc) => {
    setSelectedDoc(doc);
  };

  const handleDelete = async (doc) => {
    if (!window.confirm(`Are you sure you want to delete "${doc.original_filename}"?`)) {
      return;
    }

    setIsDeleting(doc.id);
    try {
      await documentsAPI.delete(doc.id);
      toast.success('Document deleted');
      if (onRefresh) onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete');
    } finally {
      setIsDeleting(null);
    }
  };

  const handleShare = async (doc) => {
    try {
      const response = await documentsAPI.createShareLink(doc.id);
      if (response.data.success && response.data.link) {
        await navigator.clipboard.writeText(response.data.link);
        toast.success('Share link copied to clipboard');
      } else {
        toast.error(response.data.error || 'Failed to create share link');
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create share link');
    }
  };

  if (!documents || documents.length === 0) {
    return (
      <div className={`text-center ${compact ? 'py-4' : 'py-8'} text-gray-500`}>
        <DocumentIcon className={`${compact ? 'h-8 w-8' : 'h-12 w-12'} mx-auto mb-2 text-gray-300`} />
        <p className={compact ? 'text-sm' : ''}>No documents uploaded yet</p>
      </div>
    );
  }

  if (compact) {
    return (
      <>
        <div className="space-y-2">
          {documents.map((doc) => {
            const FileIcon = getFileIcon(doc.file_type);
            return (
              <div
                key={doc.id}
                className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer"
                onClick={() => handlePreview(doc)}
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <FileIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  <span className="text-sm truncate">{doc.original_filename}</span>
                  <span
                    className={`text-xs px-1.5 py-0.5 rounded ${getCategoryColor(
                      doc.document_category
                    )}`}
                  >
                    {getCategoryLabel(doc.document_category)}
                  </span>
                </div>
                <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                  {['pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'txt'].includes(doc.file_type?.toLowerCase()) && (
                    <button
                      onClick={() => handlePreview(doc)}
                      className="p-1 text-gray-400 hover:text-primary-600"
                      title="Preview"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                  )}
                  <button
                    onClick={() => handleDownload(doc)}
                    className="p-1 text-gray-400 hover:text-primary-600"
                    title="Download"
                  >
                    <ArrowDownTrayIcon className="h-4 w-4" />
                  </button>
                  {canDelete && (
                    <button
                      onClick={() => handleDelete(doc)}
                      className="p-1 text-gray-400 hover:text-red-600"
                      disabled={isDeleting === doc.id}
                      title="Delete"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Side Panel Preview */}
        <DocumentPreviewPanel
          isOpen={isPanelOpen}
          onClose={() => setIsPanelOpen(false)}
          document={selectedDoc}
          documents={documents}
          onDocumentChange={handlePanelDocumentChange}
        />
      </>
    );
  }

  return (
    <>
      <div className="space-y-3">
        {documents.map((doc) => {
          const FileIcon = getFileIcon(doc.file_type);
          return (
            <div
              key={doc.id}
              className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-4 flex-1 min-w-0">
                <div className="p-2 bg-white rounded-lg shadow-sm">
                  <FileIcon className="h-6 w-6 text-gray-500" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-gray-900 truncate">
                    {doc.original_filename}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${getCategoryColor(
                        doc.document_category
                      )}`}
                    >
                      {getCategoryLabel(doc.document_category)}
                    </span>
                    <span className="text-xs text-gray-400">
                      {doc.file_size_formatted}
                    </span>
                    <span className="text-xs text-gray-400">
                      {new Date(doc.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {doc.uploaded_by && (
                    <p className="text-xs text-gray-400 mt-1">
                      Uploaded by {doc.uploaded_by.full_name}
                    </p>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 ml-4">
                {['pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'txt'].includes(doc.file_type?.toLowerCase()) && (
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={EyeIcon}
                    onClick={() => handlePreview(doc)}
                    title="Preview"
                  />
                )}
                <Button
                  variant="ghost"
                  size="sm"
                  icon={ShareIcon}
                  onClick={() => handleShare(doc)}
                  title="Share"
                />
                <Button
                  variant="ghost"
                  size="sm"
                  icon={ArrowDownTrayIcon}
                  onClick={() => handleDownload(doc)}
                  title="Download"
                />
                {canDelete && (
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={TrashIcon}
                    onClick={() => handleDelete(doc)}
                    loading={isDeleting === doc.id}
                    className="text-red-600 hover:bg-red-50"
                    title="Delete"
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Preview Modal (legacy) */}
      {!usePanel && (
        <Modal
          isOpen={isPreviewOpen}
          onClose={() => setIsPreviewOpen(false)}
          title={selectedDoc?.original_filename}
          size="xl"
        >
          <div className="min-h-96">
            {previewUrl && (
              <>
                {selectedDoc?.file_type?.toLowerCase() === 'pdf' ? (
                  <iframe
                    src={previewUrl}
                    className="w-full h-96 border rounded"
                    title="PDF Preview"
                  />
                ) : ['jpg', 'jpeg', 'png', 'gif'].includes(
                    selectedDoc?.file_type?.toLowerCase()
                  ) ? (
                  <img
                    src={previewUrl}
                    alt={selectedDoc?.original_filename}
                    className="max-w-full max-h-96 mx-auto rounded"
                  />
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    <DocumentIcon className="h-16 w-16 mx-auto mb-4 text-gray-300" />
                    <p>Preview not available for this file type</p>
                    <Button
                      variant="primary"
                      className="mt-4"
                      onClick={() => handleDownload(selectedDoc)}
                    >
                      Download File
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        </Modal>
      )}

      {/* Side Panel Preview */}
      <DocumentPreviewPanel
        isOpen={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
        document={selectedDoc}
        documents={documents}
        onDocumentChange={handlePanelDocumentChange}
      />
    </>
  );
}
