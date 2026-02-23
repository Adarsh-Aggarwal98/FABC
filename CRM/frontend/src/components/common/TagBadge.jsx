import React from 'react';
import { XMarkIcon } from '@heroicons/react/20/solid';

export default function TagBadge({ tag, onRemove, size = 'md', showRemove = true }) {
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  };

  const backgroundColor = tag.color || '#3B82F6';
  const isLightColor = isLight(backgroundColor);

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-medium ${sizes[size]}`}
      style={{
        backgroundColor: backgroundColor,
        color: isLightColor ? '#1f2937' : '#ffffff',
      }}
    >
      {tag.name}
      {showRemove && onRemove && (
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onRemove(tag);
          }}
          className="flex-shrink-0 rounded-full p-0.5 hover:bg-black/10 focus:outline-none"
        >
          <XMarkIcon className="h-3 w-3" />
        </button>
      )}
    </span>
  );
}

// Helper function to determine if a color is light
function isLight(color) {
  const hex = color.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;
  return brightness > 155;
}

export function TagList({ tags, onRemove, size = 'sm' }) {
  if (!tags || tags.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-1">
      {tags.map((tag) => (
        <TagBadge key={tag.id} tag={tag} onRemove={onRemove} size={size} showRemove={!!onRemove} />
      ))}
    </div>
  );
}
