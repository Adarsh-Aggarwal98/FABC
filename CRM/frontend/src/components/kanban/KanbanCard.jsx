import { useState, useRef } from 'react';
import { createPortal } from 'react-dom';
import { format } from 'date-fns';
import {
  UserIcon,
  CalendarIcon,
  ExclamationCircleIcon,
  ChevronDownIcon
} from '@heroicons/react/24/outline';

export default function KanbanCard({ request, onDragStart, onDragEnd, onClick, accountants = [], onAssign }) {
  const [isDragging, setIsDragging] = useState(false);
  const [showAssignDropdown, setShowAssignDropdown] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });
  const assignButtonRef = useRef(null);

  const handleDragStart = (e) => {
    setIsDragging(true);
    e.dataTransfer.setData('text/plain', request.id);
    e.dataTransfer.effectAllowed = 'move';
    if (onDragStart) onDragStart(request);
  };

  const handleDragEnd = () => {
    setIsDragging(false);
    if (onDragEnd) onDragEnd();
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'border-l-red-500 bg-red-50';
      case 'high': return 'border-l-orange-500 bg-orange-50';
      case 'normal': return 'border-l-blue-500';
      case 'low': return 'border-l-gray-400';
      default: return 'border-l-gray-300';
    }
  };

  const handleAssignClick = (e) => {
    e.stopPropagation();
    if (!showAssignDropdown && assignButtonRef.current) {
      const rect = assignButtonRef.current.getBoundingClientRect();
      const dropdownWidth = 192;
      const dropdownHeight = 200;

      // Position dropdown to the RIGHT of the button
      let top = rect.top;
      let left = rect.right + 8; // 8px to the right of button

      // If dropdown would go off right edge, show it to the left instead
      if (left + dropdownWidth > window.innerWidth - 8) {
        left = rect.left - dropdownWidth - 8;
      }

      // Ensure dropdown stays within vertical viewport
      if (top + dropdownHeight > window.innerHeight - 8) {
        top = window.innerHeight - dropdownHeight - 8;
      }
      if (top < 8) {
        top = 8;
      }

      setDropdownPosition({ top, left });
    }
    setShowAssignDropdown(!showAssignDropdown);
  };

  const handleAssignSelect = async (e, accountantId) => {
    e.stopPropagation();
    if (!onAssign || isAssigning) return;

    setIsAssigning(true);
    try {
      await onAssign(request.id, accountantId);
    } finally {
      setIsAssigning(false);
      setShowAssignDropdown(false);
    }
  };

  const isOverdue = request.deadline_date &&
    new Date(request.deadline_date) < new Date() &&
    request.status !== 'completed';

  return (
    <div
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onClick={() => onClick && onClick(request)}
      className={`
        bg-white rounded-lg shadow-sm border-l-4 p-3 cursor-grab active:cursor-grabbing
        transition-all duration-200 hover:shadow-md
        ${getPriorityColor(request.priority)}
        ${isDragging ? 'opacity-50 scale-95' : ''}
      `}
    >
      {/* Request Number & Service */}
      <div className="flex items-start justify-between mb-2">
        <div>
          <span className="text-xs font-medium text-gray-500">
            {request.request_number}
          </span>
          <h4 className="text-sm font-medium text-gray-900 line-clamp-1">
            {request.service?.name || 'Unknown Service'}
          </h4>
        </div>
        {isOverdue && (
          <ExclamationCircleIcon className="w-5 h-5 text-red-500 flex-shrink-0" />
        )}
      </div>

      {/* Client Entity or User */}
      <div className="flex items-center text-xs text-gray-600 mb-2">
        <UserIcon className="w-3.5 h-3.5 mr-1" />
        <span className="truncate">
          {request.client_entity?.name || request.user?.full_name || 'Unknown'}
        </span>
      </div>

      {/* Footer with deadline and assigned */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        {request.deadline_date && (
          <div className={`flex items-center ${isOverdue ? 'text-red-600' : ''}`}>
            <CalendarIcon className="w-3.5 h-3.5 mr-1" />
            <span>{format(new Date(request.deadline_date), 'MMM d')}</span>
          </div>
        )}

        {/* Staff Assignment Dropdown */}
        <div className="relative">
          <button
            ref={assignButtonRef}
            onClick={handleAssignClick}
            disabled={isAssigning || !onAssign}
            className={`
              flex items-center gap-1 px-2 py-1 rounded hover:bg-gray-100 transition
              ${isAssigning ? 'opacity-50' : ''}
              ${!onAssign ? 'cursor-default' : 'cursor-pointer'}
            `}
            title={request.assigned_accountant?.full_name || 'Unassigned'}
          >
            {request.assigned_accountant ? (
              <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium">
                {request.assigned_accountant.full_name?.charAt(0) || '?'}
              </div>
            ) : (
              <div className="w-5 h-5 rounded-full bg-gray-200 flex items-center justify-center text-gray-400">
                <UserIcon className="w-3 h-3" />
              </div>
            )}
            {onAssign && accountants.length > 0 && (
              <ChevronDownIcon className="w-3 h-3 text-gray-400" />
            )}
          </button>
        </div>
      </div>

      {/* Dropdown Portal - rendered in dedicated portal root */}
      {showAssignDropdown && accountants.length > 0 && createPortal(
        <>
          {/* Backdrop to close dropdown */}
          <div
            style={{
              position: 'fixed',
              inset: 0,
              zIndex: 99998,
              pointerEvents: 'auto',
            }}
            onClick={(e) => {
              e.stopPropagation();
              setShowAssignDropdown(false);
            }}
          />
          {/* Dropdown Menu */}
          <div
            style={{
              position: 'fixed',
              top: dropdownPosition.top,
              left: dropdownPosition.left,
              width: '192px',
              backgroundColor: 'white',
              borderRadius: '8px',
              boxShadow: '0 10px 25px rgba(0,0,0,0.15)',
              border: '1px solid #e5e7eb',
              padding: '4px 0',
              zIndex: 99999,
              pointerEvents: 'auto',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div className="px-3 py-1 text-xs text-gray-500 border-b">
              Assign to:
            </div>
            <div className="max-h-40 overflow-y-auto">
              {accountants.map((acc) => (
                <button
                  key={acc.id}
                  onClick={(e) => handleAssignSelect(e, acc.id)}
                  className={`
                    w-full text-left px-3 py-2 text-sm hover:bg-gray-50 flex items-center gap-2
                    ${request.assigned_accountant?.id === acc.id ? 'bg-blue-50 text-blue-700' : ''}
                  `}
                >
                  <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-xs font-medium">
                    {(acc.full_name || acc.first_name || 'U').charAt(0)}
                  </div>
                  <span className="truncate">
                    {acc.full_name || `${acc.first_name || ''} ${acc.last_name || ''}`.trim()}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </>,
        document.getElementById('dropdown-portal') || document.body
      )}
    </div>
  );
}
