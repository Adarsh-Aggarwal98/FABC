import { useState } from 'react';
import KanbanCard from './KanbanCard';
import TaskKanbanCard from './TaskKanbanCard';

export default function KanbanColumn({
  status,
  requests,
  onDrop,
  onCardClick,
  isLoading,
  accountants = [],
  onAssign,
  onTaskAssign,
  onDragStart,
  onDragEnd,
  isDropDisabled = false,
}) {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    if (isDropDisabled) {
      e.dataTransfer.dropEffect = 'none';
    } else {
      e.dataTransfer.dropEffect = 'move';
    }
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    if (isDropDisabled) return;
    const requestId = e.dataTransfer.getData('text/plain');
    if (requestId && onDrop) {
      onDrop(requestId, status.status_key);
    }
  };

  // Check WIP limit
  const isAtWipLimit = status.wip_limit && requests.length >= status.wip_limit;
  const isOverWipLimit = status.wip_limit && requests.length > status.wip_limit;

  return (
    <div
      className={`
        flex flex-col min-w-[280px] max-w-[320px] bg-gray-100 rounded-lg transition-opacity
        ${isDropDisabled ? 'opacity-40' : ''}
        ${isDragOver && !isAtWipLimit && !isDropDisabled ? 'ring-2 ring-blue-400 bg-blue-50' : ''}
        ${isDragOver && (isAtWipLimit || isDropDisabled) ? 'ring-2 ring-red-400 bg-red-50' : ''}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Column Header */}
      <div
        className="p-3 border-b border-gray-200"
        style={{ borderTopWidth: '3px', borderTopColor: status.color }}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-gray-900">{status.display_name}</h3>
            <span
              className={`
                text-xs px-2 py-0.5 rounded-full
                ${isOverWipLimit ? 'bg-red-100 text-red-800' : 'bg-gray-200 text-gray-700'}
              `}
            >
              {requests.length}
              {status.wip_limit && ` / ${status.wip_limit}`}
            </span>
          </div>
        </div>
        {status.description && (
          <p className="text-xs text-gray-500 mt-1">{status.description}</p>
        )}
      </div>

      {/* Cards Container */}
      <div className="flex-1 p-2 space-y-2 overflow-y-auto max-h-[calc(100vh-250px)]">
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin h-6 w-6 border-2 border-blue-500 rounded-full border-t-transparent"></div>
          </div>
        ) : requests.length === 0 ? (
          <div className="text-center py-8 text-gray-400 text-sm">
            No requests
          </div>
        ) : (
          requests.map((item) => (
            item._isTask ? (
              <TaskKanbanCard
                key={`task-${item.id}`}
                task={item}
                onClick={onCardClick}
                accountants={accountants}
                onAssign={onTaskAssign}
                onDragStart={() => onDragStart && onDragStart(item.status)}
                onDragEnd={onDragEnd}
              />
            ) : (
              <KanbanCard
                key={item.id}
                request={item}
                onClick={onCardClick}
                accountants={accountants}
                onAssign={onAssign}
                onDragStart={() => onDragStart && onDragStart(item.status)}
                onDragEnd={onDragEnd}
              />
            )
          ))
        )}
      </div>

      {/* Drop indicator when dragging over */}
      {isDragOver && (
        <div className="mx-2 mb-2 border-2 border-dashed border-blue-300 rounded-lg p-4 text-center text-blue-500 text-sm">
          Drop here
        </div>
      )}
    </div>
  );
}
