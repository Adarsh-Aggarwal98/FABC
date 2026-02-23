import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeftIcon,
  PlayIcon,
  StopIcon,
  QuestionMarkCircleIcon,
  CogIcon,
  PlusIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { workflowsAPI } from '../../services/api';
import FlowCanvas from '../../components/workflow/FlowCanvas';
import StepConfigPanel from '../../components/workflow/StepConfigPanel';
import TransitionConfigPanel from '../../components/workflow/TransitionConfigPanel';

const stepTypeOptions = [
  { type: 'START', icon: PlayIcon, label: 'Start', color: 'bg-green-100 border-green-400' },
  { type: 'NORMAL', icon: CogIcon, label: 'Normal', color: 'bg-blue-100 border-blue-400' },
  { type: 'QUERY', icon: QuestionMarkCircleIcon, label: 'Query', color: 'bg-orange-100 border-orange-400' },
  { type: 'END', icon: StopIcon, label: 'End', color: 'bg-red-100 border-red-400' },
];

export default function WorkflowBuilder() {
  const { workflowId } = useParams();
  const navigate = useNavigate();
  const isNew = workflowId === 'new';

  const [workflow, setWorkflow] = useState(null);
  const [loading, setLoading] = useState(!isNew);
  const [saving, setSaving] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  // Panels
  const [selectedStep, setSelectedStep] = useState(null);
  const [selectedTransition, setSelectedTransition] = useState(null);

  // Form state for new workflow
  const [workflowName, setWorkflowName] = useState('');
  const [workflowDescription, setWorkflowDescription] = useState('');

  // Load workflow
  useEffect(() => {
    if (!isNew && workflowId) {
      loadWorkflow();
    } else {
      // Initialize empty workflow
      setWorkflow({
        id: null,
        name: '',
        description: '',
        steps: [],
        transitions: [],
      });
    }
  }, [workflowId, isNew]);

  const loadWorkflow = async () => {
    try {
      setLoading(true);
      const response = await workflowsAPI.get(workflowId);
      setWorkflow(response.data.data.workflow);
      setWorkflowName(response.data.data.workflow.name);
      setWorkflowDescription(response.data.data.workflow.description || '');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load workflow');
    } finally {
      setLoading(false);
    }
  };

  // Validate workflow
  const validateWorkflow = async () => {
    if (!workflow?.id) return;
    try {
      const response = await workflowsAPI.validate(workflow.id);
      setValidationResult(response.data.data);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to validate workflow');
    }
  };

  useEffect(() => {
    if (workflow?.id) {
      validateWorkflow();
    }
  }, [workflow?.steps?.length, workflow?.transitions?.length]);

  // Save workflow
  const handleSave = async () => {
    if (!workflowName.trim()) {
      toast.error('Workflow name is required');
      return;
    }

    try {
      setSaving(true);
      if (isNew) {
        const response = await workflowsAPI.create({
          name: workflowName,
          description: workflowDescription,
        });
        const newWorkflow = response.data.data.workflow;
        toast.success('Workflow created');
        navigate(`/settings/workflows/${newWorkflow.id}`, { replace: true });
      } else {
        await workflowsAPI.update(workflowId, {
          name: workflowName,
          description: workflowDescription,
        });
        toast.success('Workflow saved');
        await loadWorkflow();
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save workflow');
    } finally {
      setSaving(false);
    }
  };

  // Handle step selection (for editing or creating)
  const handleStepSelect = useCallback((step) => {
    setSelectedTransition(null);
    if (step.isNew) {
      // New step from drag & drop
      setSelectedStep({
        ...step,
        id: null,
        name: '',
        display_name: '',
        description: '',
        color: step.step_type === 'START' ? 'green' :
               step.step_type === 'END' ? 'red' :
               step.step_type === 'QUERY' ? 'orange' : 'blue',
      });
    } else {
      setSelectedStep(step);
    }
  }, []);

  // Handle transition selection
  const handleTransitionSelect = useCallback((transition) => {
    setSelectedStep(null);
    setSelectedTransition(transition);
  }, []);

  // Save step
  const handleSaveStep = async (stepData) => {
    try {
      setSaving(true);
      if (selectedStep?.id) {
        // Update existing step
        await workflowsAPI.updateStep(workflow.id, selectedStep.id, stepData);
        toast.success('Step updated');
      } else {
        // Create new step
        await workflowsAPI.addStep(workflow.id, {
          ...stepData,
          position_x: selectedStep?.position_x || 100,
          position_y: selectedStep?.position_y || 100,
        });
        toast.success('Step added');
      }
      setSelectedStep(null);
      await loadWorkflow();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save step');
    } finally {
      setSaving(false);
    }
  };

  // Delete step
  const handleDeleteStep = async () => {
    if (!selectedStep?.id) return;
    if (!confirm('Are you sure you want to delete this step?')) return;

    try {
      setSaving(true);
      await workflowsAPI.deleteStep(workflow.id, selectedStep.id);
      toast.success('Step deleted');
      setSelectedStep(null);
      await loadWorkflow();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete step');
    } finally {
      setSaving(false);
    }
  };

  // Save transition
  const handleSaveTransition = async (transitionData) => {
    try {
      setSaving(true);
      await workflowsAPI.updateTransition(workflow.id, selectedTransition.id, transitionData);
      toast.success('Transition updated');
      setSelectedTransition(null);
      await loadWorkflow();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save transition');
    } finally {
      setSaving(false);
    }
  };

  // Delete transition
  const handleDeleteTransition = async () => {
    if (!selectedTransition?.id) return;
    if (!confirm('Are you sure you want to delete this transition?')) return;

    try {
      setSaving(true);
      await workflowsAPI.deleteTransition(workflow.id, selectedTransition.id);
      toast.success('Transition deleted');
      setSelectedTransition(null);
      await loadWorkflow();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to delete transition');
    } finally {
      setSaving(false);
    }
  };

  // Handle new connection between steps
  const handleConnect = async (connection) => {
    try {
      await workflowsAPI.addTransition(workflow.id, {
        from_step_id: connection.from_step_id,
        to_step_id: connection.to_step_id,
        name: 'New Transition',
      });
      toast.success('Transition added');
      await loadWorkflow();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to add transition');
    }
  };

  // Handle step position changes
  const handleStepsChange = async (updates) => {
    // Update positions in the background
    for (const update of updates) {
      try {
        await workflowsAPI.updateStep(workflow.id, update.id, {
          position_x: update.position_x,
          position_y: update.position_y,
        });
      } catch (error) {
        console.error('Failed to update step position', error);
      }
    }
  };

  // Drag start for step types
  const onDragStart = (event, stepType) => {
    event.dataTransfer.setData('application/reactflow', stepType);
    event.dataTransfer.effectAllowed = 'move';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/settings/workflows')}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeftIcon className="w-5 h-5" />
          </button>
          <div>
            <input
              type="text"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              className="text-lg font-semibold bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1"
              placeholder="Workflow Name"
            />
            <input
              type="text"
              value={workflowDescription}
              onChange={(e) => setWorkflowDescription(e.target.value)}
              className="block text-sm text-gray-500 bg-transparent border-b border-transparent hover:border-gray-300 focus:border-blue-500 focus:outline-none px-1 mt-1 w-64"
              placeholder="Description (optional)"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Validation status */}
          {validationResult && (
            <div className={`flex items-center gap-1 text-sm ${validationResult.is_valid ? 'text-green-600' : 'text-yellow-600'}`}>
              {validationResult.is_valid ? (
                <>
                  <CheckCircleIcon className="w-5 h-5" />
                  <span>Valid</span>
                </>
              ) : (
                <>
                  <ExclamationTriangleIcon className="w-5 h-5" />
                  <span>{validationResult.errors.length} issue(s)</span>
                </>
              )}
            </div>
          )}

          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Step Types Sidebar */}
        <div className="w-48 bg-white border-r border-gray-200 p-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
            Step Types
          </h3>
          <p className="text-xs text-gray-400 mb-3">
            Drag to canvas to add
          </p>
          <div className="space-y-2">
            {stepTypeOptions.map((option) => (
              <div
                key={option.type}
                draggable={!isNew && !!workflow?.id}
                onDragStart={(e) => onDragStart(e, option.type)}
                className={`
                  flex items-center gap-2 p-2 rounded-lg border-2 cursor-move
                  ${option.color}
                  ${(!workflow?.id) ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md'}
                  transition-shadow
                `}
              >
                <option.icon className="w-5 h-5" />
                <span className="text-sm font-medium">{option.label}</span>
              </div>
            ))}
          </div>

          {isNew && (
            <p className="mt-4 text-xs text-gray-500">
              Save the workflow first to add steps
            </p>
          )}

          {/* Validation errors */}
          {validationResult && !validationResult.is_valid && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                Issues
              </h4>
              <ul className="space-y-1">
                {validationResult.errors.map((error, idx) => (
                  <li key={idx} className="text-xs text-red-600">
                    {error}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Canvas */}
        <div className="flex-1 relative">
          {workflow?.id ? (
            <FlowCanvas
              workflow={workflow}
              onStepSelect={handleStepSelect}
              onTransitionSelect={handleTransitionSelect}
              onStepsChange={handleStepsChange}
              onConnect={handleConnect}
            />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500">
              <div className="text-center">
                <CogIcon className="w-12 h-12 mx-auto text-gray-300 mb-4" />
                <p className="text-lg font-medium">Enter a workflow name</p>
                <p className="text-sm">and click Save to start building</p>
              </div>
            </div>
          )}
        </div>

        {/* Config Panels */}
        {selectedStep && (
          <StepConfigPanel
            step={selectedStep}
            onSave={handleSaveStep}
            onClose={() => setSelectedStep(null)}
            onDelete={selectedStep.id ? handleDeleteStep : null}
          />
        )}

        {selectedTransition && (
          <TransitionConfigPanel
            transition={selectedTransition}
            onSave={handleSaveTransition}
            onClose={() => setSelectedTransition(null)}
            onDelete={handleDeleteTransition}
          />
        )}
      </div>
    </div>
  );
}
