import React, { useState, useEffect, useRef, useCallback } from 'react';
import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { UserIcon, DocumentIcon, ClipboardDocumentListIcon } from '@heroicons/react/24/solid';
import { searchAPI } from '../../services/api';
import { useNavigate } from 'react-router-dom';

export default function GlobalSearch({ placeholder = 'Search...', className = '' }) {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [results, setResults] = useState({ users: [], requests: [], documents: [] });
  const [loading, setLoading] = useState(false);
  const searchRef = useRef(null);
  const navigate = useNavigate();

  // Debounce search
  const debounce = (func, wait) => {
    let timeout;
    return (...args) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(this, args), wait);
    };
  };

  const performSearch = useCallback(
    debounce(async (searchQuery) => {
      if (!searchQuery || searchQuery.length < 2) {
        setResults({ users: [], requests: [], documents: [] });
        return;
      }

      setLoading(true);
      try {
        const response = await searchAPI.global(searchQuery, 'all', 5);
        setResults(response.data.data || { users: [], requests: [], documents: [] });
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setLoading(false);
      }
    }, 300),
    []
  );

  useEffect(() => {
    performSearch(query);
  }, [query, performSearch]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleResultClick = (type, item) => {
    setIsOpen(false);
    setQuery('');
    switch (type) {
      case 'user':
        navigate(`/clients/${item.id}`);
        break;
      case 'request':
        navigate(`/requests/${item.id}`);
        break;
      case 'document':
        navigate(`/documents/${item.id}`);
        break;
    }
  };

  const hasResults =
    results.users?.length > 0 ||
    results.requests?.length > 0 ||
    results.documents?.length > 0;

  return (
    <div className={`relative ${className}`} ref={searchRef}>
      <div className="relative">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsOpen(true)}
          placeholder={placeholder}
          className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
        />
        {query && (
          <button
            onClick={() => {
              setQuery('');
              setResults({ users: [], requests: [], documents: [] });
            }}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        )}
      </div>

      {isOpen && query.length >= 2 && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-96 overflow-auto">
          {loading ? (
            <div className="px-4 py-3 text-sm text-gray-500">Searching...</div>
          ) : !hasResults ? (
            <div className="px-4 py-3 text-sm text-gray-500">No results found</div>
          ) : (
            <>
              {results.users?.length > 0 && (
                <div className="p-2">
                  <div className="px-2 py-1 text-xs font-semibold text-gray-500 uppercase">
                    Clients
                  </div>
                  {results.users.map((user) => (
                    <button
                      key={user.id}
                      onClick={() => handleResultClick('user', user)}
                      className="w-full px-3 py-2 flex items-center gap-3 hover:bg-gray-50 rounded-lg text-left"
                    >
                      <UserIcon className="h-5 w-5 text-gray-400" />
                      <div>
                        <div className="text-sm font-medium">{user.full_name || user.email}</div>
                        <div className="text-xs text-gray-500">{user.email}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {results.requests?.length > 0 && (
                <div className="p-2 border-t border-gray-100">
                  <div className="px-2 py-1 text-xs font-semibold text-gray-500 uppercase">
                    Requests
                  </div>
                  {results.requests.map((request) => (
                    <button
                      key={request.id}
                      onClick={() => handleResultClick('request', request)}
                      className="w-full px-3 py-2 flex items-center gap-3 hover:bg-gray-50 rounded-lg text-left"
                    >
                      <ClipboardDocumentListIcon className="h-5 w-5 text-gray-400" />
                      <div>
                        <div className="text-sm font-medium">{request.service?.name}</div>
                        <div className="text-xs text-gray-500">{request.user?.email}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {results.documents?.length > 0 && (
                <div className="p-2 border-t border-gray-100">
                  <div className="px-2 py-1 text-xs font-semibold text-gray-500 uppercase">
                    Documents
                  </div>
                  {results.documents.map((doc) => (
                    <button
                      key={doc.id}
                      onClick={() => handleResultClick('document', doc)}
                      className="w-full px-3 py-2 flex items-center gap-3 hover:bg-gray-50 rounded-lg text-left"
                    >
                      <DocumentIcon className="h-5 w-5 text-gray-400" />
                      <div>
                        <div className="text-sm font-medium">{doc.original_filename}</div>
                        <div className="text-xs text-gray-500">{doc.category}</div>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
}
