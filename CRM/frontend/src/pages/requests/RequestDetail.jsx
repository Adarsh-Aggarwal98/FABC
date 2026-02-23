import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  ArrowLeftIcon,
  PaperAirplaneIcon,
  CurrencyDollarIcon,
  DocumentPlusIcon,
  PencilSquareIcon,
  ClockIcon,
  EyeIcon,
  UserGroupIcon,
  ChatBubbleLeftRightIcon,
  LockClosedIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  PlusIcon,
  ClipboardDocumentCheckIcon,
  CalendarIcon,
  TrashIcon,
  CloudArrowUpIcon,
  PaperClipIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  UserIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { TextArea, Select } from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import Badge from '../../components/common/Badge';
import DocumentUpload from '../../components/features/documents/DocumentUpload';
import DocumentList from '../../components/features/documents/DocumentList';
import { ClientEntitySelector } from '../../components/features/client-entities';
import { requestsAPI, userAPI, documentsAPI, formsAPI, workflowsAPI, clientEntitiesAPI, tasksAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import useCompanyStore from '../../store/companyStore';

export default function RequestDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { fetchCompany, formatPrice, getTaxLabel, getTaxRate, calculateTax, calculateTotalWithTax, getCurrencySettings } = useCompanyStore();
  const taxLabel = getTaxLabel();
  const taxRate = getTaxRate();
  const currencySettings = getCurrencySettings();
  const [request, setRequest] = useState(null);
  const [queries, setQueries] = useState([]);
  const [formResponses, setFormResponses] = useState([]);
  const [formQuestions, setFormQuestions] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [newMessage, setNewMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  // Message tabs
  const [activeMessageTab, setActiveMessageTab] = useState('client'); // 'client' or 'internal'
  const [isInternalMessage, setIsInternalMessage] = useState(false);

  // Workflow
  const [workflow, setWorkflow] = useState(null);
  const [availableTransitions, setAvailableTransitions] = useState([]);
  const [isExecutingTransition, setIsExecutingTransition] = useState(false);

  // State history
  const [stateHistory, setStateHistory] = useState([]);
  const [isHistoryModalOpen, setIsHistoryModalOpen] = useState(false);

  // Assignment history
  const [assignmentHistory, setAssignmentHistory] = useState([]);

  // Modals
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [isReassignModalOpen, setIsReassignModalOpen] = useState(false);
  const [isInvoiceModalOpen, setIsInvoiceModalOpen] = useState(false);
  const [isNoteModalOpen, setIsNoteModalOpen] = useState(false);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isAuditLogModalOpen, setIsAuditLogModalOpen] = useState(false);

  // Assign form
  const [accountants, setAccountants] = useState([]);
  const [selectedAccountant, setSelectedAccountant] = useState('');
  const [deadlineDate, setDeadlineDate] = useState('');
  const [priority, setPriority] = useState('normal');
  const [reassignReason, setReassignReason] = useState('');

  // Invoice form
  const [invoiceData, setInvoiceData] = useState({
    invoice_amount: '',
    payment_link: '',
  });

  // Cost tracking
  const [isCostModalOpen, setIsCostModalOpen] = useState(false);
  const [costData, setCostData] = useState({
    actual_cost: '',
    cost_notes: '',
    labor_hours: '',
    labor_rate: '',
  });

  // Note form
  const [newNote, setNewNote] = useState('');

  // Edit form
  const [editData, setEditData] = useState({});
  const [isEditing, setIsEditing] = useState(false);
  const [selectedEntityForEdit, setSelectedEntityForEdit] = useState(null);

  // Audit log
  const [auditLogs, setAuditLogs] = useState([]);

  // Form response editing
  const [isFormEditModalOpen, setIsFormEditModalOpen] = useState(false);
  const [formEditData, setFormEditData] = useState([]);
  const [formEditFiles, setFormEditFiles] = useState({});
  const [isFormEditing, setIsFormEditing] = useState(false);
  const [formEditRepeatables, setFormEditRepeatables] = useState({});
  const [formEditCollapsed, setFormEditCollapsed] = useState({});

  // Tasks
  const [tasks, setTasks] = useState([]);
  const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [isTaskSubmitting, setIsTaskSubmitting] = useState(false);
  const [taskFormData, setTaskFormData] = useState({
    title: '',
    description: '',
    assigned_to_id: '',
    due_date: '',
    priority: 'normal',
    estimated_minutes: '',
  });

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'senior_accountant';
  const isAccountant = user?.role === 'accountant' || user?.role === 'senior_accountant';
  const isStaff = isAdmin || isAccountant;
  const isOwner = request?.user?.id === user?.id;
  const isAssignedAccountant = request?.assigned_accountant?.id === user?.id;

  // Get status color for the status card
  const getStatusColor = (status) => {
    const colors = {
      pending: '#F59E0B',
      collecting_docs: '#8B5CF6',
      in_progress: '#3B82F6',
      review: '#F97316',
      awaiting_client: '#6B7280',
      lodgement: '#14B8A6',
      invoicing: '#EC4899',
      completed: '#10B981',
      on_hold: '#9CA3AF',
      cancelled: '#EF4444',
      // Legacy statuses
      assigned: '#F59E0B',
      processing: '#3B82F6',
      query_raised: '#8B5CF6',
    };
    return colors[status] || '#6B7280';
  };

  useEffect(() => {
    fetchRequest();
    fetchQueries();
    fetchDocuments();
    fetchCompany();
    fetchTasks();
  }, [id]);

  useEffect(() => {
    if (request) {
      fetchFormResponses();
      if (request.service?.form_id) {
        fetchFormQuestions(request.service.form_id);
      }
      // Fetch workflow details
      if (request.service?.workflow_id || request.current_step_id) {
        fetchWorkflowDetails();
      }
      // Fetch state history
      if (isStaff) {
        fetchStateHistory();
        fetchAssignmentHistory();
      }
    }
  }, [request?.id]);

  useEffect(() => {
    if (isStaff) {
      fetchAccountants();
    }
  }, [isStaff]);

  const fetchRequest = async () => {
    setIsLoading(true);
    try {
      const response = await requestsAPI.get(id);
      setRequest(response.data.data.request);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch request');
      navigate('/requests');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchWorkflowDetails = async () => {
    try {
      const response = await workflowsAPI.getRequestTransitions(id);
      setWorkflow(response.data.data.workflow);
      setAvailableTransitions(response.data.data.available_transitions || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch workflow details');
    }
  };

  const fetchStateHistory = async () => {
    try {
      const response = await requestsAPI.getStateHistory(id);
      setStateHistory(response.data.data.history || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch state history');
    }
  };

  const fetchAssignmentHistory = async () => {
    try {
      const response = await requestsAPI.getAssignmentHistory(id);
      setAssignmentHistory(response.data.data.history || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch assignment history');
    }
  };

  const fetchFormResponses = async () => {
    try {
      const response = await requestsAPI.getFormResponses(id);
      const responses = response.data.data.form_responses || [];
      setFormResponses(responses);
      // Always fetch form questions (needed for dropdown options in edit modal)
      if (request?.service?.form_id) {
        fetchFormQuestions(request.service.form_id);
      }
    } catch (error) {
      // Form responses may not exist yet - this is expected for new requests
    }
  };

  const fetchFormQuestions = async (formId) => {
    try {
      const response = await formsAPI.get(formId);
      setFormQuestions(response.data.data.form?.questions || []);
    } catch (error) {
      // Form questions may not be available - non-critical
    }
  };

  const fetchQueries = async () => {
    try {
      const response = await requestsAPI.getQueries(id);
      setQueries(response.data.data.queries || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch queries');
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await documentsAPI.list({ service_request_id: id });
      setDocuments(response.data.documents || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch documents');
    }
  };

  const handleDocumentUploadComplete = () => {
    setIsUploadModalOpen(false);
    fetchDocuments();
  };

  const fetchAuditLog = async () => {
    try {
      const response = await requestsAPI.getAuditLog(id);
      setAuditLogs(response.data.data.audit_logs || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch audit log');
    }
  };

  const fetchAccountants = async () => {
    try {
      const response = await userAPI.getAccountants();
      setAccountants(response.data.data.accountants || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch accountants');
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await tasksAPI.list({ service_request_id: id });
      setTasks(response.data.data || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch tasks');
    }
  };

  const handleTaskStatusChange = async (taskId, newStatus) => {
    try {
      await tasksAPI.updateStatus(taskId, newStatus);
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? { ...t, status: newStatus } : t))
      );
      toast.success('Task updated');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update task');
      fetchTasks();
    }
  };

  const openTaskModal = (task = null) => {
    if (task) {
      setEditingTask(task);
      setTaskFormData({
        title: task.title || '',
        description: task.description || '',
        assigned_to_id: task.assigned_to?.id || '',
        due_date: task.due_date || '',
        priority: task.priority || 'normal',
        estimated_minutes: task.estimated_minutes ? String(Math.round(task.estimated_minutes / 60)) : '',
      });
    } else {
      setEditingTask(null);
      setTaskFormData({
        title: '',
        description: '',
        assigned_to_id: user?.id || '',
        due_date: '',
        priority: 'normal',
        estimated_minutes: '',
      });
    }
    setIsTaskModalOpen(true);
  };

  const handleTaskSubmit = async (e) => {
    e.preventDefault();
    setIsTaskSubmitting(true);
    try {
      const data = {
        ...taskFormData,
        service_request_id: id,
        estimated_minutes: taskFormData.estimated_minutes ? parseInt(taskFormData.estimated_minutes) * 60 : null,
        assigned_to_id: taskFormData.assigned_to_id || null,
      };

      if (editingTask) {
        await tasksAPI.update(editingTask.id, data);
        toast.success('Task updated');
      } else {
        await tasksAPI.create(data);
        toast.success('Task created');
      }

      setIsTaskModalOpen(false);
      fetchTasks();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save task');
    } finally {
      setIsTaskSubmitting(false);
    }
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Delete this task?')) return;
    try {
      await tasksAPI.delete(taskId);
      toast.success('Task deleted');
      fetchTasks();
    } catch (error) {
      toast.error('Failed to delete task');
    }
  };

  // Workflow transition handler
  const handleTransition = async (transition) => {
    if (!transition?.id) return;

    const confirmMessage = transition.name
      ? `Execute "${transition.name}"?`
      : 'Proceed with this transition?';

    if (!confirm(confirmMessage)) return;

    setIsExecutingTransition(true);
    try {
      await workflowsAPI.executeTransition(id, transition.id);
      toast.success(transition.name ? `${transition.name} completed` : 'Status updated');
      fetchRequest();
      fetchWorkflowDetails();
      fetchStateHistory();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to execute transition');
    } finally {
      setIsExecutingTransition(false);
    }
  };

  const handleAssign = async () => {
    try {
      await requestsAPI.assign(id, selectedAccountant, deadlineDate || null, priority);
      toast.success('Request assigned successfully');
      setIsAssignModalOpen(false);
      setDeadlineDate('');
      setPriority('normal');
      fetchRequest();
      fetchAssignmentHistory();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to assign request');
    }
  };

  const handleReassign = async () => {
    try {
      await requestsAPI.reassign(id, selectedAccountant, reassignReason);
      toast.success('Request reassigned successfully');
      setIsReassignModalOpen(false);
      setSelectedAccountant('');
      setReassignReason('');
      fetchRequest();
      fetchAssignmentHistory();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to reassign request');
    }
  };

  const handleStatusChange = async (status) => {
    try {
      await requestsAPI.updateStatus(id, status);
      toast.success('Status updated');
      fetchRequest();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update status');
    }
  };

  const handleInvoiceUpdate = async (raised, paid) => {
    try {
      await requestsAPI.updateInvoice(id, {
        invoice_raised: raised,
        invoice_paid: paid,
        invoice_amount: invoiceData.invoice_amount || undefined,
        payment_link: invoiceData.payment_link || undefined,
      });
      toast.success('Invoice updated');
      setIsInvoiceModalOpen(false);
      fetchRequest();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update invoice');
    }
  };

  const handleCostUpdate = async () => {
    try {
      await requestsAPI.updateCost(id, {
        actual_cost: costData.actual_cost || null,
        cost_notes: costData.cost_notes || null,
        labor_hours: costData.labor_hours || null,
        labor_rate: costData.labor_rate || null,
      });
      toast.success('Cost details updated');
      setIsCostModalOpen(false);
      fetchRequest();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update cost details');
    }
  };

  const openCostModal = () => {
    setCostData({
      actual_cost: request?.actual_cost || '',
      cost_notes: request?.cost_notes || '',
      labor_hours: request?.labor_hours || '',
      labor_rate: request?.labor_rate || '',
    });
    setIsCostModalOpen(true);
  };

  const handlePreviewInvoice = async () => {
    try {
      const response = await requestsAPI.previewInvoicePdf(id);
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to preview invoice');
    }
  };

  const handleAddNote = async () => {
    try {
      await requestsAPI.addNote(id, newNote);
      toast.success('Note added');
      setIsNoteModalOpen(false);
      setNewNote('');
      fetchRequest();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to add note');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    setIsSending(true);
    try {
      await requestsAPI.addQuery(id, newMessage, isInternalMessage);
      toast.success(isInternalMessage ? 'Internal note added' : 'Message sent');
      setNewMessage('');
      fetchQueries();
      fetchRequest();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to send message');
    } finally {
      setIsSending(false);
    }
  };

  const openEditModal = () => {
    setEditData({
      status: request?.status || '',
      xero_reference_job_id: request?.xero_reference_job_id || '',
      internal_reference: request?.internal_reference || '',
      internal_notes: request?.internal_notes || '',
      invoice_amount: request?.invoice_amount || '',
      invoice_raised: request?.invoice_raised || false,
      invoice_paid: request?.invoice_paid || false,
      payment_link: request?.payment_link || '',
      client_entity_id: request?.client_entity_id || null,
    });
    setSelectedEntityForEdit(request?.client_entity || null);
    setIsEditModalOpen(true);
  };

  const handleEditSubmit = async () => {
    setIsEditing(true);
    try {
      await requestsAPI.update(id, editData);
      toast.success('Request updated successfully');
      setIsEditModalOpen(false);
      fetchRequest();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update request');
    } finally {
      setIsEditing(false);
    }
  };

  const openAuditLogModal = async () => {
    await fetchAuditLog();
    setIsAuditLogModalOpen(true);
  };

  const openFormEditModal = async () => {
    // Fetch fresh questions to ensure we have options for dropdowns
    let questions = formQuestions;
    if (request?.service?.form_id) {
      try {
        const res = await formsAPI.get(request.service.form_id);
        questions = res.data.data?.form?.questions || res.data.form?.questions || [];
        setFormQuestions(questions);
      } catch (e) {
        // Fall back to existing formQuestions
      }
    }

    // Build question metadata lookup
    const questionMetaMap = {};
    questions.forEach(q => {
      questionMetaMap[q.id] = q;
    });

    // Detect repeatable sections from questions
    const repeatables = {};
    questions.forEach(q => {
      if (q.is_section_repeatable && q.section_group) {
        if (!repeatables[q.section_group]) {
          repeatables[q.section_group] = {
            min: q.min_section_repeats || 1,
            max: q.max_section_repeats || 10,
            sectionTitle: q.section_title,
            instances: [{ id: 1 }],
          };
        }
      }
    });

    let editData = [];
    if (formResponses.length > 0 && formResponses[0].responses) {
      const questionOptionsMap = {};
      questions.forEach(q => {
        if (q.options) questionOptionsMap[q.id] = q.options;
      });

      // Check if existing responses have repeatable instance keys (e.g. "123_2")
      // Parse existing instances from saved response data
      const existingInstances = {};
      formResponses[0].responses.forEach(r => {
        const qMeta = questionMetaMap[r.question_id];
        if (qMeta?.is_section_repeatable && qMeta?.section_group) {
          const group = qMeta.section_group;
          if (!existingInstances[group]) existingInstances[group] = new Set();
          existingInstances[group].add(1); // base instance
        }
      });

      // Also check formData-style keys with instance suffixes in the raw responses dict
      if (formResponses[0].response_data) {
        const rawData = formResponses[0].response_data;
        Object.keys(rawData).forEach(key => {
          const parts = key.split('_');
          if (parts.length >= 2) {
            const instanceId = parseInt(parts[parts.length - 1]);
            const questionId = parseInt(parts.slice(0, -1).join('_'));
            if (!isNaN(instanceId) && !isNaN(questionId)) {
              const qMeta = questionMetaMap[questionId];
              if (qMeta?.is_section_repeatable && qMeta?.section_group) {
                const group = qMeta.section_group;
                if (!existingInstances[group]) existingInstances[group] = new Set();
                existingInstances[group].add(instanceId);
              }
            }
          }
        });
      }

      // Update repeatable instances based on saved data
      Object.entries(existingInstances).forEach(([group, instanceIds]) => {
        if (repeatables[group]) {
          const ids = Array.from(instanceIds).sort((a, b) => a - b);
          if (ids.length > 0) {
            repeatables[group].instances = ids.map(id => ({ id }));
          }
        }
      });

      editData = formResponses[0].responses.map(r => ({
        question_id: r.question_id,
        question_text: r.question_text || r.question,
        question_type: r.question_type,
        section_number: r.section_number,
        section_title: r.section_title,
        answer: r.answer || '',
        attachments: r.attachments || [],
        options: r.options || questionOptionsMap[r.question_id] || [],
        is_section_repeatable: questionMetaMap[r.question_id]?.is_section_repeatable || false,
        section_group: questionMetaMap[r.question_id]?.section_group || null,
        min_section_repeats: questionMetaMap[r.question_id]?.min_section_repeats || 1,
        max_section_repeats: questionMetaMap[r.question_id]?.max_section_repeats || 10,
      }));
    } else if (questions.length > 0) {
      editData = questions.map(q => ({
        question_id: q.id,
        question_text: q.question_text,
        question_type: q.question_type,
        section_number: q.section_number,
        section_title: q.section_title,
        answer: '',
        attachments: [],
        options: q.options || [],
        is_section_repeatable: q.is_section_repeatable || false,
        section_group: q.section_group || null,
        min_section_repeats: q.min_section_repeats || 1,
        max_section_repeats: q.max_section_repeats || 10,
      }));
    }

    setFormEditData(editData);
    setFormEditRepeatables(repeatables);
    setFormEditCollapsed({});
    setFormEditFiles({});
    setIsFormEditModalOpen(true);
  };

  // State for repeatable instance answers: { "questionId_instanceId": value }
  const [formEditRepeatableAnswers, setFormEditRepeatableAnswers] = useState({});

  const handleFormEditSubmit = async () => {
    setIsFormEditing(true);
    try {
      // Build responses including repeatable instance data
      const responses = {};
      formEditData.forEach(item => {
        if (!item.is_section_repeatable) {
          responses[item.question_id] = item.answer;
        }
      });
      // Add repeatable answers with instance keys
      Object.entries(formEditRepeatableAnswers).forEach(([key, value]) => {
        responses[key] = value;
      });

      if (formResponses.length > 0) {
        // For update, merge repeatable answers into the edit data
        const updatedEditData = [...formEditData];
        await formsAPI.updateResponse(formResponses[0].id, updatedEditData, responses);
      } else {
        await formsAPI.submit(
          request.service.form_id,
          responses,
          id,
          { partial: true }
        );
      }
      // Upload any files attached during form editing
      for (const [questionId, file] of Object.entries(formEditFiles)) {
        try {
          await documentsAPI.upload(file, id, 'form_attachment');
        } catch (err) {
          console.error('Failed to upload form file:', err);
        }
      }
      setFormEditFiles({});
      setFormEditRepeatableAnswers({});
      toast.success('Form responses updated successfully');
      setIsFormEditModalOpen(false);
      fetchFormResponses();
      fetchDocuments();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to update form responses');
    } finally {
      setIsFormEditing(false);
    }
  };

  const updateFormEditAnswer = (questionId, value) => {
    setFormEditData(prev =>
      prev.map(item =>
        item.question_id === questionId ? { ...item, answer: value } : item
      )
    );
  };

  const updateRepeatableAnswer = (questionId, instanceId, value) => {
    const key = `${questionId}_${instanceId}`;
    setFormEditRepeatableAnswers(prev => ({ ...prev, [key]: value }));
  };

  const getRepeatableAnswer = (questionId, instanceId) => {
    const key = `${questionId}_${instanceId}`;
    return formEditRepeatableAnswers[key] || '';
  };

  const addRepeatableEditInstance = (groupName) => {
    setFormEditRepeatables(prev => {
      const group = prev[groupName];
      if (!group || group.instances.length >= group.max) return prev;
      const newId = Math.max(...group.instances.map(i => i.id)) + 1;
      return {
        ...prev,
        [groupName]: {
          ...group,
          instances: [...group.instances, { id: newId }],
        },
      };
    });
  };

  const removeRepeatableEditInstance = (groupName, instanceId) => {
    setFormEditRepeatables(prev => {
      const group = prev[groupName];
      if (!group || group.instances.length <= group.min) return prev;
      return {
        ...prev,
        [groupName]: {
          ...group,
          instances: group.instances.filter(i => i.id !== instanceId),
        },
      };
    });
    // Clean up answers for removed instance
    setFormEditRepeatableAnswers(prev => {
      const cleaned = { ...prev };
      Object.keys(cleaned).forEach(key => {
        if (key.endsWith(`_${instanceId}`)) delete cleaned[key];
      });
      return cleaned;
    });
    setFormEditCollapsed(prev => {
      const cleaned = { ...prev };
      delete cleaned[`${groupName}_${instanceId}`];
      return cleaned;
    });
  };

  // Filter messages by type
  const clientMessages = queries.filter(q => !q.is_internal);
  const internalMessages = queries.filter(q => q.is_internal);

  // Get current step info from workflow
  const currentStep = workflow?.steps?.find(s => s.id === request?.current_step_id);

  // Simple workflow progress component
  const WorkflowProgress = () => {
    if (!workflow?.steps || workflow.steps.length === 0) {
      return null;
    }

    // Sort steps by order
    const sortedSteps = [...workflow.steps].sort((a, b) => a.order - b.order);
    const currentIndex = sortedSteps.findIndex(s => s.id === request?.current_step_id);

    return (
      <Card>
        <CardHeader
          title="Workflow Progress"
          subtitle={currentStep?.display_name || currentStep?.name || request?.status}
        />

        {/* Simple Progress Bar */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-gray-500">
              Step {currentIndex + 1} of {sortedSteps.length}
            </span>
            <Badge status={request?.status}>
              {currentStep?.display_name || request?.status}
            </Badge>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${((currentIndex + 1) / sortedSteps.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Step Pills */}
        <div className="flex flex-wrap gap-2 mb-4">
          {sortedSteps.map((step, idx) => {
            const isPast = idx < currentIndex;
            const isCurrent = idx === currentIndex;
            const isEnd = step.step_type === 'END';

            return (
              <div
                key={step.id}
                className={`flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${
                  isCurrent
                    ? 'bg-primary-100 text-primary-800 ring-2 ring-primary-500'
                    : isPast
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-500'
                }`}
              >
                {isPast && <CheckCircleIcon className="h-3 w-3" />}
                {step.display_name || step.name}
              </div>
            );
          })}
        </div>

        {/* Available Actions */}
        {availableTransitions.length > 0 && request?.status !== 'completed' && (
          <div className="border-t pt-4">
            <p className="text-sm text-gray-500 mb-2">Available Actions:</p>
            <div className="flex flex-wrap gap-2">
              {availableTransitions.map((transition) => (
                <Button
                  key={transition.id}
                  size="sm"
                  variant={transition.to_step?.step_type === 'END' ? 'success' : 'secondary'}
                  onClick={() => handleTransition(transition)}
                  loading={isExecutingTransition}
                >
                  {transition.name || `Go to ${transition.to_step?.display_name}`}
                </Button>
              ))}
            </div>
          </div>
        )}
      </Card>
    );
  };

  // Message Section Component with Tabs
  const MessageSection = () => (
    <Card>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Communication</h3>
        {isStaff && (
          <div className="flex rounded-lg bg-gray-100 p-1">
            <button
              onClick={() => {
                setActiveMessageTab('client');
                setIsInternalMessage(false);
              }}
              className={`flex items-center gap-1 px-3 py-1 text-sm rounded-md transition ${
                activeMessageTab === 'client'
                  ? 'bg-white shadow text-primary-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <ChatBubbleLeftRightIcon className="h-4 w-4" />
              Client ({clientMessages.length})
            </button>
            <button
              onClick={() => {
                setActiveMessageTab('internal');
                setIsInternalMessage(true);
              }}
              className={`flex items-center gap-1 px-3 py-1 text-sm rounded-md transition ${
                activeMessageTab === 'internal'
                  ? 'bg-white shadow text-orange-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <LockClosedIcon className="h-4 w-4" />
              Internal ({internalMessages.length})
            </button>
          </div>
        )}
      </div>

      {/* Messages List */}
      <div className="space-y-3 max-h-80 overflow-y-auto mb-3">
        {(activeMessageTab === 'client' ? clientMessages : internalMessages).length === 0 ? (
          <p className="text-gray-500 text-center py-6 text-sm">
            {activeMessageTab === 'client'
              ? 'No client messages yet'
              : 'No internal notes yet'}
          </p>
        ) : (
          (activeMessageTab === 'client' ? clientMessages : internalMessages).map((query) => (
            <div
              key={query.id}
              className={`p-3 rounded-lg text-sm ${
                query.is_internal
                  ? 'bg-orange-50 border border-orange-100'
                  : query.sender.role === 'user'
                  ? 'bg-gray-100'
                  : 'bg-primary-50'
              }`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium text-xs flex items-center gap-1">
                  {query.sender.full_name}
                  {query.is_internal && (
                    <LockClosedIcon className="h-3 w-3 text-orange-500" />
                  )}
                </span>
                <span className="text-xs text-gray-400">
                  {new Date(query.created_at).toLocaleString()}
                </span>
              </div>
              <p className="text-gray-700">{query.message}</p>
            </div>
          ))
        )}
      </div>

      {/* Message Input */}
      {request?.status !== 'completed' && (
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <Input
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder={isInternalMessage ? 'Add internal note...' : 'Type message to client...'}
            className="flex-1 text-sm"
          />
          <Button
            type="submit"
            loading={isSending}
            icon={PaperAirplaneIcon}
            size="sm"
            variant={isInternalMessage ? 'warning' : 'primary'}
          />
        </form>
      )}
      {isStaff && activeMessageTab === 'internal' && (
        <p className="text-xs text-orange-600 mt-2 flex items-center gap-1">
          <LockClosedIcon className="h-3 w-3" />
          Internal notes are only visible to staff
        </p>
      )}
    </Card>
  );

  // Task Statuses for mini Kanban
  const TASK_STATUSES = [
    { key: 'pending', label: 'Pending', color: '#F59E0B' },
    { key: 'in_progress', label: 'In Progress', color: '#3B82F6' },
    { key: 'completed', label: 'Completed', color: '#10B981' },
  ];

  // Tasks Section Component
  const TasksSection = () => {
    const groupedTasks = TASK_STATUSES.reduce((acc, status) => {
      acc[status.key] = tasks.filter((t) => t.status === status.key);
      return acc;
    }, {});

    const TaskCard = ({ task }) => {
      const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'completed';
      const priorityColors = {
        urgent: 'border-l-red-500 bg-red-50',
        high: 'border-l-orange-500 bg-orange-50',
        normal: 'border-l-blue-500',
        low: 'border-l-gray-400',
      };

      return (
        <div
          draggable
          onDragStart={(e) => e.dataTransfer.setData('taskId', task.id)}
          className={`p-2 bg-white rounded border-l-4 shadow-sm cursor-grab hover:shadow-md transition ${priorityColors[task.priority] || ''} ${task.status === 'done' ? 'opacity-60' : ''}`}
        >
          <div className="flex items-start justify-between gap-2">
            <span className={`text-sm font-medium ${task.status === 'done' ? 'line-through text-gray-500' : 'text-gray-900'}`}>
              {task.title}
            </span>
            {isOverdue && <span className="text-red-500 text-xs">!</span>}
          </div>
          {task.description && (
            <p className="text-xs text-gray-500 mt-1 line-clamp-1">{task.description}</p>
          )}
          <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
            <div className="flex items-center gap-2">
              {task.assigned_to && (
                <span className="bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">
                  {task.assigned_to.first_name?.charAt(0) || '?'}
                </span>
              )}
              {task.due_date && (
                <span className={isOverdue ? 'text-red-500' : ''}>
                  {new Date(task.due_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </span>
              )}
            </div>
            <div className="flex gap-1">
              <button onClick={() => openTaskModal(task)} className="hover:text-primary-600">
                <PencilSquareIcon className="h-3.5 w-3.5" />
              </button>
              {isAdmin && (
                <button onClick={() => handleDeleteTask(task.id)} className="hover:text-red-600">
                  <TrashIcon className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          </div>
        </div>
      );
    };

    const TaskColumn = ({ status, tasks: columnTasks }) => (
      <div
        className="flex-1 min-w-[140px] bg-gray-50 rounded-lg p-2"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          const taskId = e.dataTransfer.getData('taskId');
          if (taskId) handleTaskStatusChange(taskId, status.key);
        }}
      >
        <div className="flex items-center gap-2 mb-2 pb-2 border-b" style={{ borderBottomColor: status.color }}>
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: status.color }} />
          <span className="text-xs font-medium text-gray-700">{status.label}</span>
          <span className="text-xs text-gray-400">({columnTasks.length})</span>
        </div>
        <div className="space-y-2 min-h-[60px]">
          {columnTasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      </div>
    );

    return (
      <Card>
        <CardHeader
          title="Tasks"
          subtitle={`${tasks.length} task${tasks.length !== 1 ? 's' : ''} linked to this request`}
          action={
            isStaff && request?.status !== 'completed' && (
              <Button size="sm" icon={PlusIcon} onClick={() => openTaskModal()}>
                Add Task
              </Button>
            )
          }
        />
        {tasks.length === 0 ? (
          <div className="text-center py-6 text-gray-400">
            <ClipboardDocumentCheckIcon className="h-8 w-8 mx-auto mb-2" />
            <p className="text-sm">No tasks yet</p>
            {isStaff && request?.status !== 'completed' && (
              <Button size="sm" variant="secondary" className="mt-2" onClick={() => openTaskModal()}>
                Create First Task
              </Button>
            )}
          </div>
        ) : (
          <div className="flex gap-2 overflow-x-auto pb-2">
            {TASK_STATUSES.map((status) => (
              <TaskColumn key={status.key} status={status} tasks={groupedTasks[status.key] || []} />
            ))}
          </div>
        )}
      </Card>
    );
  };

  // State History Timeline
  const StateHistoryTimeline = () => (
    <div className="space-y-3">
      {stateHistory.length === 0 ? (
        <p className="text-gray-500 text-center py-4 text-sm">No state changes recorded</p>
      ) : (
        stateHistory.map((entry, idx) => (
          <div key={entry.id} className="flex gap-3">
            <div className="flex flex-col items-center">
              <div className={`w-3 h-3 rounded-full ${idx === stateHistory.length - 1 ? 'bg-primary-500' : 'bg-gray-300'}`} />
              {idx < stateHistory.length - 1 && <div className="w-0.5 h-full bg-gray-200" />}
            </div>
            <div className="flex-1 pb-4">
              <div className="flex items-center justify-between">
                <span className="font-medium text-sm">
                  {entry.from_state ? (
                    <>
                      <span className="text-gray-500">{entry.from_state}</span>
                      <span className="mx-2">→</span>
                      <span className="text-primary-600">{entry.to_state}</span>
                    </>
                  ) : (
                    <span className="text-primary-600">{entry.to_state}</span>
                  )}
                </span>
                {entry.duration_formatted && (
                  <span className="text-xs text-gray-400">{entry.duration_formatted}</span>
                )}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {new Date(entry.changed_at).toLocaleString()}
                {entry.changed_by && ` by ${entry.changed_by.full_name}`}
              </div>
              {entry.notes && (
                <p className="text-xs text-gray-600 mt-1">{entry.notes}</p>
              )}
            </div>
          </div>
        ))
      )}
    </div>
  );

  if (isLoading) {
    return (
      <DashboardLayout title="Request Details">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="Request Details">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            icon={ArrowLeftIcon}
            onClick={() => navigate('/requests')}
          >
            Back to Requests
          </Button>

          <div className="flex gap-2">
            {isStaff && (
              <>
                <Button
                  variant="secondary"
                  icon={PencilSquareIcon}
                  onClick={openEditModal}
                >
                  Edit
                </Button>
                <Button
                  variant="ghost"
                  icon={ClockIcon}
                  onClick={() => setIsHistoryModalOpen(true)}
                >
                  History
                </Button>
              </>
            )}

            {isStaff && request?.status !== 'completed' && (
              <>
                {/* Assign button for admin/accountant when no one is assigned */}
                {isStaff && !request?.assigned_accountant && (
                  <Button onClick={() => setIsAssignModalOpen(true)}>
                    Assign
                  </Button>
                )}
                {/* Reassign button - any accountant or admin in the company can reassign */}
                {request?.assigned_accountant && isStaff && (
                  <Button
                    variant="secondary"
                    icon={UserGroupIcon}
                    onClick={() => setIsReassignModalOpen(true)}
                  >
                    Reassign
                  </Button>
                )}
                <Button
                  variant="secondary"
                  onClick={() => setIsInvoiceModalOpen(true)}
                >
                  Invoice
                </Button>
              </>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Current Status Card */}
            <Card className="bg-gradient-to-r from-gray-50 to-white border-l-4" style={{ borderLeftColor: getStatusColor(request?.status) }}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Current Status</p>
                    <div className="flex items-center gap-2">
                      <Badge status={request?.status} size="lg" />
                      {currentStep && (
                        <span className="text-sm text-gray-500">
                          ({currentStep.display_name || currentStep.name})
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">Request #{request?.request_number}</p>
                  {request?.deadline_date && (
                    <p className={`text-sm font-medium ${new Date(request.deadline_date) < new Date() ? 'text-red-600' : 'text-gray-700'}`}>
                      Due: {new Date(request.deadline_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
              </div>
            </Card>

            {/* Request Info */}
            <Card>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-xl font-semibold text-gray-900">
                      {request?.service?.name}
                    </h2>
                    <span className="text-sm text-gray-400">#{request?.request_number}</span>
                  </div>
                  <p className="text-gray-500">{request?.service?.description}</p>
                </div>
                <Badge status={request?.status} />
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-500">Created</p>
                  <p className="font-medium">
                    {new Date(request?.created_at).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <p className="text-gray-500">Last Updated</p>
                  <p className="font-medium">
                    {new Date(request?.updated_at).toLocaleDateString()}
                  </p>
                </div>
                {isStaff && (
                  <>
                    <div>
                      <p className="text-gray-500">Client</p>
                      <Link
                        to={`/users/${request?.user?.id}`}
                        className="hover:text-primary-600"
                      >
                        <p className="font-medium text-primary-600 hover:text-primary-700">
                          {request?.user?.full_name}
                        </p>
                      </Link>
                      <p className="text-xs text-gray-400">{request?.user?.email}</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Assigned To</p>
                      <p className="font-medium">
                        {request?.assigned_accountant?.full_name || 'Unassigned'}
                      </p>
                    </div>
                    {request?.client_entity && (
                      <div className="col-span-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <p className="text-gray-500 text-xs mb-1">Client Entity</p>
                        <Link
                          to={`/client-entities/${request.client_entity.id}`}
                          className="hover:text-primary-600"
                        >
                          <p className="font-medium text-primary-600 hover:text-primary-700">
                            {request.client_entity.name}
                          </p>
                        </Link>
                        <div className="flex items-center gap-2 mt-1">
                          <span className="text-xs px-1.5 py-0.5 rounded bg-gray-200 text-gray-600">
                            {request.client_entity.entity_type}
                          </span>
                          {request.client_entity.abn && (
                            <span className="text-xs text-gray-500">ABN: {request.client_entity.abn}</span>
                          )}
                        </div>
                      </div>
                    )}
                    <div>
                      <p className="text-gray-500">Xero Job ID</p>
                      <p className="font-medium font-mono">
                        {request?.xero_reference_job_id || <span className="text-gray-400">Not set</span>}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Internal Reference</p>
                      <p className="font-medium font-mono">
                        {request?.internal_reference || <span className="text-gray-400">Not set</span>}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Deadline</p>
                      <p className={`font-medium ${request?.deadline_date && new Date(request.deadline_date) < new Date() ? 'text-red-600' : ''}`}>
                        {request?.deadline_date ? new Date(request.deadline_date).toLocaleDateString() : <span className="text-gray-400">Not set</span>}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500">Priority</p>
                      <Badge status={request?.priority === 'urgent' ? 'query_raised' : request?.priority === 'high' ? 'in_progress' : 'pending'}>
                        {request?.priority ? request.priority.charAt(0).toUpperCase() + request.priority.slice(1) : 'Normal'}
                      </Badge>
                    </div>
                  </>
                )}
              </div>
            </Card>

            {/* Workflow Progress */}
            <WorkflowProgress />

            {/* Tasks Section */}
            {isStaff && <TasksSection />}

            {/* Invoice Info */}
            {request?.invoice_raised && (
              <Card>
                <CardHeader
                  title="Invoice"
                  action={
                    <Button
                      variant="ghost"
                      size="sm"
                      icon={EyeIcon}
                      onClick={handlePreviewInvoice}
                    >
                      Preview PDF
                    </Button>
                  }
                />
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Subtotal (excl. {taxLabel})</span>
                    <span>{formatPrice(request?.invoice_amount || 0)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">{taxLabel} ({taxRate}%)</span>
                    <span>{formatPrice(calculateTax(request?.invoice_amount || 0))}</span>
                  </div>
                  <div className="flex justify-between font-semibold text-base border-t pt-2">
                    <span>Total (incl. {taxLabel})</span>
                    <span>{formatPrice(calculateTotalWithTax(request?.invoice_amount || 0))}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2">
                    <span className="text-gray-500">Status</span>
                    <Badge status={request?.invoice_paid ? 'completed' : 'pending'}>
                      {request?.invoice_paid ? 'Paid' : 'Pending'}
                    </Badge>
                  </div>
                </div>
                {!request?.invoice_paid && request?.payment_link && isOwner && (
                  <div className="mt-4">
                    <a
                      href={request.payment_link}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Button icon={CurrencyDollarIcon}>Pay Now</Button>
                    </a>
                  </div>
                )}
              </Card>
            )}

            {/* Cost Tracking (Admin/Accountant only) */}
            {isStaff && (
              <Card>
                <CardHeader
                  title="Cost Tracking"
                  subtitle="Track actual costs for profitability analysis"
                  action={
                    <Button
                      variant="secondary"
                      size="sm"
                      icon={PencilSquareIcon}
                      onClick={openCostModal}
                    >
                      Edit
                    </Button>
                  }
                />
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Actual Cost</span>
                    <span>{request?.actual_cost ? formatPrice(request.actual_cost) : <span className="text-gray-400">Not set</span>}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Labor Hours</span>
                    <span>{request?.labor_hours || 0} hrs</span>
                  </div>
                  {request?.labor_rate && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Labor Rate</span>
                      <span>{formatPrice(request.labor_rate)}/hr</span>
                    </div>
                  )}
                  {request?.invoice_amount && request?.actual_cost && (
                    <>
                      <div className="flex justify-between border-t pt-2">
                        <span className="text-gray-500">Profit</span>
                        <span className={request.invoice_amount - request.actual_cost >= 0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                          {formatPrice(request.invoice_amount - request.actual_cost)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Margin</span>
                        <span className={request.invoice_amount - request.actual_cost >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {((request.invoice_amount - request.actual_cost) / request.invoice_amount * 100).toFixed(1)}%
                        </span>
                      </div>
                    </>
                  )}
                  {request?.cost_notes && (
                    <div className="border-t pt-2">
                      <p className="text-gray-500 text-xs mb-1">Cost Notes:</p>
                      <p className="text-gray-700">{request.cost_notes}</p>
                    </div>
                  )}
                </div>
              </Card>
            )}

            {/* Form Responses */}
            {(formResponses.length > 0 || formQuestions.length > 0) && isStaff && (
              <Card>
                <CardHeader
                  title="Client Information Form"
                  subtitle={formResponses.length > 0 ? 'Submitted by client' : 'Not yet filled by client'}
                  action={
                    <Button
                      variant="secondary"
                      size="sm"
                      icon={PencilSquareIcon}
                      onClick={openFormEditModal}
                    >
                      Edit
                    </Button>
                  }
                />
                <div className="space-y-4">
                  {formResponses.length > 0 ? (
                    formResponses.map((response) =>
                      response.detailed_responses?.map((item, idx) => (
                        <div key={idx} className="border-b border-gray-100 pb-3 last:border-0">
                          <p className="text-sm text-gray-500">{item.question}</p>
                          <p className="font-medium mt-1">
                            {Array.isArray(item.answer)
                              ? item.answer.join(', ')
                              : item.answer || <span className="text-gray-400 italic">No answer</span>}
                          </p>
                        </div>
                      ))
                    )
                  ) : (
                    formQuestions.map((question, idx) => (
                      <div key={idx} className="border-b border-gray-100 pb-3 last:border-0">
                        <p className="text-sm text-gray-500">{question.question_text}</p>
                        <p className="font-medium mt-1 text-gray-400 italic">Not filled</p>
                      </div>
                    ))
                  )}
                </div>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Internal Notes (Staff Only) */}
            {isStaff && (
              <Card>
                <CardHeader
                  title="Internal Notes"
                  action={
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setIsNoteModalOpen(true)}
                    >
                      Add Note
                    </Button>
                  }
                />
                <div className="text-sm text-gray-600 whitespace-pre-wrap">
                  {request?.internal_notes || 'No notes yet'}
                </div>
              </Card>
            )}

            {/* Documents */}
            <Card>
              <CardHeader
                title="Documents"
                action={
                  request?.status !== 'completed' && (
                    <Button
                      variant="secondary"
                      size="sm"
                      icon={DocumentPlusIcon}
                      onClick={() => setIsUploadModalOpen(true)}
                    >
                      Upload
                    </Button>
                  )
                }
              />
              <DocumentList
                documents={documents}
                onRefresh={fetchDocuments}
                canDelete={isOwner || isStaff}
                compact
              />
            </Card>

            {/* Messages */}
            <MessageSection />
          </div>
        </div>
      </div>

      {/* Assign Modal */}
      <Modal
        isOpen={isAssignModalOpen}
        onClose={() => setIsAssignModalOpen(false)}
        title="Assign Request"
      >
        <div className="space-y-4">
          <Select
            label="Select Accountant"
            options={[
              { value: '', label: 'Choose an accountant' },
              ...accountants.map((a) => ({
                value: a.id,
                label: a.full_name || a.email,
              })),
            ]}
            value={selectedAccountant}
            onChange={(e) => setSelectedAccountant(e.target.value)}
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Deadline Date"
              type="date"
              value={deadlineDate}
              onChange={(e) => setDeadlineDate(e.target.value)}
              helper="Optional: When should this job be completed?"
            />
            <Select
              label="Priority"
              options={[
                { value: 'low', label: 'Low' },
                { value: 'normal', label: 'Normal' },
                { value: 'high', label: 'High' },
                { value: 'urgent', label: 'Urgent' },
              ]}
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setIsAssignModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAssign} disabled={!selectedAccountant}>
              Assign
            </Button>
          </div>
        </div>
      </Modal>

      {/* Reassign Modal */}
      <Modal
        isOpen={isReassignModalOpen}
        onClose={() => setIsReassignModalOpen(false)}
        title="Reassign Request"
      >
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
            Currently assigned to: <strong>{request?.assigned_accountant?.full_name}</strong>
          </div>
          <Select
            label="Reassign To"
            options={[
              { value: '', label: 'Choose a staff member' },
              ...accountants
                .filter(a => a.id !== request?.assigned_accountant?.id)
                .map((a) => ({
                  value: a.id,
                  label: a.full_name || a.email,
                })),
            ]}
            value={selectedAccountant}
            onChange={(e) => setSelectedAccountant(e.target.value)}
          />
          <TextArea
            label="Reason for Reassignment"
            value={reassignReason}
            onChange={(e) => setReassignReason(e.target.value)}
            placeholder="Enter reason for reassignment (required for audit trail)"
            rows={3}
            required
          />
          <p className="text-xs text-gray-500 -mt-2">
            This reason will be logged for audit purposes
          </p>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setIsReassignModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleReassign} disabled={!selectedAccountant || !reassignReason.trim()}>
              Reassign
            </Button>
          </div>
        </div>
      </Modal>

      {/* Invoice Modal */}
      <Modal
        isOpen={isInvoiceModalOpen}
        onClose={() => setIsInvoiceModalOpen(false)}
        title="Update Invoice"
      >
        <div className="space-y-4">
          <Input
            label={`Invoice Amount (${currencySettings.currency_symbol} excl. ${taxLabel})`}
            type="number"
            step="0.01"
            value={invoiceData.invoice_amount}
            onChange={(e) =>
              setInvoiceData({ ...invoiceData, invoice_amount: e.target.value })
            }
            placeholder="0.00"
            helper={`${taxLabel} will be added automatically on the invoice`}
          />
          <Input
            label="Payment Link"
            value={invoiceData.payment_link}
            onChange={(e) =>
              setInvoiceData({ ...invoiceData, payment_link: e.target.value })
            }
            placeholder="https://..."
          />
          <div className="flex justify-end gap-2">
            <Button
              variant="secondary"
              onClick={() => setIsInvoiceModalOpen(false)}
            >
              Cancel
            </Button>
            {!request?.invoice_raised && (
              <Button onClick={() => handleInvoiceUpdate(true, false)}>
                Raise Invoice
              </Button>
            )}
            {request?.invoice_raised && !request?.invoice_paid && (
              <Button
                variant="success"
                onClick={() => handleInvoiceUpdate(true, true)}
              >
                Mark as Paid
              </Button>
            )}
          </div>
        </div>
      </Modal>

      {/* Note Modal */}
      <Modal
        isOpen={isNoteModalOpen}
        onClose={() => setIsNoteModalOpen(false)}
        title="Add Internal Note"
      >
        <div className="space-y-4">
          <TextArea
            value={newNote}
            onChange={(e) => setNewNote(e.target.value)}
            placeholder="Add a note..."
            rows={4}
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setIsNoteModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAddNote} disabled={!newNote.trim()}>
              Add Note
            </Button>
          </div>
        </div>
      </Modal>

      {/* Document Upload Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Supporting Documents"
        size="lg"
      >
        <DocumentUpload
          serviceRequestId={id}
          onUploadComplete={handleDocumentUploadComplete}
        />
      </Modal>

      {/* History Modal (State History + Assignment History) */}
      <Modal
        isOpen={isHistoryModalOpen}
        onClose={() => setIsHistoryModalOpen(false)}
        title="Request History"
        size="lg"
      >
        <div className="space-y-6">
          {/* State History */}
          <div>
            <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <ArrowPathIcon className="h-4 w-4" />
              Status Changes
            </h4>
            <StateHistoryTimeline />
          </div>

          {/* Assignment History */}
          {assignmentHistory.length > 0 && (
            <div className="border-t pt-6">
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <UserGroupIcon className="h-4 w-4" />
                Assignment History
              </h4>
              <div className="space-y-3">
                {assignmentHistory.map((entry) => (
                  <div key={entry.id} className="flex items-start gap-3 text-sm">
                    <div className="w-2 h-2 rounded-full bg-blue-500 mt-2" />
                    <div>
                      <p>
                        {entry.from_user ? (
                          <>
                            <span className="text-gray-500">{entry.from_user.full_name}</span>
                            <span className="mx-2">→</span>
                          </>
                        ) : null}
                        <span className="font-medium">{entry.to_user?.full_name}</span>
                        {entry.assignment_type === 'initial' && (
                          <span className="text-xs text-gray-400 ml-2">(Initial assignment)</span>
                        )}
                      </p>
                      {entry.reason && (
                        <p className="text-gray-500 text-xs mt-1">{entry.reason}</p>
                      )}
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(entry.created_at).toLocaleString()}
                        {entry.assigned_by && ` by ${entry.assigned_by.full_name}`}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </Modal>

      {/* Edit Request Modal */}
      <Modal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        title="Edit Request"
        size="lg"
      >
        <div className="space-y-4">
          {isAdmin && (
            <>
              <Select
                label="Status"
                options={[
                  { value: 'pending', label: 'Pending' },
                  { value: 'assigned', label: 'Assigned' },
                  { value: 'in_progress', label: 'In Progress' },
                  { value: 'query_raised', label: 'Query Raised' },
                  { value: 'review', label: 'Under Review' },
                  { value: 'completed', label: 'Completed' },
                  { value: 'cancelled', label: 'Cancelled' },
                ]}
                value={editData.status}
                onChange={(e) => setEditData({ ...editData, status: e.target.value })}
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Xero Job ID"
                  value={editData.xero_reference_job_id}
                  onChange={(e) => setEditData({ ...editData, xero_reference_job_id: e.target.value })}
                  placeholder="Enter Xero/XPM Job ID"
                />
                <Input
                  label="Internal Reference"
                  value={editData.internal_reference}
                  onChange={(e) => setEditData({ ...editData, internal_reference: e.target.value })}
                  placeholder="Enter internal reference"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label={`Invoice Amount (${currencySettings.currency_symbol} excl. ${taxLabel})`}
                  type="number"
                  value={editData.invoice_amount}
                  onChange={(e) => setEditData({ ...editData, invoice_amount: e.target.value })}
                  placeholder="0.00"
                />
                <Input
                  label="Payment Link"
                  value={editData.payment_link}
                  onChange={(e) => setEditData({ ...editData, payment_link: e.target.value })}
                  placeholder="https://..."
                />
              </div>

              <div className="flex gap-4">
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={editData.invoice_raised}
                    onChange={(e) => setEditData({ ...editData, invoice_raised: e.target.checked })}
                    className="h-4 w-4 text-primary-600 rounded border-gray-300"
                  />
                  <span className="text-sm">Invoice Raised</span>
                </label>
                <label className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={editData.invoice_paid}
                    onChange={(e) => setEditData({ ...editData, invoice_paid: e.target.checked })}
                    className="h-4 w-4 text-primary-600 rounded border-gray-300"
                  />
                  <span className="text-sm">Invoice Paid</span>
                </label>
              </div>

              {/* Client Entity Selection */}
              <div className="border-t pt-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Client Entity (Organization)
                </label>
                <ClientEntitySelector
                  value={selectedEntityForEdit}
                  onChange={(entity) => {
                    setSelectedEntityForEdit(entity);
                    setEditData({ ...editData, client_entity_id: entity?.id || null });
                  }}
                  placeholder="Select client entity (optional)..."
                  allowCreate={false}
                  clearable={true}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Link this request to a specific client organization (company, trust, etc.)
                </p>
              </div>
            </>
          )}

          {isAccountant && !isAdmin && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800">
              As an accountant, you can only edit internal notes. Contact your practice owner to update status, Xero ID, or invoice details.
            </div>
          )}

          <TextArea
            label="Internal Notes"
            value={editData.internal_notes}
            onChange={(e) => setEditData({ ...editData, internal_notes: e.target.value })}
            placeholder="Add internal notes..."
            rows={4}
          />

          <div className="flex justify-end gap-2 pt-4 border-t">
            <Button variant="secondary" onClick={() => setIsEditModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleEditSubmit} loading={isEditing}>
              Save Changes
            </Button>
          </div>
        </div>
      </Modal>

      {/* Form Response Edit Modal */}
      <Modal
        isOpen={isFormEditModalOpen}
        onClose={() => setIsFormEditModalOpen(false)}
        title="Edit Client Information"
        size="lg"
      >
        <div className="space-y-4 max-h-[60vh] overflow-y-auto">
          {(() => {
            // Group formEditData by sections, handling repeatable sections
            const sections = {};
            const renderedGroups = new Set();
            formEditData.forEach(item => {
              const secKey = item.section_number || 1;
              if (!sections[secKey]) sections[secKey] = { items: [], title: item.section_title };
              sections[secKey].items.push(item);
            });

            const renderField = (item, value, onChange, keySuffix = '') => {
              const fieldKey = `${item.question_id}${keySuffix}`;
              if (item.question_type === 'textarea') {
                return <TextArea key={fieldKey} label={item.question_text} value={value || ''} onChange={(e) => onChange(e.target.value)} rows={3} />;
              } else if (item.question_type === 'select') {
                return <Select key={fieldKey} label={item.question_text} options={[{ value: '', label: 'Select...' }, ...(item.options || []).map(opt => ({ value: opt, label: opt }))]} value={value || ''} onChange={(e) => onChange(e.target.value)} />;
              } else if (item.question_type === 'radio') {
                return (
                  <div key={fieldKey}>
                    <label className="block text-sm font-medium text-gray-700 mb-2">{item.question_text}</label>
                    <div className="flex flex-wrap gap-4">
                      {(item.options || []).map((opt, optIdx) => (
                        <label key={optIdx} className="flex items-center gap-2 cursor-pointer">
                          <input type="radio" name={`form-edit-${fieldKey}`} value={opt} checked={value === opt} onChange={() => onChange(opt)} className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500" />
                          <span className="text-sm text-gray-700">{opt}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                );
              } else if (item.question_type === 'checkbox' || item.question_type === 'multiselect') {
                const selected = Array.isArray(value) ? value : [];
                return (
                  <div key={fieldKey}>
                    <label className="block text-sm font-medium text-gray-700 mb-2">{item.question_text}</label>
                    <div className="space-y-2">
                      {(item.options || []).map((opt, optIdx) => (
                        <label key={optIdx} className="flex items-center gap-2">
                          <input type="checkbox" checked={selected.includes(opt)} onChange={(e) => { e.target.checked ? onChange([...selected, opt]) : onChange(selected.filter(v => v !== opt)); }} className="h-4 w-4 text-primary-600 rounded border-gray-300" />
                          <span className="text-sm">{opt}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                );
              } else if (item.question_type === 'date') {
                return <Input key={fieldKey} type="date" label={item.question_text} value={value || ''} onChange={(e) => onChange(e.target.value)} />;
              } else if (item.question_type === 'number') {
                return <Input key={fieldKey} type="number" label={item.question_text} value={value || ''} onChange={(e) => onChange(e.target.value)} />;
              } else if (item.question_type === 'file') {
                return (
                  <div key={fieldKey}>
                    <label className="block text-sm font-medium text-gray-700 mb-2">{item.question_text}</label>
                    {value && <p className="text-sm text-gray-500 mb-2">Current: {value}</p>}
                    <input type="file" accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx" onChange={(e) => { const file = e.target.files[0]; if (file) { onChange(file.name); setFormEditFiles(prev => ({ ...prev, [fieldKey]: file })); } }} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100" />
                  </div>
                );
              } else {
                return <Input key={fieldKey} label={item.question_text} value={value || ''} onChange={(e) => onChange(e.target.value)} />;
              }
            };

            return Object.entries(sections).sort(([a], [b]) => Number(a) - Number(b)).map(([secNum, sec]) => {
              const repeatableItems = sec.items.filter(i => i.is_section_repeatable && i.section_group);
              const regularItems = sec.items.filter(i => !i.is_section_repeatable || !i.section_group);
              const sectionGroup = repeatableItems.length > 0 ? repeatableItems[0].section_group : null;

              // Skip if this repeatable group was already rendered
              if (sectionGroup && renderedGroups.has(sectionGroup)) return null;
              if (sectionGroup) renderedGroups.add(sectionGroup);

              const group = sectionGroup ? formEditRepeatables[sectionGroup] : null;
              const entityLabel = sectionGroup
                ? (sectionGroup.charAt(0).toUpperCase() + sectionGroup.slice(1))
                : '';

              const cardColors = [
                { bg: 'bg-blue-50', border: 'border-blue-200', header: 'bg-blue-100', icon: 'text-blue-600' },
                { bg: 'bg-green-50', border: 'border-green-200', header: 'bg-green-100', icon: 'text-green-600' },
                { bg: 'bg-purple-50', border: 'border-purple-200', header: 'bg-purple-100', icon: 'text-purple-600' },
                { bg: 'bg-amber-50', border: 'border-amber-200', header: 'bg-amber-100', icon: 'text-amber-600' },
                { bg: 'bg-rose-50', border: 'border-rose-200', header: 'bg-rose-100', icon: 'text-rose-600' },
              ];

              return (
                <div key={secNum}>
                  {sec.title && (
                    <h3 className="font-semibold text-gray-900 mb-3 mt-4 first:mt-0">{sec.title}</h3>
                  )}

                  {/* Regular (non-repeatable) fields */}
                  {regularItems.map(item => (
                    <div key={item.question_id} className="mb-3">
                      {renderField(item, item.answer, (val) => updateFormEditAnswer(item.question_id, val))}
                    </div>
                  ))}

                  {/* Repeatable section instances */}
                  {group && group.instances.map((instance, idx) => {
                    const colors = cardColors[idx % cardColors.length];
                    const collapseKey = `${sectionGroup}_${instance.id}`;
                    const isCollapsed = formEditCollapsed[collapseKey] || false;
                    // Get name field for summary
                    const nameField = repeatableItems.find(i => i.question_text.toLowerCase().includes('name'));
                    const summary = nameField ? getRepeatableAnswer(nameField.question_id, instance.id) : '';

                    return (
                      <div key={instance.id} className={`rounded-xl border-2 ${colors.border} overflow-hidden shadow-sm mb-3`}>
                        <div
                          className={`${colors.header} px-4 py-3 flex items-center justify-between cursor-pointer`}
                          onClick={() => setFormEditCollapsed(prev => ({ ...prev, [collapseKey]: !prev[collapseKey] }))}
                        >
                          <div className="flex items-center gap-3">
                            <div className={`p-1.5 rounded-full ${colors.bg}`}>
                              <UserIcon className={`h-4 w-4 ${colors.icon}`} />
                            </div>
                            <div>
                              <span className="font-semibold text-gray-800 text-sm">
                                {entityLabel} {idx + 1}
                              </span>
                              {isCollapsed && summary && (
                                <span className="text-sm text-gray-600 ml-2">- {summary}</span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-1">
                            {group.instances.length > group.min && (
                              <button
                                type="button"
                                onClick={(e) => { e.stopPropagation(); removeRepeatableEditInstance(sectionGroup, instance.id); }}
                                className="p-1 rounded hover:bg-red-100 text-gray-400 hover:text-red-600"
                              >
                                <TrashIcon className="h-4 w-4" />
                              </button>
                            )}
                            {isCollapsed ? <ChevronDownIcon className="h-4 w-4 text-gray-500" /> : <ChevronUpIcon className="h-4 w-4 text-gray-500" />}
                          </div>
                        </div>
                        {!isCollapsed && (
                          <div className={`${colors.bg} px-4 py-3 space-y-3`}>
                            {repeatableItems.map(item =>
                              renderField(
                                item,
                                getRepeatableAnswer(item.question_id, instance.id),
                                (val) => updateRepeatableAnswer(item.question_id, instance.id, val),
                                `_${instance.id}`
                              )
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}

                  {/* Add more button */}
                  {group && group.instances.length < group.max && (
                    <button
                      type="button"
                      onClick={() => addRepeatableEditInstance(sectionGroup)}
                      className="w-full py-3 border-2 border-dashed border-gray-300 rounded-xl text-gray-600 hover:border-primary-400 hover:text-primary-600 hover:bg-primary-50 transition-all flex items-center justify-center gap-2 mb-3"
                    >
                      <PlusIcon className="h-4 w-4" />
                      <span className="text-sm font-medium">Add Another {entityLabel}</span>
                    </button>
                  )}
                </div>
              );
            });
          })()}

          {/* Supporting Document Upload Section */}
          <div className="mt-6 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center gap-2">
              <DocumentPlusIcon className="h-4 w-4" />
              Attach Supporting Documents
            </h4>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-primary-400 transition-colors">
              <input
                type="file"
                multiple
                accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.xls,.xlsx,.csv,.txt"
                onChange={(e) => {
                  const files = Array.from(e.target.files);
                  files.forEach(file => {
                    const key = `general_${Date.now()}_${file.name}`;
                    setFormEditFiles(prev => ({ ...prev, [key]: file }));
                  });
                  e.target.value = '';
                }}
                className="hidden"
                id="form-edit-file-upload"
              />
              <label htmlFor="form-edit-file-upload" className="cursor-pointer">
                <CloudArrowUpIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                <p className="text-sm text-gray-600">Click to upload supporting documents</p>
                <p className="text-xs text-gray-400 mt-1">PDF, PNG, JPG, DOC, XLS, CSV (max 50MB)</p>
              </label>
            </div>
            {Object.keys(formEditFiles).length > 0 && (
              <div className="mt-2 space-y-1">
                {Object.entries(formEditFiles).map(([key, file]) => (
                  <div key={key} className="flex items-center justify-between p-2 bg-gray-50 rounded text-sm">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <PaperClipIcon className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      <span className="truncate">{file.name}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setFormEditFiles(prev => {
                        const updated = { ...prev };
                        delete updated[key];
                        return updated;
                      })}
                      className="text-gray-400 hover:text-red-500 ml-2"
                    >
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="flex justify-end gap-2 pt-4 mt-4 border-t">
          <Button variant="secondary" onClick={() => setIsFormEditModalOpen(false)}>
            Cancel
          </Button>
          <Button onClick={handleFormEditSubmit} loading={isFormEditing}>
            Save Changes
          </Button>
        </div>
      </Modal>

      {/* Cost Tracking Modal */}
      <Modal
        isOpen={isCostModalOpen}
        onClose={() => setIsCostModalOpen(false)}
        title="Update Cost Details"
      >
        <div className="space-y-4">
          <Input
            label={`Actual Cost (${currencySettings.currency_symbol})`}
            type="number"
            step="0.01"
            value={costData.actual_cost}
            onChange={(e) => setCostData({ ...costData, actual_cost: e.target.value })}
            placeholder="0.00"
            helper="Total cost incurred for this job"
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Labor Hours"
              type="number"
              step="0.5"
              value={costData.labor_hours}
              onChange={(e) => setCostData({ ...costData, labor_hours: e.target.value })}
              placeholder="0"
            />
            <Input
              label={`Hourly Rate (${currencySettings.currency_symbol})`}
              type="number"
              step="0.01"
              value={costData.labor_rate}
              onChange={(e) => setCostData({ ...costData, labor_rate: e.target.value })}
              placeholder="0.00"
            />
          </div>
          <TextArea
            label="Cost Notes"
            value={costData.cost_notes}
            onChange={(e) => setCostData({ ...costData, cost_notes: e.target.value })}
            placeholder="Notes about costs (materials, subcontractors, etc.)"
            rows={3}
          />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setIsCostModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCostUpdate}>
              Save Cost Details
            </Button>
          </div>
        </div>
      </Modal>

      {/* Task Modal */}
      <Modal
        isOpen={isTaskModalOpen}
        onClose={() => setIsTaskModalOpen(false)}
        title={editingTask ? 'Edit Task' : 'Create Task'}
      >
        <form onSubmit={handleTaskSubmit} className="space-y-4">
          <Input
            label="Title"
            value={taskFormData.title}
            onChange={(e) => setTaskFormData({ ...taskFormData, title: e.target.value })}
            placeholder="Task title"
            required
          />

          <TextArea
            label="Description"
            value={taskFormData.description}
            onChange={(e) => setTaskFormData({ ...taskFormData, description: e.target.value })}
            placeholder="Task description (optional)"
            rows={3}
          />

          <div className="grid grid-cols-2 gap-4">
            <Select
              label="Assign To"
              options={[
                { value: '', label: 'Unassigned' },
                ...accountants.map((a) => ({ value: a.id, label: a.full_name || a.email })),
              ]}
              value={taskFormData.assigned_to_id}
              onChange={(e) => setTaskFormData({ ...taskFormData, assigned_to_id: e.target.value })}
              disabled={!isAdmin && taskFormData.assigned_to_id === user?.id}
            />

            <Select
              label="Priority"
              options={[
                { value: 'low', label: 'Low' },
                { value: 'normal', label: 'Normal' },
                { value: 'high', label: 'High' },
                { value: 'urgent', label: 'Urgent' },
              ]}
              value={taskFormData.priority}
              onChange={(e) => setTaskFormData({ ...taskFormData, priority: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Due Date"
              type="date"
              value={taskFormData.due_date}
              onChange={(e) => setTaskFormData({ ...taskFormData, due_date: e.target.value })}
            />

            <Input
              label="Estimated Hours"
              type="number"
              min="0"
              step="0.5"
              value={taskFormData.estimated_minutes}
              onChange={(e) => setTaskFormData({ ...taskFormData, estimated_minutes: e.target.value })}
              placeholder="e.g., 2"
            />
          </div>

          <div className="flex justify-between pt-4 border-t">
            <div>
              {editingTask && isAdmin && (
                <Button
                  variant="danger"
                  type="button"
                  onClick={() => {
                    handleDeleteTask(editingTask.id);
                    setIsTaskModalOpen(false);
                  }}
                >
                  Delete
                </Button>
              )}
            </div>
            <div className="flex gap-3">
              <Button variant="secondary" type="button" onClick={() => setIsTaskModalOpen(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={isTaskSubmitting}>
                {editingTask ? 'Update Task' : 'Create Task'}
              </Button>
            </div>
          </div>
        </form>
      </Modal>
    </DashboardLayout>
  );
}
