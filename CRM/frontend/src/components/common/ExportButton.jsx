import React, { useState } from 'react';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import Button from './Button';

export default function ExportButton({
  onExport,
  filename = 'export',
  formats = ['csv', 'excel'],
  loading = false,
  className = '',
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [exporting, setExporting] = useState(false);

  const handleExport = async (format) => {
    setIsOpen(false);
    setExporting(true);
    try {
      const blob = await onExport(format);
      const extension = format === 'excel' ? 'xlsx' : 'csv';
      downloadBlob(blob, `${filename}.${extension}`);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setExporting(false);
    }
  };

  const downloadBlob = (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  if (formats.length === 1) {
    return (
      <Button
        variant="secondary"
        size="sm"
        onClick={() => handleExport(formats[0])}
        loading={exporting || loading}
        icon={ArrowDownTrayIcon}
        className={className}
      >
        Export
      </Button>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <Button
        variant="secondary"
        size="sm"
        onClick={() => setIsOpen(!isOpen)}
        loading={exporting || loading}
        icon={ArrowDownTrayIcon}
      >
        Export
      </Button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
          {formats.includes('csv') && (
            <button
              className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 first:rounded-t-lg"
              onClick={() => handleExport('csv')}
            >
              Export as CSV
            </button>
          )}
          {formats.includes('excel') && (
            <button
              className="w-full px-4 py-2 text-left text-sm hover:bg-gray-50 last:rounded-b-lg"
              onClick={() => handleExport('excel')}
            >
              Export as Excel
            </button>
          )}
        </div>
      )}
    </div>
  );
}
