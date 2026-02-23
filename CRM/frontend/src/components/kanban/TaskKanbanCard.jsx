import { useState, useRef } from 'react';
import { createPortal } from 'react-dom';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import {
  UserIcon,
  CalendarIcon,
  ClockIcon,
  LinkIcon,
  ExclamationCircleIcon,
  ChevronDownIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

export default function TaskKanbanCard({
  task,
  onDragStart,
  onDragEnd,
  onClick,
  accountants = [],
  onAssign,
  compact = false,
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [showAssignDropdown, setShowAssignDropdown] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0 });
  const assignButtonRef = useRef(null);

  const handleDragStart = (e) => {
    setIsDragging(true);
    e.dataTransfer.setData('text/plain', task.id);
    e.dataTransfer.effectAllowed = 'move';
    if (onDragStart) onDragStart(task);
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

  const getPriorityBadge = (priority) => {
    const colors = {
      urgent: 'bg-red-100 text-red-700',
      high: 'bg-orange-100 text-orange-700',
      normal: 'bg-blue-100 text-blue-700',
      low: 'bg-gray-100 text-gray-600',
    };
    return colors[priority] || colors.normal;
  };

  const handleAssignClick = (e) => {
    e.stopPropagation();
    if (!showAssignDropdown && assignButtonRef.current) {
      const rect = assignButtonRef.current.getBoundingClientRect();
      const dropdownWidth = 192;
      const dropdownHeight = 200;

      let top = rect.top;
      let left = rect.right + 8;

      if (left + dropdownWidth > window.innerWidth - 8) {
        left = rect.left - dropdownWidth - 8;
      }

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
      await onAssign(task.id, accountantId);
    } finally {
      setIsAssigning(false);
      setShowAssignDropdown(false);
    }
  };

  const isOverdue = task.due_date &&
    new Date(task.due_date) < new Date() &&
    task.status !== 'completed';

  const isDone = task.status === 'completed';

  return (
    <div
      draggable
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onClick={() => onClick && onClick(task)}
      className={`
        bg-white rounded-lg shadow-sm border-l-4 cursor-grab active:cursor-grabbing
        transition-all duration-200 hover:shadow-md
        ${getPriorityColor(task.priority)}
        ${isDragging ? 'opacity-50 scale-95' : ''}
        ${isDone ? 'opacity-75' : ''}
        ${compact ? 'p-2' : 'p-3'}
      `}
    >
      {/* Title & Priority */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1 min-w-0">
          <h4 className={`font-medium text-gray-900 ${compact ? 'text-xs line-clamp-1' : 'text-sm line-clamp-2'} ${isDone ? 'line-through text-gray-500' : ''}`}>
            {task.title}
          </h4>
        </div>
        <div className="flex items-center gap-1 ml-2 flex-shrink-0">
          {isDone && (
            <CheckCircleIcon className="w-4 h-4 text-green-500" />
          )}
          {isOverdue && !isDone && (
            <ExclamationCircleIcon className="w-4 h-4 text-red-500" />
          )}
        </div>
      </div>

      {/* Description preview (non-compact only) */}
      {!compact && task.description && (
        <p className="text-xs text-gray-500 mb-2 line-clamp-2">
          {task.description}
        </p>
      )}

      {/* Linked Request */}
      {task.service_request && (
        <Link
          to={`/requests/${task.service_request.id}`}
          onClick={(e) => e.stopPropagation()}
          className="flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 mb-2"
        >
          <LinkIcon className="h-3 w-3" />
          <span className="truncate">{task.service_request.request_number}</span>
        </Link>
      )}

      {/* Priority badge (only show for non-normal) */}
      {task.priority !== 'normal' && !compact && (
        <span className={`inline-block text-xs px-1.5 py-0.5 rounded mb-2 ${getPriorityBadge(task.priority)}`}>
          {task.priority}
        </span>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <div className="flex items-center gap-2">
          {/* Due date */}
          {task.due_date && (
            <div className={`flex items-center ${isOverdue && !isDone ? 'text-red-600 font-medium' : ''}`}>
              <CalendarIcon className="w-3 h-3 mr-0.5" />
              <span>{format(new Date(task.due_date), 'MMM d')}</span>
            </div>
          )}

          {/* Time estimate */}
          {task.estimated_minutes && !compact && (
            <div className="flex items-center text-gray-400">
              <ClockIcon className="w-3 h-3 mr-0.5" />
              <span>{Math.round(task.estimated_minutes / 60)}h</span>
            </div>
          )}
        </div>

        {/* Assignee */}
        <div className="relative">
          <button
            ref={assignButtonRef}
            onClick={handleAssignClick}
            disabled={isAssigning || !onAssign}
            className={`
              flex items-center gap-1 px-1.5 py-0.5 rounded hover:bg-gray-100 transition
              ${isAssigning ? 'opacity-50' : ''}
              ${!onAssign ? 'cursor-default' : 'cursor-pointer'}
            `}
            title={task.assigned_to?.full_name || 'Unassigned'}
          >
            {task.assigned_to ? (
              <div className="w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium text-xs">
                {task.assigned_to.full_name?.charAt(0) || task.assigned_to.first_name?.charAt(0) || '?'}
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

      {/* Dropdown Portal */}
      {showAssignDropdown && accountants.length > 0 && createPortal(
        <>
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
                    ${task.assigned_to?.id === acc.id ? 'bg-blue-50 text-blue-700' : ''}
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
