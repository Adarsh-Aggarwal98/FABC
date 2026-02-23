import React, { useState, useEffect, useRef } from 'react';
import {
  ChevronDownIcon,
  PlusIcon,
  MagnifyingGlassIcon,
  BuildingOffice2Icon,
  XMarkIcon,
} from '@heroicons/react/20/solid';
import { clientEntitiesAPI } from '../../../services/api';

/**
 * ClientEntitySelector - A searchable dropdown for selecting or creating client entities
 *
 * @param {Object} props
 * @param {Object} props.value - Currently selected entity (or null)
 * @param {Function} props.onChange - Callback when selection changes (receives entity or null)
 * @param {Function} props.onCreateNew - Callback to open create entity form (optional)
 * @param {string} props.placeholder - Placeholder text
 * @param {boolean} props.allowCreate - Whether to show "Create New" option
 * @param {boolean} props.clearable - Whether to allow clearing the selection
 * @param {boolean} props.disabled - Whether the selector is disabled
 * @param {string} props.error - Error message to display
 */
export default function ClientEntitySelector({
  value = null,
  onChange,
  onCreateNew,
  placeholder = 'Select client entity (optional)...',
  allowCreate = true,
  clearable = true,
  disabled = false,
  error = '',
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [entities, setEntities] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    loadEntities();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadEntities = async () => {
    try {
      setLoading(true);
      const response = await clientEntitiesAPI.list({ is_active: true });
      setEntities(response.data.data?.entities || response.data.data || []);
    } catch (error) {
      console.error('Failed to load client entities:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEntitySelect = (entity) => {
    onChange(entity);
    setIsOpen(false);
    setSearchQuery('');
  };

  const handleClear = (e) => {
    e.stopPropagation();
    onChange(null);
    setSearchQuery('');
  };

  const handleCreateNew = () => {
    setIsOpen(false);
    if (onCreateNew) {
      onCreateNew();
    }
  };

  const filteredEntities = entities.filter((entity) => {
    const query = searchQuery.toLowerCase();
    return (
      entity.name?.toLowerCase().includes(query) ||
      entity.trading_name?.toLowerCase().includes(query) ||
      entity.abn?.includes(query)
    );
  });

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

  const getEntityTypeColor = (type) => {
    const colors = {
      COMPANY: 'bg-blue-100 text-blue-800',
      TRUST: 'bg-purple-100 text-purple-800',
      SMSF: 'bg-green-100 text-green-800',
      PARTNERSHIP: 'bg-yellow-100 text-yellow-800',
      SOLE_TRADER: 'bg-orange-100 text-orange-800',
      INDIVIDUAL: 'bg-gray-100 text-gray-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <div
        className={`min-h-[42px] flex items-center px-3 py-2 border rounded-lg bg-white cursor-pointer ${
          disabled
            ? 'bg-gray-50 cursor-not-allowed'
            : isOpen
            ? 'ring-2 ring-primary-500 border-primary-500'
            : error
            ? 'border-red-300'
            : 'border-gray-300 hover:border-gray-400'
        }`}
        onClick={() => !disabled && setIsOpen(!isOpen)}
      >
        {value ? (
          <div className="flex-1 flex items-center gap-2">
            <BuildingOffice2Icon className="h-5 w-5 text-gray-400" />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-900">{value.name}</span>
                <span
                  className={`text-xs px-1.5 py-0.5 rounded ${getEntityTypeColor(
                    value.entity_type
                  )}`}
                >
                  {getEntityTypeLabel(value.entity_type)}
                </span>
              </div>
              {value.abn && (
                <span className="text-xs text-gray-500">ABN: {value.abn}</span>
              )}
            </div>
            {clearable && !disabled && (
              <button
                type="button"
                onClick={handleClear}
                className="text-gray-400 hover:text-gray-600"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            )}
          </div>
        ) : (
          <>
            <span className="flex-1 text-gray-500">{placeholder}</span>
            <ChevronDownIcon className="h-5 w-5 text-gray-400" />
          </>
        )}
      </div>

      {isOpen && !disabled && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-80 overflow-hidden">
          {/* Search input */}
          <div className="p-2 border-b border-gray-200">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                ref={inputRef}
                type="text"
                className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                placeholder="Search by name or ABN..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onClick={(e) => e.stopPropagation()}
                autoFocus
              />
            </div>
          </div>

          {/* Options list */}
          <div className="max-h-60 overflow-auto">
            {loading ? (
              <div className="px-4 py-3 text-sm text-gray-500">
                Loading entities...
              </div>
            ) : filteredEntities.length === 0 ? (
              <div className="px-4 py-3 text-sm text-gray-500">
                {searchQuery
                  ? 'No matching entities found'
                  : 'No client entities yet'}
              </div>
            ) : (
              filteredEntities.map((entity) => (
                <button
                  key={entity.id}
                  type="button"
                  className={`w-full px-4 py-3 text-left hover:bg-gray-50 flex items-start gap-3 border-b border-gray-100 last:border-b-0 ${
                    value?.id === entity.id ? 'bg-primary-50' : ''
                  }`}
                  onClick={() => handleEntitySelect(entity)}
                >
                  <BuildingOffice2Icon className="h-5 w-5 text-gray-400 mt-0.5" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900 truncate">
                        {entity.name}
                      </span>
                      <span
                        className={`text-xs px-1.5 py-0.5 rounded flex-shrink-0 ${getEntityTypeColor(
                          entity.entity_type
                        )}`}
                      >
                        {getEntityTypeLabel(entity.entity_type)}
                      </span>
                    </div>
                    {entity.trading_name && (
                      <p className="text-xs text-gray-500 truncate">
                        Trading as: {entity.trading_name}
                      </p>
                    )}
                    {entity.abn && (
                      <p className="text-xs text-gray-500">ABN: {entity.abn}</p>
                    )}
                  </div>
                </button>
              ))
            )}
          </div>

          {/* Create new option */}
          {allowCreate && onCreateNew && (
            <div className="border-t border-gray-200 p-2">
              <button
                type="button"
                className="w-full px-3 py-2 text-left text-sm font-medium text-primary-600 hover:bg-primary-50 rounded-md flex items-center gap-2"
                onClick={handleCreateNew}
              >
                <PlusIcon className="h-4 w-4" />
                Create New Client Entity
              </button>
            </div>
          )}
        </div>
      )}

      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  );
}
