import { useState, useEffect, useMemo } from 'react';
import { workflowsAPI } from '../../services/api';
import {
  PlayIcon,
  StopIcon,
  QuestionMarkCircleIcon,
  CogIcon,
  CheckIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';

const stepTypeIcons = {
  START: PlayIcon,
  END: StopIcon,
  QUERY: QuestionMarkCircleIcon,
  NORMAL: CogIcon,
};

const stepColors = {
  gray: 'bg-gray-100 border-gray-300 text-gray-700',
  blue: 'bg-blue-100 border-blue-300 text-blue-700',
  green: 'bg-green-100 border-green-300 text-green-700',
  yellow: 'bg-yellow-100 border-yellow-300 text-yellow-700',
  orange: 'bg-orange-100 border-orange-300 text-orange-700',
  red: 'bg-red-100 border-red-300 text-red-700',
  purple: 'bg-purple-100 border-purple-300 text-purple-700',
  indigo: 'bg-indigo-100 border-indigo-300 text-indigo-700',
  pink: 'bg-pink-100 border-pink-300 text-pink-700',
};

export default function WorkflowPreview({ requestId, currentStepId, onTransitionClick }) {
  const [workflowData, setWorkflowData] = useState(null);
  const [transitions, setTransitions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (requestId) {
      loadWorkflowData();
    }
  }, [requestId, currentStepId]);

  const loadWorkflowData = async () => {
    try {
      setLoading(true);
      const [workflowRes, transitionsRes] = await Promise.all([
        workflowsAPI.getRequestWorkflow(requestId),
        workflowsAPI.getRequestTransitions(requestId),
      ]);

      setWorkflowData(workflowRes.data.data);
      setTransitions(transitionsRes.data.data.available_transitions || []);
    } catch (error) {
      console.error('Failed to load workflow data', error);
    } finally {
      setLoading(false);
    }
  };

  // Sort steps by order
  const sortedSteps = useMemo(() => {
    if (!workflowData?.workflow?.steps) return [];
    return [...workflowData.workflow.steps].sort((a, b) => a.order - b.order);
  }, [workflowData]);

  // Find current step index
  const currentStepIndex = useMemo(() => {
    const currentId = workflowData?.current_step_id || currentStepId;
    return sortedSteps.findIndex(s => s.id === currentId);
  }, [sortedSteps, workflowData, currentStepId]);

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-16 bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (!workflowData?.workflow) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-3">Workflow Progress</h3>

      {/* Linear workflow visualization */}
      <div className="flex items-center overflow-x-auto pb-2">
        {sortedSteps.map((step, index) => {
          const Icon = stepTypeIcons[step.step_type] || CogIcon;
          const isCurrentStep = index === currentStepIndex;
          const isPastStep = index < currentStepIndex;
          const colorClass = stepColors[step.color] || stepColors.blue;

          return (
            <div key={step.id} className="flex items-center flex-shrink-0">
              {/* Step */}
              <div
                className={`
                  relative flex items-center gap-2 px-3 py-2 rounded-lg border-2
                  ${isCurrentStep
                    ? `${colorClass} ring-2 ring-blue-500 ring-offset-2`
                    : isPastStep
                      ? 'bg-green-50 border-green-300 text-green-700'
                      : 'bg-gray-50 border-gray-200 text-gray-500'
                  }
                  transition-all
                `}
              >
                {isPastStep ? (
                  <CheckIcon className="w-4 h-4" />
                ) : (
                  <Icon className="w-4 h-4" />
                )}
                <span className="text-xs font-medium whitespace-nowrap">
                  {step.display_name || step.name}
                </span>

                {/* Current step indicator */}
                {isCurrentStep && (
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full border-2 border-white" />
                )}
              </div>

              {/* Arrow between steps */}
              {index < sortedSteps.length - 1 && (
                <ArrowRightIcon className="w-4 h-4 mx-2 text-gray-300 flex-shrink-0" />
              )}
            </div>
          );
        })}
      </div>

      {/* Available transitions */}
      {transitions.length > 0 && (
        <div className="mt-4 border-t pt-4">
          <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
            Available Actions
          </h4>
          <div className="flex flex-wrap gap-2">
            {transitions.map((transition) => (
              <button
                key={transition.id}
                onClick={() => onTransitionClick && onTransitionClick(transition)}
                className={`
                  px-3 py-1.5 rounded-lg text-sm font-medium
                  border border-blue-300 bg-blue-50 text-blue-700
                  hover:bg-blue-100 hover:border-blue-400
                  transition-colors
                `}
              >
                {transition.name || 'Next Step'}
                {transition.to_step && (
                  <span className="ml-1 text-xs opacity-70">
                    {transition.to_step.display_name || transition.to_step.name}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
