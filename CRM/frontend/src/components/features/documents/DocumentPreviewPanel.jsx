import React, { useState, useEffect } from 'react';
import {
  XMarkIcon,
  ArrowDownTrayIcon,
  ShareIcon,
  DocumentIcon,
  DocumentTextIcon,
  PhotoIcon,
  TableCellsIcon,
  ArrowTopRightOnSquareIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  MagnifyingGlassPlusIcon,
  MagnifyingGlassMinusIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import Button from '../../common/Button';
import { documentsAPI } from '../../../services/api';

const getFileIcon = (fileType) => {
  const type = fileType?.toLowerCase();
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(type)) {
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
    form_attachment: 'Form Attachment',
  };
  return labels[category] || category || 'Document';
};

const getCategoryColor = (category) => {
  const colors = {
    supporting_document: 'bg-blue-100 text-blue-700',
    id_proof: 'bg-purple-100 text-purple-700',
    tax_document: 'bg-green-100 text-green-700',
    financial_statement: 'bg-yellow-100 text-yellow-700',
    invoice: 'bg-orange-100 text-orange-700',
    other: 'bg-gray-100 text-gray-700',
    form_attachment: 'bg-indigo-100 text-indigo-700',
  };
  return colors[category] || 'bg-gray-100 text-gray-700';
};

const isPreviewable = (fileType) => {
  const type = fileType?.toLowerCase();
  return ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'txt'].includes(type);
};

export default function DocumentPreviewPanel({
  isOpen,
  onClose,
  document,
  documents = [],
  onDocumentChange,
}) {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [imageZoom, setImageZoom] = useState(100);
  const [isAnimating, setIsAnimating] = useState(false);

  // Get current document index for navigation
  const currentIndex = documents.findIndex((d) => d.id === document?.id);
  const hasPrevious = currentIndex > 0;
  const hasNext = currentIndex < documents.length - 1;

  useEffect(() => {
    if (isOpen) {
      setIsAnimating(true);
      if (document) {
        loadPreview();
      }
    }
    return () => {
      setPreviewUrl(null);
      setError(null);
      setImageZoom(100);
    };
  }, [isOpen, document?.id]);

  const handleClose = () => {
    setIsAnimating(false);
    setTimeout(() => {
      onClose();
    }, 300);
  };

  const loadPreview = async () => {
    if (!document) return;

    setIsLoading(true);
    setError(null);

    try {
      const fileType = document.file_type?.toLowerCase();
      const isImg = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(fileType);

      // Use backend proxy for all previewable files to avoid CORS/auth issues with external storage
      const token = localStorage.getItem('access_token');
      const proxyUrl = documentsAPI.getProxyUrl(document.id);
      setPreviewUrl(`${proxyUrl}?token=${encodeURIComponent(token)}`);
    } catch (err) {
      console.error('Preview error:', err);
      setError(err.response?.data?.error || 'Failed to load preview');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    try {
      // Use proxy endpoint for reliable downloads
      const token = localStorage.getItem('access_token');
      const proxyUrl = documentsAPI.getProxyUrl(document.id);
      window.open(`${proxyUrl}?token=${encodeURIComponent(token)}`, '_blank');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to download');
    }
  };

  const handleShare = async () => {
    try {
      const response = await documentsAPI.createShareLink(document.id);
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

  const handleOpenInNewTab = () => {
    if (previewUrl) {
      window.open(previewUrl, '_blank');
    }
  };

  const handlePrevious = () => {
    if (hasPrevious && onDocumentChange) {
      onDocumentChange(documents[currentIndex - 1]);
    }
  };

  const handleNext = () => {
    if (hasNext && onDocumentChange) {
      onDocumentChange(documents[currentIndex + 1]);
    }
  };

  const handleZoomIn = () => {
    setImageZoom((prev) => Math.min(prev + 25, 200));
  };

  const handleZoomOut = () => {
    setImageZoom((prev) => Math.max(prev - 25, 50));
  };

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        handleClose();
      } else if (e.key === 'ArrowLeft' && hasPrevious) {
        handlePrevious();
      } else if (e.key === 'ArrowRight' && hasNext) {
        handleNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, hasPrevious, hasNext]);

  if (!isOpen) return null;

  const FileIcon = document ? getFileIcon(document.file_type) : DocumentIcon;
  const canPreview = document && isPreviewable(document.file_type);
  const isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(
    document?.file_type?.toLowerCase()
  );

  const renderPreview = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto" />
            <p className="mt-4 text-gray-500">Loading preview...</p>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <DocumentIcon className="h-16 w-16 mx-auto text-gray-300" />
            <p className="mt-4 text-gray-500">{error}</p>
            <Button variant="primary" className="mt-4" onClick={handleDownload}>
              Download Instead
            </Button>
          </div>
        </div>
      );
    }

    if (!canPreview) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <FileIcon className="h-20 w-20 mx-auto text-gray-300" />
            <p className="mt-4 text-gray-500 font-medium">{document?.original_filename}</p>
            <p className="text-sm text-gray-400 mt-1">
              Preview not available for .{document?.file_type} files
            </p>
            <Button variant="primary" className="mt-6" onClick={handleDownload}>
              Download File
            </Button>
          </div>
        </div>
      );
    }

    if (!previewUrl) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <DocumentIcon className="h-16 w-16 mx-auto text-gray-300" />
            <p className="mt-4 text-gray-500">No preview available</p>
          </div>
        </div>
      );
    }

    // PDF Preview
    if (document?.file_type?.toLowerCase() === 'pdf') {
      return (
        <iframe
          src={previewUrl}
          className="w-full h-full border-0"
          title={`Preview: ${document.original_filename}`}
        />
      );
    }

    // Image Preview
    if (isImage) {
      return (
        <div className="flex items-center justify-center h-full overflow-auto p-4 bg-gray-100">
          <img
            src={previewUrl}
            alt={document.original_filename}
            className="max-w-none rounded shadow-lg transition-transform duration-200"
            style={{ transform: `scale(${imageZoom / 100})` }}
            onError={() => setError('Failed to load image')}
          />
        </div>
      );
    }

    // Text file preview
    if (document?.file_type?.toLowerCase() === 'txt') {
      return (
        <iframe
          src={previewUrl}
          className="w-full h-full border-0 bg-white p-4 font-mono text-sm"
          title={`Preview: ${document.original_filename}`}
        />
      );
    }

    // Fallback
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <FileIcon className="h-16 w-16 mx-auto text-gray-300" />
          <p className="mt-4 text-gray-500">Preview not supported</p>
          <Button variant="primary" className="mt-4" onClick={handleDownload}>
            Download File
          </Button>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className={`fixed inset-0 bg-gray-500 transition-opacity duration-300 ${
          isAnimating ? 'bg-opacity-50' : 'bg-opacity-0'
        }`}
        onClick={handleClose}
      />

      {/* Panel */}
      <div className="fixed inset-y-0 right-0 flex max-w-full pl-10">
        <div
          className={`w-screen max-w-2xl transform transition-transform duration-300 ease-in-out ${
            isAnimating ? 'translate-x-0' : 'translate-x-full'
          }`}
        >
          <div className="flex h-full flex-col bg-white shadow-xl">
            {/* Header */}
            <div className="border-b border-gray-200 px-4 py-4 sm:px-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3 min-w-0 flex-1">
                  <div className="p-2 bg-gray-100 rounded-lg flex-shrink-0">
                    <FileIcon className="h-6 w-6 text-gray-500" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h2 className="text-lg font-semibold text-gray-900 truncate">
                      {document?.original_filename}
                    </h2>
                    <div className="flex items-center gap-2 mt-1">
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full ${getCategoryColor(
                          document?.document_category
                        )}`}
                      >
                        {getCategoryLabel(document?.document_category)}
                      </span>
                      <span className="text-xs text-gray-400">
                        {document?.file_size_formatted}
                      </span>
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  className="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  onClick={handleClose}
                >
                  <span className="sr-only">Close panel</span>
                  <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                </button>
              </div>

              {/* Action buttons */}
              <div className="flex items-center gap-2 mt-4">
                <Button
                  variant="secondary"
                  size="sm"
                  icon={ArrowDownTrayIcon}
                  onClick={handleDownload}
                >
                  Download
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  icon={ShareIcon}
                  onClick={handleShare}
                >
                  Share
                </Button>
                {previewUrl && (
                  <Button
                    variant="ghost"
                    size="sm"
                    icon={ArrowTopRightOnSquareIcon}
                    onClick={handleOpenInNewTab}
                  >
                    Open in Tab
                  </Button>
                )}

                {/* Zoom controls for images */}
                {isImage && previewUrl && (
                  <div className="flex items-center gap-1 ml-auto">
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={MagnifyingGlassMinusIcon}
                      onClick={handleZoomOut}
                      disabled={imageZoom <= 50}
                      title="Zoom out"
                    />
                    <span className="text-xs text-gray-500 w-12 text-center">
                      {imageZoom}%
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={MagnifyingGlassPlusIcon}
                      onClick={handleZoomIn}
                      disabled={imageZoom >= 200}
                      title="Zoom in"
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Preview Area */}
            <div className="flex-1 overflow-hidden bg-gray-50">
              {renderPreview()}
            </div>

            {/* Footer with navigation and metadata */}
            <div className="border-t border-gray-200 px-4 py-3 sm:px-6">
              <div className="flex items-center justify-between">
                {/* Navigation */}
                {documents.length > 1 ? (
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={ArrowLeftIcon}
                      onClick={handlePrevious}
                      disabled={!hasPrevious}
                    >
                      Previous
                    </Button>
                    <span className="text-sm text-gray-500">
                      {currentIndex + 1} of {documents.length}
                    </span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleNext}
                      disabled={!hasNext}
                    >
                      Next
                      <ArrowRightIcon className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                ) : (
                  <div />
                )}

                {/* Metadata */}
                <div className="text-xs text-gray-400 text-right">
                  {document?.uploaded_by && (
                    <p>Uploaded by {document.uploaded_by.full_name}</p>
                  )}
                  {document?.created_at && (
                    <p>{new Date(document.created_at).toLocaleString()}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
