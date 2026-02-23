import { useCallback, useMemo, useState, useRef } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import StepNode from './StepNode';
import TransitionEdge from './TransitionEdge';

const nodeTypes = {
  stepNode: StepNode,
};

const edgeTypes = {
  transitionEdge: TransitionEdge,
};

const defaultEdgeOptions = {
  type: 'transitionEdge',
  markerEnd: {
    type: MarkerType.ArrowClosed,
    width: 20,
    height: 20,
    color: '#6b7280',
  },
  style: {
    strokeWidth: 1.5,
    stroke: '#6b7280',
  },
};

export default function FlowCanvas({
  workflow,
  onStepSelect,
  onTransitionSelect,
  onStepsChange,
  onTransitionsChange,
  onConnect,
  readOnly = false,
  currentStepId = null,
}) {
  const reactFlowWrapper = useRef(null);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);

  // Convert workflow steps to ReactFlow nodes
  const initialNodes = useMemo(() => {
    if (!workflow?.steps) return [];
    return workflow.steps.map((step) => ({
      id: step.id,
      type: 'stepNode',
      position: { x: step.position_x || 0, y: step.position_y || 0 },
      data: {
        ...step,
        isCurrentStep: step.id === currentStepId,
        onEdit: readOnly ? null : () => onStepSelect(step),
      },
    }));
  }, [workflow?.steps, currentStepId, onStepSelect, readOnly]);

  // Convert workflow transitions to ReactFlow edges
  const initialEdges = useMemo(() => {
    if (!workflow?.transitions) return [];
    return workflow.transitions.map((transition) => ({
      id: transition.id,
      source: transition.from_step_id,
      target: transition.to_step_id,
      type: 'transitionEdge',
      data: {
        ...transition,
        onEdit: readOnly ? null : () => onTransitionSelect(transition),
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20,
        color: '#6b7280',
      },
    }));
  }, [workflow?.transitions, onTransitionSelect, readOnly]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Handle node position changes
  const handleNodesChange = useCallback((changes) => {
    onNodesChange(changes);
    if (onStepsChange && changes.some(c => c.type === 'position' && c.dragging === false)) {
      // Update step positions after drag ends
      const updatedSteps = changes
        .filter(c => c.type === 'position' && c.position)
        .map(c => ({
          id: c.id,
          position_x: c.position.x,
          position_y: c.position.y,
        }));
      if (updatedSteps.length > 0) {
        onStepsChange(updatedSteps);
      }
    }
  }, [onNodesChange, onStepsChange]);

  // Handle new connections
  const handleConnect = useCallback((params) => {
    if (onConnect) {
      onConnect({
        from_step_id: params.source,
        to_step_id: params.target,
      });
    }
    setEdges((eds) => addEdge({
      ...params,
      type: 'transitionEdge',
      markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20,
        color: '#6b7280',
      },
    }, eds));
  }, [onConnect, setEdges]);

  // Handle node click
  const handleNodeClick = useCallback((event, node) => {
    if (!readOnly && onStepSelect) {
      const step = workflow?.steps?.find(s => s.id === node.id);
      if (step) {
        onStepSelect(step);
      }
    }
  }, [onStepSelect, workflow?.steps, readOnly]);

  // Handle edge click
  const handleEdgeClick = useCallback((event, edge) => {
    if (!readOnly && onTransitionSelect) {
      const transition = workflow?.transitions?.find(t => t.id === edge.id);
      if (transition) {
        onTransitionSelect(transition);
      }
    }
  }, [onTransitionSelect, workflow?.transitions, readOnly]);

  // Handle drag over for adding new nodes
  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  // Handle drop for adding new nodes
  const onDrop = useCallback((event) => {
    event.preventDefault();

    if (!reactFlowInstance || readOnly) return;

    const type = event.dataTransfer.getData('application/reactflow');
    if (!type) return;

    const position = reactFlowInstance.screenToFlowPosition({
      x: event.clientX,
      y: event.clientY,
    });

    // Trigger callback to create new step at this position
    if (onStepSelect) {
      onStepSelect({
        isNew: true,
        step_type: type,
        position_x: position.x,
        position_y: position.y,
      });
    }
  }, [reactFlowInstance, onStepSelect, readOnly]);

  return (
    <div className="h-full w-full" ref={reactFlowWrapper}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={readOnly ? undefined : handleNodesChange}
        onEdgesChange={readOnly ? undefined : onEdgesChange}
        onConnect={readOnly ? undefined : handleConnect}
        onNodeClick={handleNodeClick}
        onEdgeClick={handleEdgeClick}
        onInit={setReactFlowInstance}
        onDrop={readOnly ? undefined : onDrop}
        onDragOver={readOnly ? undefined : onDragOver}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        fitView
        proOptions={{ hideAttribution: true }}
        connectionLineStyle={{ stroke: '#6b7280', strokeWidth: 1.5 }}
        nodesDraggable={!readOnly}
        nodesConnectable={!readOnly}
        elementsSelectable={!readOnly}
        panOnDrag={true}
        zoomOnScroll={true}
      >
        <Background color="#e5e7eb" gap={16} />
        <Controls showInteractive={false} />
        {!readOnly && (
          <MiniMap
            nodeColor={(n) => {
              const step = workflow?.steps?.find(s => s.id === n.id);
              if (step?.step_type === 'START') return '#22c55e';
              if (step?.step_type === 'END') return '#ef4444';
              if (step?.step_type === 'QUERY') return '#f97316';
              return '#3b82f6';
            }}
            maskColor="rgba(0, 0, 0, 0.1)"
          />
        )}
      </ReactFlow>
    </div>
  );
}
