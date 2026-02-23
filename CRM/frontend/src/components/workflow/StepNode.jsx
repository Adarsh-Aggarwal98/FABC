import { memo } from 'react';
import { Handle, Position } from 'reactflow';
import {
  PlayIcon,
  StopIcon,
  QuestionMarkCircleIcon,
  CogIcon,
} from '@heroicons/react/24/outline';

const stepTypeIcons = {
  START: PlayIcon,
  END: StopIcon,
  QUERY: QuestionMarkCircleIcon,
  NORMAL: CogIcon,
};

const stepColors = {
  gray: 'bg-gray-100 border-gray-400 text-gray-800',
  blue: 'bg-blue-100 border-blue-400 text-blue-800',
  green: 'bg-green-100 border-green-400 text-green-800',
  yellow: 'bg-yellow-100 border-yellow-400 text-yellow-800',
  orange: 'bg-orange-100 border-orange-400 text-orange-800',
  red: 'bg-red-100 border-red-400 text-red-800',
  purple: 'bg-purple-100 border-purple-400 text-purple-800',
  indigo: 'bg-indigo-100 border-indigo-400 text-indigo-800',
  pink: 'bg-pink-100 border-pink-400 text-pink-800',
};

const StepNode = memo(({ data, selected }) => {
  const {
    name,
    display_name,
    step_type = 'NORMAL',
    color = 'blue',
    description,
    onEdit,
    isCurrentStep,
  } = data;

  const Icon = stepTypeIcons[step_type] || CogIcon;
  const colorClass = stepColors[color] || stepColors.blue;

  return (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 shadow-sm min-w-[140px]
        ${colorClass}
        ${selected ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
        ${isCurrentStep ? 'ring-2 ring-green-500 ring-offset-2 animate-pulse' : ''}
        transition-all duration-200
      `}
    >
      {/* Source handle (outgoing) - not shown for END steps */}
      {step_type !== 'END' && (
        <Handle
          type="source"
          position={Position.Right}
          className="w-3 h-3 bg-gray-600 border-2 border-white"
        />
      )}

      {/* Target handle (incoming) - not shown for START steps */}
      {step_type !== 'START' && (
        <Handle
          type="target"
          position={Position.Left}
          className="w-3 h-3 bg-gray-600 border-2 border-white"
        />
      )}

      <div className="flex items-center gap-2">
        <Icon className="w-5 h-5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="font-medium text-sm truncate">
            {display_name || name}
          </div>
          {description && (
            <div className="text-xs opacity-70 truncate mt-0.5">
              {description}
            </div>
          )}
        </div>
      </div>

      {/* Step type badge */}
      <div className="mt-2 flex items-center justify-between">
        <span className="text-[10px] uppercase tracking-wider opacity-60">
          {step_type}
        </span>
        {onEdit && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onEdit(data);
            }}
            className="text-xs opacity-60 hover:opacity-100 transition-opacity"
          >
            Edit
          </button>
        )}
      </div>

      {/* Current step indicator */}
      {isCurrentStep && (
        <div className="absolute -top-2 -right-2 w-4 h-4 bg-green-500 rounded-full border-2 border-white flex items-center justify-center">
          <div className="w-2 h-2 bg-white rounded-full"></div>
        </div>
      )}
    </div>
  );
});

StepNode.displayName = 'StepNode';

export default StepNode;
