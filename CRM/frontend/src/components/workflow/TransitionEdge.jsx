import { memo } from 'react';
import { getBezierPath, EdgeLabelRenderer, BaseEdge } from 'reactflow';

const TransitionEdge = memo(({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  markerEnd,
  selected,
}) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const { name, onEdit, requires_invoice_raised, requires_invoice_paid, requires_assignment } = data || {};

  // Determine if this edge has conditions
  const hasConditions = requires_invoice_raised || requires_invoice_paid || requires_assignment;

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          stroke: selected ? '#3b82f6' : '#6b7280',
          strokeWidth: selected ? 2 : 1.5,
        }}
      />
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            pointerEvents: 'all',
          }}
          className="nodrag nopan"
        >
          {name && (
            <div
              className={`
                px-2 py-1 rounded text-xs font-medium shadow-sm border
                ${selected
                  ? 'bg-blue-100 border-blue-300 text-blue-800'
                  : 'bg-white border-gray-200 text-gray-700'
                }
                ${onEdit ? 'cursor-pointer hover:bg-gray-50' : ''}
                transition-colors
              `}
              onClick={() => onEdit && onEdit(data)}
            >
              <span>{name}</span>
              {hasConditions && (
                <span className="ml-1 text-yellow-600" title="Has conditions">
                  *
                </span>
              )}
            </div>
          )}
        </div>
      </EdgeLabelRenderer>
    </>
  );
});

TransitionEdge.displayName = 'TransitionEdge';

export default TransitionEdge;
