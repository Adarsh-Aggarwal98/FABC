import React, { useState, useRef } from 'react';
import { CloudArrowUpIcon, XMarkIcon, DocumentIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import Button from '../../common/Button';
import { Select } from '../../common/Input';
import { documentsAPI } from '../../../services/api';

const DOCUMENT_CATEGORIES = [
  { value: 'supporting_document', label: 'Supporting Document' },
  { value: 'id_proof', label: 'ID Proof' },
  { value: 'tax_document', label: 'Tax Document' },
  { value: 'financial_statement', label: 'Financial Statement' },
  { value: 'invoice', label: 'Invoice' },
  { value: 'other', label: 'Other' },
];

const ALLOWED_EXTENSIONS = ['pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'txt'];
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export default function DocumentUpload({ serviceRequestId, onUploadComplete, compact = false }) {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [category, setCategory] = useState('supporting_document');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const fileInputRef = useRef(null);

  const validateFile = (file) => {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      toast.error(`File type .${ext} is not allowed`);
      return false;
    }
    if (file.size > MAX_FILE_SIZE) {
      toast.error(`File ${file.name} exceeds 50MB limit`);
      return false;
    }
    return true;
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    const validFiles = files.filter(validateFile);
    setSelectedFiles((prev) => [...prev, ...validFiles]);
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files);
    const validFiles = files.filter(validateFile);
    setSelectedFiles((prev) => [...prev, ...validFiles]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const removeFile = (index) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Please select files to upload');
      return;
    }

    setIsUploading(true);
    const results = [];

    for (let i = 0; i < selectedFiles.length; i++) {
      const file = selectedFiles[i];
      setUploadProgress((prev) => ({ ...prev, [i]: 0 }));

      try {
        const response = await documentsAPI.upload(file, serviceRequestId, category);
        setUploadProgress((prev) => ({ ...prev, [i]: 100 }));
        results.push({ success: true, file: file.name, data: response.data.document });
      } catch (error) {
        setUploadProgress((prev) => ({ ...prev, [i]: -1 }));
        results.push({
          success: false,
          file: file.name,
          error: error.response?.data?.error || 'Upload failed',
        });
      }
    }

    setIsUploading(false);

    const successCount = results.filter((r) => r.success).length;
    const failCount = results.filter((r) => !r.success).length;

    if (successCount > 0) {
      toast.success(`${successCount} file(s) uploaded successfully`);
    }
    if (failCount > 0) {
      toast.error(`${failCount} file(s) failed to upload`);
    }

    // Clear uploaded files
    setSelectedFiles([]);
    setUploadProgress({});

    if (onUploadComplete) {
      onUploadComplete(results);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  if (compact) {
    return (
      <div className="space-y-3">
        <div className="flex items-center gap-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            multiple
            className="hidden"
            accept={ALLOWED_EXTENSIONS.map((ext) => `.${ext}`).join(',')}
          />
          <Button
            variant="secondary"
            size="sm"
            icon={CloudArrowUpIcon}
            onClick={() => fileInputRef.current?.click()}
          >
            Add Files
          </Button>
          <Select
            options={DOCUMENT_CATEGORIES}
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="text-sm"
          />
        </div>

        {selectedFiles.length > 0 && (
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm"
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  <DocumentIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  <span className="truncate">{file.name}</span>
                  <span className="text-gray-400 text-xs flex-shrink-0">
                    ({formatFileSize(file.size)})
                  </span>
                </div>
                {uploadProgress[index] !== undefined ? (
                  <span
                    className={`text-xs ${
                      uploadProgress[index] === 100
                        ? 'text-green-600'
                        : uploadProgress[index] === -1
                        ? 'text-red-600'
                        : 'text-blue-600'
                    }`}
                  >
                    {uploadProgress[index] === 100
                      ? 'Done'
                      : uploadProgress[index] === -1
                      ? 'Failed'
                      : 'Uploading...'}
                  </span>
                ) : (
                  <button
                    onClick={() => removeFile(index)}
                    className="text-gray-400 hover:text-red-500"
                  >
                    <XMarkIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            ))}
            <Button
              size="sm"
              onClick={uploadFiles}
              loading={isUploading}
              disabled={isUploading}
            >
              Upload {selectedFiles.length} File(s)
            </Button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-primary-400 transition-colors cursor-pointer"
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          multiple
          className="hidden"
          accept={ALLOWED_EXTENSIONS.map((ext) => `.${ext}`).join(',')}
        />
        <CloudArrowUpIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600 mb-2">
          Drag and drop files here, or <span className="text-primary-600">browse</span>
        </p>
        <p className="text-gray-400 text-sm">
          Supported formats: {ALLOWED_EXTENSIONS.join(', ')} (max 50MB)
        </p>
      </div>

      {/* Category Selection */}
      <Select
        label="Document Category"
        options={DOCUMENT_CATEGORIES}
        value={category}
        onChange={(e) => setCategory(e.target.value)}
      />

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">
            Selected Files ({selectedFiles.length})
          </p>
          {selectedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <div className="flex items-center gap-3 flex-1 min-w-0">
                <DocumentIcon className="h-5 w-5 text-gray-400 flex-shrink-0" />
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-gray-400">{formatFileSize(file.size)}</p>
                </div>
              </div>
              {uploadProgress[index] !== undefined ? (
                <div className="flex items-center gap-2">
                  {uploadProgress[index] === 100 ? (
                    <span className="text-green-600 text-sm">Uploaded</span>
                  ) : uploadProgress[index] === -1 ? (
                    <span className="text-red-600 text-sm">Failed</span>
                  ) : (
                    <span className="text-blue-600 text-sm">Uploading...</span>
                  )}
                </div>
              ) : (
                <button
                  onClick={() => removeFile(index)}
                  className="text-gray-400 hover:text-red-500 p-1"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              )}
            </div>
          ))}

          <Button
            onClick={uploadFiles}
            loading={isUploading}
            disabled={isUploading}
            className="w-full"
          >
            Upload {selectedFiles.length} File(s)
          </Button>
        </div>
      )}
    </div>
  );
}
