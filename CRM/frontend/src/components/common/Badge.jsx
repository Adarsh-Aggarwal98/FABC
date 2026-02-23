import React from 'react';

const statusColors = {
  pending: 'badge-pending',
  assigned: 'badge-assigned',
  query_raised: 'badge-query',
  accountant_review_pending: 'bg-indigo-100 text-indigo-800',
  processing: 'badge-processing',
  completed: 'badge-completed',
  active: 'badge-completed',
  inactive: 'bg-gray-100 text-gray-800',
  // New Kanban statuses
  collecting_docs: 'bg-purple-100 text-purple-800',
  in_progress: 'bg-blue-100 text-blue-800',
  review: 'bg-orange-100 text-orange-800',
  awaiting_client: 'bg-gray-100 text-gray-800',
  lodgement: 'bg-teal-100 text-teal-800',
  invoicing: 'bg-pink-100 text-pink-800',
  on_hold: 'bg-gray-200 text-gray-700',
  cancelled: 'bg-red-100 text-red-800',
};

const sizeClasses = {
  sm: 'text-xs px-1.5 py-0.5',
  md: 'text-sm px-2 py-0.5',
  lg: 'text-base px-3 py-1',
};

export default function Badge({ status, children, className = '', size = 'md' }) {
  const colorClass = statusColors[status] || 'bg-gray-100 text-gray-800';
  const sizeClass = sizeClasses[size] || sizeClasses.md;

  const displayText = children || status?.replace(/_/g, ' ');

  return (
    <span className={`badge ${colorClass} ${sizeClass} capitalize ${className}`}>
      {displayText}
    </span>
  );
}

export function RoleBadge({ role }) {
  const roleColors = {
    super_admin: 'bg-purple-100 text-purple-800',
    admin: 'bg-blue-100 text-blue-800',
    senior_accountant: 'bg-teal-100 text-teal-800',
    accountant: 'bg-green-100 text-green-800',
    external_accountant: 'bg-emerald-100 text-emerald-800',
    user: 'bg-gray-100 text-gray-800',
  };

  return (
    <span className={`badge ${roleColors[role] || 'bg-gray-100 text-gray-800'} capitalize`}>
      {role?.replace(/_/g, ' ')}
    </span>
  );
}
