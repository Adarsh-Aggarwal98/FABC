import React, { useState, useEffect, useRef } from 'react';
import { ChevronDownIcon, PlusIcon, XMarkIcon } from '@heroicons/react/20/solid';
import { tagsAPI } from '../../services/api';
import TagBadge from './TagBadge';

export default function TagSelector({
  selectedTags = [],
  onTagsChange,
  userId,
  companyId,
  placeholder = 'Add tags...',
  allowCreate = false,
}) {
  const [isOpen, setIsOpen] = useState(false);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const dropdownRef = useRef(null);

  useEffect(() => {
    loadTags();
  }, [companyId]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const loadTags = async () => {
    try {
      setLoading(true);
      const response = await tagsAPI.list({ company_id: companyId });
      setTags(response.data.data.tags || []);
    } catch (error) {
      console.error('Failed to load tags:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTagSelect = async (tag) => {
    if (selectedTags.some((t) => t.id === tag.id)) return;

    if (userId) {
      try {
        await tagsAPI.assignTag(userId, tag.id);
        onTagsChange([...selectedTags, tag]);
      } catch (error) {
        console.error('Failed to assign tag:', error);
      }
    } else {
      onTagsChange([...selectedTags, tag]);
    }
    setSearchQuery('');
  };

  const handleTagRemove = async (tag) => {
    if (userId) {
      try {
        await tagsAPI.removeTag(userId, tag.id);
        onTagsChange(selectedTags.filter((t) => t.id !== tag.id));
      } catch (error) {
        console.error('Failed to remove tag:', error);
      }
    } else {
      onTagsChange(selectedTags.filter((t) => t.id !== tag.id));
    }
  };

  const filteredTags = tags.filter(
    (tag) =>
      tag.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
      !selectedTags.some((t) => t.id === tag.id)
  );

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="min-h-[42px] flex flex-wrap gap-1 p-2 border border-gray-300 rounded-lg bg-white focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-primary-500">
        {selectedTags.map((tag) => (
          <TagBadge key={tag.id} tag={tag} onRemove={handleTagRemove} size="sm" />
        ))}
        <input
          type="text"
          className="flex-1 min-w-[100px] outline-none text-sm"
          placeholder={selectedTags.length === 0 ? placeholder : ''}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => setIsOpen(true)}
        />
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="text-gray-400 hover:text-gray-600"
        >
          <ChevronDownIcon className="h-5 w-5" />
        </button>
      </div>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-auto">
          {loading ? (
            <div className="px-4 py-3 text-sm text-gray-500">Loading tags...</div>
          ) : filteredTags.length === 0 ? (
            <div className="px-4 py-3 text-sm text-gray-500">
              {searchQuery ? 'No matching tags found' : 'No tags available'}
            </div>
          ) : (
            filteredTags.map((tag) => (
              <button
                key={tag.id}
                type="button"
                className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                onClick={() => handleTagSelect(tag)}
              >
                <span
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: tag.color }}
                />
                <span className="text-sm">{tag.name}</span>
              </button>
            ))
          )}
        </div>
      )}
    </div>
  );
}
