import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  CheckIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  DocumentTextIcon,
  CloudArrowUpIcon,
  CheckCircleIcon,
  PaperClipIcon,
  XMarkIcon,
  FolderIcon,
  DocumentArrowUpIcon,
  UserIcon,
  BookmarkIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { TextArea, Select } from '../../components/common/Input';
import DynamicForm from '../../components/forms/DynamicForm';
import { ClientEntitySelector, ClientEntityForm } from '../../components/features/client-entities';
import { servicesAPI, requestsAPI, formsAPI, documentsAPI, userAPI, clientEntitiesAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import useCompanyStore from '../../store/companyStore';

// Default questions if service has no form attached
const DEFAULT_SERVICE_QUESTIONS = {
  'Individual Tax Return': [
    { id: 'tfn', question_text: 'What is your Tax File Number (TFN)?', question_type: 'text', is_required: true, allow_attachment: false, placeholder: 'XXX XXX XXX' },
    { id: 'dob', question_text: 'Date of Birth', question_type: 'date', is_required: true, allow_attachment: false },
    { id: 'occupation', question_text: 'What is your current occupation?', question_type: 'text', is_required: true, allow_attachment: false },
    { id: 'income_type', question_text: 'What types of income did you receive?', question_type: 'multiselect', is_required: true, allow_attachment: false, options: ['Salary/Wages', 'Bank Interest', 'Dividends', 'Rental Income', 'Capital Gains', 'Government Payments', 'Other'] },
    { id: 'payg_summary', question_text: 'Upload your PAYG Payment Summary', question_type: 'text', is_required: false, allow_attachment: true, help_text: 'Please attach your PAYG summary from your employer' },
    { id: 'deductions', question_text: 'What deductions do you want to claim?', question_type: 'multiselect', is_required: false, allow_attachment: true, options: ['Work from Home', 'Vehicle/Travel', 'Uniform/Clothing', 'Tools & Equipment', 'Self Education', 'Donations', 'Other'], help_text: 'Attach receipts for claimed deductions' },
    { id: 'health_insurance', question_text: 'Do you have Private Health Insurance?', question_type: 'radio', is_required: true, allow_attachment: true, options: ['Yes', 'No'], help_text: 'If yes, please attach your health insurance statement' },
    { id: 'additional_info', question_text: 'Any additional information we should know?', question_type: 'textarea', is_required: false, allow_attachment: true, help_text: 'Attach any other relevant documents' },
  ],
  'Business Activity Statement (BAS)': [
    { id: 'abn', question_text: 'What is your ABN?', question_type: 'text', is_required: true, allow_attachment: false, placeholder: 'XX XXX XXX XXX' },
    { id: 'business_name', question_text: 'Business Name', question_type: 'text', is_required: true, allow_attachment: false },
    { id: 'bas_period', question_text: 'Which period is this BAS for?', question_type: 'select', is_required: true, allow_attachment: false, options: ['July-September (Q1)', 'October-December (Q2)', 'January-March (Q3)', 'April-June (Q4)', 'Monthly'] },
    { id: 'gst_registered', question_text: 'Are you registered for GST?', question_type: 'radio', is_required: true, allow_attachment: false, options: ['Yes', 'No'] },
    { id: 'total_sales', question_text: 'Total Sales/Income for the period (inc. GST)', question_type: 'number', is_required: true, allow_attachment: true, placeholder: '0.00', help_text: 'Attach sales reports/invoices' },
    { id: 'total_purchases', question_text: 'Total Purchases/Expenses for the period (inc. GST)', question_type: 'number', is_required: true, allow_attachment: true, placeholder: '0.00', help_text: 'Attach purchase invoices/receipts' },
    { id: 'payg_withholding', question_text: 'Do you have PAYG Withholding obligations?', question_type: 'radio', is_required: true, allow_attachment: false, options: ['Yes', 'No'] },
    { id: 'wages_paid', question_text: 'Total Wages Paid (if applicable)', question_type: 'number', is_required: false, allow_attachment: true, placeholder: '0.00', help_text: 'Attach payroll summary' },
    { id: 'notes', question_text: 'Any additional notes or queries?', question_type: 'textarea', is_required: false, allow_attachment: true },
  ],
};

export default function NewServiceRequest() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user: currentUser } = useAuthStore();
  const { fetchCompany, formatPrice, getTaxLabel } = useCompanyStore();
  const isAdmin = currentUser?.role === 'super_admin' || currentUser?.role === 'admin';
  const taxLabel = getTaxLabel();

  // Steps depend on whether admin is creating for another user
  const STEPS = isAdmin ? ['Select Client', 'Select Services', 'Fill Details', 'Review & Submit'] : ['Select Services', 'Fill Details', 'Review & Submit'];

  const [currentStep, setCurrentStep] = useState(0);
  const [services, setServices] = useState([]);
  const [selectedServices, setSelectedServices] = useState([]);
  const [formAnswers, setFormAnswers] = useState({});
  const [uploadedFiles, setUploadedFiles] = useState({});
  const [questionAttachments, setQuestionAttachments] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentServiceIndex, setCurrentServiceIndex] = useState(0);
  const [dynamicFormData, setDynamicFormData] = useState({});
  const fileInputRefs = useRef({});
  const sidebarFileInputRef = useRef(null);

  // User selection state for admin
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userSearchQuery, setUserSearchQuery] = useState('');
  const [isLoadingUsers, setIsLoadingUsers] = useState(false);

  // Client entity selection state (optional)
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [showEntityForm, setShowEntityForm] = useState(false);
  const [userEntities, setUserEntities] = useState([]);
  const [isLoadingEntities, setIsLoadingEntities] = useState(false);
  const [entityDetails, setEntityDetails] = useState(null);

  // Draft save/resume
  const DRAFT_KEY = `service_request_draft_${currentUser?.id || 'anon'}`;
  const [draftLoaded, setDraftLoaded] = useState(false);
  const [hasDraft, setHasDraft] = useState(false);
  const [showDraftPrompt, setShowDraftPrompt] = useState(false);
  const [serverDrafts, setServerDrafts] = useState([]);  // Draft requests from DB
  const [draftRequestIds, setDraftRequestIds] = useState({});  // {service_id: request_id}

  // Fetch full entity details when entity is selected (for TFN/ABN pre-fill)
  useEffect(() => {
    if (selectedEntity?.id) {
      clientEntitiesAPI.get(selectedEntity.id).then(res => {
        const entity = res.data.entity || res.data.data?.entity || res.data;
        setEntityDetails(entity);
      }).catch(() => setEntityDetails(null));
    } else {
      setEntityDetails(null);
    }
  }, [selectedEntity?.id]);

  // Pre-fill form answers from entity data when entering form details step
  useEffect(() => {
    if (!entityDetails || selectedServices.length === 0) return;
    const detailsStep = isAdmin ? 2 : 1;
    if (currentStep !== detailsStep) return;

    // Build keyword-to-value mapping from entity data
    const prefillMap = [];
    if (entityDetails.tfn) {
      prefillMap.push({ keywords: ['tfn', 'tax file number'], value: entityDetails.tfn });
    }
    if (entityDetails.abn) {
      prefillMap.push({ keywords: ['abn', 'australian business number'], value: entityDetails.abn });
    }
    if (entityDetails.acn) {
      prefillMap.push({ keywords: ['acn', 'australian company number'], value: entityDetails.acn });
    }
    if (entityDetails.name) {
      prefillMap.push({ keywords: ['business name', 'company name', 'trust name', 'partnership name', 'entity name', 'full name of the trust', 'name of the trust'], value: entityDetails.name });
    }
    if (entityDetails.entity_type) {
      prefillMap.push({ keywords: ['type of trust', 'entity type', 'business type'], value: entityDetails.entity_type });
    }

    if (prefillMap.length === 0) return;

    // Pre-fill for each selected service
    const newFormAnswers = { ...formAnswers };
    const newDynamicData = { ...dynamicFormData };

    selectedServices.forEach(service => {
      const questions = getQuestionsForService(service);
      if (!questions.length) return;

      const prefilled = {};
      questions.forEach(q => {
        const qText = (q.question_text || '').toLowerCase();
        for (const { keywords, value } of prefillMap) {
          if (keywords.some(kw => qText.includes(kw))) {
            prefilled[q.id] = value;
            break;
          }
        }
      });

      if (Object.keys(prefilled).length > 0) {
        // For simple forms
        newFormAnswers[service.name] = {
          ...prefilled,
          ...newFormAnswers[service.name], // Don't overwrite user edits
        };
        // For dynamic forms
        if (usesDynamicForm(service)) {
          newDynamicData[service.name] = {
            ...newDynamicData[service.name],
            formData: {
              ...prefilled,
              ...newDynamicData[service.name]?.formData,
            },
          };
        }
      }
    });

    setFormAnswers(newFormAnswers);
    setDynamicFormData(newDynamicData);
  }, [entityDetails, currentStep, selectedServices.length]);

  // Pre-fill form answers from current user's profile data (TFN, DOB, occupation, etc.)
  useEffect(() => {
    if (!currentUser || selectedServices.length === 0) return;
    const detailsStep = isAdmin ? 2 : 1;
    if (currentStep !== detailsStep) return;

    // Build keyword-to-value mapping from user profile
    const userPrefillMap = [];
    if (currentUser.tfn) {
      userPrefillMap.push({ keywords: ['tfn', 'tax file number'], value: currentUser.tfn });
    }
    if (currentUser.date_of_birth) {
      userPrefillMap.push({ keywords: ['date of birth', 'dob', 'birth date'], value: currentUser.date_of_birth });
    }
    if (currentUser.occupation) {
      userPrefillMap.push({ keywords: ['occupation', 'current occupation'], value: currentUser.occupation });
    }
    if (currentUser.phone) {
      userPrefillMap.push({ keywords: ['phone', 'mobile', 'contact number', 'telephone'], value: currentUser.phone });
    }
    if (currentUser.email) {
      userPrefillMap.push({ keywords: ['email address', 'email'], value: currentUser.email });
    }
    if (currentUser.address) {
      userPrefillMap.push({ keywords: ['residential address', 'current address', 'postal address', 'address'], value: currentUser.address });
    }
    if (currentUser.first_name && currentUser.last_name) {
      userPrefillMap.push({ keywords: ['full name', 'your name', 'name of the taxpayer', 'taxpayer name'], value: `${currentUser.first_name} ${currentUser.last_name}` });
    }
    if (currentUser.visa_status) {
      userPrefillMap.push({ keywords: ['visa', 'residency status', 'visa status'], value: currentUser.visa_status });
    }
    if (currentUser.bsb) {
      userPrefillMap.push({ keywords: ['bsb'], value: currentUser.bsb });
    }
    if (currentUser.bank_account_number) {
      userPrefillMap.push({ keywords: ['account number', 'bank account number'], value: currentUser.bank_account_number });
    }
    if (currentUser.bank_account_holder_name) {
      userPrefillMap.push({ keywords: ['account holder', 'account name', 'bank account holder'], value: currentUser.bank_account_holder_name });
    }

    if (userPrefillMap.length === 0) return;

    const newFormAnswers = { ...formAnswers };
    const newDynamicData = { ...dynamicFormData };

    selectedServices.forEach(service => {
      const questions = getQuestionsForService(service);
      if (!questions.length) return;

      const prefilled = {};
      questions.forEach(q => {
        const qText = (q.question_text || '').toLowerCase();
        for (const { keywords, value } of userPrefillMap) {
          if (keywords.some(kw => qText.includes(kw))) {
            prefilled[q.id] = value;
            break;
          }
        }
      });

      if (Object.keys(prefilled).length > 0) {
        // For simple forms - entity data and user edits take priority
        newFormAnswers[service.name] = {
          ...prefilled,
          ...newFormAnswers[service.name],
        };
        // For dynamic forms
        if (usesDynamicForm(service)) {
          newDynamicData[service.name] = {
            ...newDynamicData[service.name],
            formData: {
              ...prefilled,
              ...newDynamicData[service.name]?.formData,
            },
          };
        }
      }
    });

    setFormAnswers(newFormAnswers);
    setDynamicFormData(newDynamicData);
  }, [currentUser, currentStep, selectedServices.length]);

  // Save draft to localStorage + server
  // extraDynData: optional override for dynamicFormData (handles stale closure from DynamicForm)
  const saveDraft = useCallback(async (saveToServer = false, extraDynData = null) => {
    try {
      // Merge extra dynamic data if provided (from DynamicForm onSaveDraft)
      const mergedDynamicData = extraDynData
        ? { ...dynamicFormData, ...extraDynData }
        : dynamicFormData;

      // Always save to localStorage for quick restore
      const draft = {
        selectedServiceIds: selectedServices.map(s => s.id),
        formAnswers,
        dynamicFormData: mergedDynamicData,
        currentStep,
        currentServiceIndex,
        selectedEntityId: selectedEntity?.id || null,
        selectedUserId: selectedUser?.id || null,
        savedAt: new Date().toISOString(),
        draftRequestIds,
      };
      localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));

      // Save to server when explicitly requested (Save & Continue Later)
      if (saveToServer && selectedServices.length > 0) {
        const formResponsesPayload = {};
        for (const service of selectedServices) {
          const answers = formAnswers[service.name] || {};
          const dynData = mergedDynamicData[service.name];
          const combined = { ...answers };
          if (dynData?.formData) {
            Object.entries(dynData.formData).forEach(([k, v]) => { combined[k] = v; });
          }
          if (service.form_id && Object.keys(combined).length > 0) {
            formResponsesPayload[String(service.id)] = {
              form_id: service.form_id,
              responses: combined,
            };
          }
        }

        const res = await requestsAPI.saveDraft({
          service_ids: selectedServices.map(s => s.id),
          form_responses: formResponsesPayload,
          client_entity_id: selectedEntity?.id || null,
          user_id: isAdmin && selectedUser ? selectedUser.id : null,
        });

        // Store the draft request IDs for later use
        const drafts = res.data?.data?.drafts || [];
        const newDraftIds = {};
        drafts.forEach(d => {
          newDraftIds[d.service?.id] = d.id;
        });
        setDraftRequestIds(newDraftIds);

        // Update localStorage with draft IDs
        draft.draftRequestIds = newDraftIds;
        localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
      }

      return true;
    } catch (e) {
      console.error('Failed to save draft:', e);
      return false;
    }
  }, [selectedServices, formAnswers, dynamicFormData, currentStep, currentServiceIndex, selectedEntity, selectedUser, DRAFT_KEY, draftRequestIds, isAdmin]);

  // Load draft from localStorage (with server draft IDs)
  const loadDraft = useCallback((allServices) => {
    try {
      const saved = localStorage.getItem(DRAFT_KEY);
      if (!saved) return false;
      const draft = JSON.parse(saved);
      if (!draft.selectedServiceIds?.length) return false;

      // Restore selected services from IDs
      const restored = draft.selectedServiceIds
        .map(id => allServices.find(s => s.id === id))
        .filter(Boolean);
      if (restored.length === 0) return false;

      setSelectedServices(restored);
      setFormAnswers(draft.formAnswers || {});
      setDynamicFormData(draft.dynamicFormData || {});
      setCurrentStep(draft.currentStep || 0);
      setCurrentServiceIndex(draft.currentServiceIndex || 0);
      if (draft.draftRequestIds) {
        setDraftRequestIds(draft.draftRequestIds);
      }
      if (draft.selectedUserId && isAdmin) {
        setSelectedUser({ id: draft.selectedUserId });
      }
      setDraftLoaded(true);
      return true;
    } catch (e) {
      console.error('Failed to load draft:', e);
      return false;
    }
  }, [DRAFT_KEY, isAdmin]);

  const clearDraft = useCallback(() => {
    localStorage.removeItem(DRAFT_KEY);
    setHasDraft(false);
  }, [DRAFT_KEY]);

  // Handle explicit "Save & Continue Later" - saves to server + localStorage
  const handleSaveAndExit = useCallback(async (extraDynData = null) => {
    try {
      const result = await saveDraft(true, extraDynData);  // saveToServer = true
      if (result) {
        toast.success('Draft saved! You can resume later.');
        navigate('/dashboard');
      } else {
        toast.error('Failed to save draft');
      }
    } catch (e) {
      toast.error('Failed to save draft');
    }
  }, [saveDraft, navigate]);

  // Auto-save when form data changes (localStorage only, not server)
  useEffect(() => {
    if (!draftLoaded && !selectedServices.length) return;
    if (selectedServices.length > 0 && (Object.keys(formAnswers).length > 0 || Object.keys(dynamicFormData).length > 0)) {
      saveDraft(false);  // localStorage only
    }
  }, [formAnswers, dynamicFormData, currentStep, currentServiceIndex]);

  // Check for existing drafts on mount (localStorage + server)
  useEffect(() => {
    // Check localStorage
    const saved = localStorage.getItem(DRAFT_KEY);
    if (saved) {
      try {
        const draft = JSON.parse(saved);
        if (draft.selectedServiceIds?.length > 0) {
          setHasDraft(true);
          setShowDraftPrompt(true);
        }
      } catch (e) { /* ignore */ }
    }

    // Also fetch server drafts
    requestsAPI.getDrafts().then(res => {
      const drafts = res.data?.data?.drafts || [];
      if (drafts.length > 0) {
        setServerDrafts(drafts);
        if (!saved) {
          setHasDraft(true);
          setShowDraftPrompt(true);
        }
      }
    }).catch(() => { /* ignore */ });
  }, [DRAFT_KEY]);

  useEffect(() => {
    fetchServices();
    fetchCompany(); // Fetch company currency settings
    if (isAdmin) {
      fetchUsers();
      // Check if user_id is passed in URL
      const userIdFromUrl = searchParams.get('user_id');
      if (userIdFromUrl) {
        // Will be set after users are fetched
        setSelectedUser({ id: userIdFromUrl });
      }
    } else {
      // Non-admin users: fetch their linked entities
      fetchUserEntities();
    }
  }, [isAdmin]);

  const fetchUserEntities = async () => {
    setIsLoadingEntities(true);
    try {
      const response = await clientEntitiesAPI.getMyEntities();
      setUserEntities(response.data.entities || []);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load your entities');
    } finally {
      setIsLoadingEntities(false);
    }
  };

  const fetchServices = async () => {
    try {
      const response = await servicesAPI.list();
      // Handle both possible response structures
      const allServices = response.data.data?.services || response.data.services || [];

      // For services with form_id but missing/empty form questions, fetch form data
      const enriched = await Promise.all(
        allServices.map(async (service) => {
          if (service.form_id && (!service.form || !service.form.questions || service.form.questions.length === 0)) {
            try {
              const formRes = await formsAPI.get(service.form_id);
              const formData = formRes.data.data?.form || formRes.data.form || formRes.data;
              return { ...service, form: formData };
            } catch {
              return service;
            }
          }
          return service;
        })
      );

      setServices(enriched);
      return enriched;
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load services');
      return [];
    } finally {
      setIsLoading(false);
    }
  };

  const fetchUsers = async () => {
    setIsLoadingUsers(true);
    try {
      // Fetch client users (role=user) and external accountants (treated as B2B clients)
      const [usersResponse, extAccountantsResponse] = await Promise.all([
        userAPI.list({ role: 'user', per_page: 500 }),
        userAPI.list({ role: 'external_accountant', per_page: 500 }),
      ]);

      const clientUsers = usersResponse.data.data?.users || usersResponse.data.users || [];
      const externalAccountants = extAccountantsResponse.data.data?.users || extAccountantsResponse.data.users || [];

      // Combine both lists - external accountants are B2B clients
      const usersList = [...clientUsers, ...externalAccountants];
      setUsers(usersList);

      // If user_id was passed in URL, find and select that user
      const userIdFromUrl = searchParams.get('user_id');
      if (userIdFromUrl) {
        const foundUser = usersList.find(u => u.id === userIdFromUrl);
        if (foundUser) {
          setSelectedUser(foundUser);
          setCurrentStep(1); // Skip to service selection
        }
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to load users');
    } finally {
      setIsLoadingUsers(false);
    }
  };

  // Filter users based on search query
  const filteredUsers = useMemo(() => {
    if (!userSearchQuery.trim()) return users;
    const query = userSearchQuery.toLowerCase();
    return users.filter(user =>
      user.full_name?.toLowerCase().includes(query) ||
      user.email?.toLowerCase().includes(query) ||
      user.first_name?.toLowerCase().includes(query) ||
      user.last_name?.toLowerCase().includes(query)
    );
  }, [users, userSearchQuery]);

  const toggleService = (service) => {
    setSelectedServices(prev => {
      const isSelected = prev.find(s => s.id === service.id);
      if (isSelected) {
        return prev.filter(s => s.id !== service.id);
      } else {
        return [...prev, service];
      }
    });
  };

  // Get questions for a service
  const getQuestionsForService = (service) => {
    if (service?.form?.questions?.length > 0) {
      return service.form.questions;
    }
    return DEFAULT_SERVICE_QUESTIONS[service?.name] || [];
  };

  // Check if service uses multi-section dynamic form
  const usesDynamicForm = (service) => {
    if (!service?.form?.questions?.length) return false;
    return service.form.questions.some(q => q.section_number > 1 || q.is_section_repeatable);
  };

  // Get required documents for current service
  const getRequiredDocuments = useMemo(() => {
    if (currentStep !== 1 || !selectedServices[currentServiceIndex]) return [];

    const service = selectedServices[currentServiceIndex];
    const questions = getQuestionsForService(service);

    const docs = [];
    questions.forEach(q => {
      if (q.question_type === 'file') {
        docs.push({
          id: q.id,
          name: q.question_text,
          required: q.is_required,
          helpText: q.help_text,
          sectionGroup: q.section_group,
        });
      }
    });

    return docs;
  }, [currentStep, currentServiceIndex, selectedServices]);

  // Handle file upload from sidebar
  const handleSidebarFileUpload = (docId, files) => {
    const serviceName = selectedServices[currentServiceIndex]?.name;
    if (!serviceName) return;

    const key = `${serviceName}_sidebar_${docId}`;
    setUploadedFiles(prev => ({
      ...prev,
      [key]: [...(prev[key] || []), ...Array.from(files)],
    }));
    toast.success(`${files.length} file(s) uploaded`);
  };

  const removeSidebarFile = (docId, index) => {
    const serviceName = selectedServices[currentServiceIndex]?.name;
    const key = `${serviceName}_sidebar_${docId}`;
    setUploadedFiles(prev => ({
      ...prev,
      [key]: prev[key].filter((_, i) => i !== index),
    }));
  };

  const handleAnswerChange = (serviceName, questionId, value) => {
    setFormAnswers(prev => ({
      ...prev,
      [serviceName]: {
        ...prev[serviceName],
        [questionId]: value,
      },
    }));
  };

  const handleMultiSelectChange = (serviceName, questionId, option) => {
    setFormAnswers(prev => {
      const current = prev[serviceName]?.[questionId] || [];
      const isSelected = current.includes(option);
      return {
        ...prev,
        [serviceName]: {
          ...prev[serviceName],
          [questionId]: isSelected
            ? current.filter(o => o !== option)
            : [...current, option],
        },
      };
    });
  };

  const handleQuestionAttachment = (serviceName, questionId, files) => {
    const key = `${serviceName}_${questionId}`;
    setQuestionAttachments(prev => ({
      ...prev,
      [key]: [...(prev[key] || []), ...Array.from(files)],
    }));
  };

  const removeQuestionAttachment = (serviceName, questionId, index) => {
    const key = `${serviceName}_${questionId}`;
    setQuestionAttachments(prev => ({
      ...prev,
      [key]: prev[key].filter((_, i) => i !== index),
    }));
  };

  // Handle DynamicForm submission
  const handleDynamicFormSubmit = (serviceName, data) => {
    setDynamicFormData(prev => ({
      ...prev,
      [serviceName]: data,
    }));
    // Move to next service or review step
    if (currentServiceIndex < selectedServices.length - 1) {
      setCurrentServiceIndex(prev => prev + 1);
    } else {
      const reviewStep = isAdmin ? 3 : 2; // Review step index
      setCurrentStep(reviewStep);
      setCurrentServiceIndex(0);
    }
  };

  // Get step index offsets for admin vs non-admin
  const getStepIndex = (stepName) => {
    const stepNames = isAdmin
      ? ['client', 'services', 'details', 'review']
      : ['services', 'details', 'review'];
    return stepNames.indexOf(stepName);
  };

  const validateCurrentStep = () => {
    const servicesStep = getStepIndex('services');
    const detailsStep = getStepIndex('details');

    // Admin client selection step
    if (isAdmin && currentStep === 0) {
      if (!selectedUser) {
        toast.error('Please select a client');
        return false;
      }
    }

    // Service selection step
    if (currentStep === servicesStep) {
      if (selectedServices.length === 0) {
        toast.error('Please select at least one service');
        return false;
      }
    }

    // Form details step
    if (currentStep === detailsStep) {
      const currentService = selectedServices[currentServiceIndex];
      // Skip validation for DynamicForm (it validates internally)
      if (usesDynamicForm(currentService)) return true;

      const questions = getQuestionsForService(currentService);
      const answers = formAnswers[currentService.name] || {};

      for (const q of questions) {
        if (q.is_required && !answers[q.id]) {
          toast.error(`Please answer: ${q.question_text}`);
          return false;
        }
      }
    }
    return true;
  };

  const handleNext = () => {
    if (!validateCurrentStep()) return;

    const detailsStep = getStepIndex('details');
    const reviewStep = getStepIndex('review');

    if (currentStep === detailsStep) {
      const currentService = selectedServices[currentServiceIndex];
      // DynamicForm handles its own navigation
      if (usesDynamicForm(currentService)) return;

      if (currentServiceIndex < selectedServices.length - 1) {
        setCurrentServiceIndex(prev => prev + 1);
      } else {
        setCurrentStep(reviewStep);
        setCurrentServiceIndex(0);
      }
    } else {
      setCurrentStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    const detailsStep = getStepIndex('details');

    if (currentStep === detailsStep && currentServiceIndex > 0) {
      setCurrentServiceIndex(prev => prev - 1);
    } else {
      setCurrentStep(prev => prev - 1);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      const createdRequests = [];

      for (const service of selectedServices) {
        let createdRequest;
        const existingDraftId = draftRequestIds[service.id];

        if (existingDraftId) {
          // We have a draft in the DB - first update form data, then submit it
          // Save latest form data to server first
          const formResponsesPayload = {};
          const answers = formAnswers[service.name] || {};
          const dynData = dynamicFormData[service.name];
          const combined = { ...answers };
          if (dynData?.formData) {
            Object.entries(dynData.formData).forEach(([k, v]) => { combined[k] = v; });
          }
          if (service.form_id && Object.keys(combined).length > 0) {
            formResponsesPayload[String(service.id)] = {
              form_id: service.form_id,
              responses: combined,
            };
          }

          // Update draft with latest data
          await requestsAPI.saveDraft({
            service_ids: [service.id],
            form_responses: formResponsesPayload,
            client_entity_id: selectedEntity?.id || null,
            draft_id: existingDraftId,
          });

          // Submit the draft (converts to pending)
          const submitRes = await requestsAPI.submitDraft(existingDraftId);
          createdRequest = submitRes.data?.data?.request;
        } else {
          // No draft - create fresh request
          const userId = isAdmin && selectedUser ? selectedUser.id : null;
          const entityId = selectedEntity?.id || null;
          const requestResponse = await requestsAPI.create([service.id], userId, entityId);
          createdRequest = requestResponse.data.data.requests?.[0];
        }

        if (createdRequest) {
          createdRequests.push({
            service: service.name,
            requestId: createdRequest.id,
          });

          // Upload all files (general + sidebar + question attachments)
          const allFileKeys = Object.keys(uploadedFiles).filter(k => k.startsWith(service.name));
          for (const key of allFileKeys) {
            const files = uploadedFiles[key] || [];
            for (const file of files) {
              try {
                await documentsAPI.upload(file, createdRequest.id, 'supporting_document');
              } catch (err) {
                console.error('Failed to upload:', err);
              }
            }
          }

          // Upload question attachments
          const qAttachKeys = Object.keys(questionAttachments).filter(k => k.startsWith(service.name));
          for (const key of qAttachKeys) {
            const files = questionAttachments[key] || [];
            for (const file of files) {
              try {
                await documentsAPI.upload(file, createdRequest.id, 'supporting_document');
              } catch (err) {
                console.error('Failed to upload:', err);
              }
            }
          }

          // Submit form data (skip if already saved via draft path)
          const simpleAnswers = formAnswers[service.name];
          const dynamicData = dynamicFormData[service.name];

          if ((simpleAnswers || dynamicData) && !existingDraftId) {
            try {
              let responses = {};
              if (simpleAnswers) {
                Object.entries(simpleAnswers).forEach(([key, value]) => {
                  responses[key] = value;
                });
              }
              if (dynamicData?.formData) {
                Object.entries(dynamicData.formData).forEach(([key, value]) => {
                  responses[key] = value;
                });
              }
              if (service.form_id && Object.keys(responses).length > 0) {
                await formsAPI.submit(service.form_id, responses, createdRequest.id);
              }
              // Upload DynamicForm files
              if (dynamicData?.files) {
                for (const [key, file] of Object.entries(dynamicData.files)) {
                  if (file) {
                    try {
                      await documentsAPI.upload(file, createdRequest.id, 'form_attachment');
                    } catch (err) {
                      console.error('Failed to upload form file:', err);
                    }
                  }
                }
              }
            } catch (err) {
              console.error('Failed to submit form:', err);
            }
          }
        }
      }

      clearDraft();
      toast.success(`${createdRequests.length} service request(s) created successfully!`);
      navigate('/requests');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to create requests');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Document Sidebar Component
  const renderDocumentSidebar = () => {
    const currentService = selectedServices[currentServiceIndex];
    if (!currentService) return null;

    const documents = getRequiredDocuments;
    const serviceName = currentService.name;

    // Don't render sidebar if no documents required
    if (documents.length === 0) return null;

    // Group documents by section
    const groupedDocs = {};
    documents.forEach(doc => {
      const group = doc.sectionGroup || 'general';
      if (!groupedDocs[group]) groupedDocs[group] = [];
      groupedDocs[group].push(doc);
    });

    // Get uploaded count
    const getUploadedCount = (docId) => {
      const key = `${serviceName}_sidebar_${docId}`;
      return uploadedFiles[key]?.length || 0;
    };

    return (
      <div className="w-72 shrink-0">
        <Card className="sticky top-4 p-4">
          <div className="flex items-center gap-2 mb-4">
            <FolderIcon className="h-5 w-5 text-primary-600" />
            <h3 className="font-semibold text-gray-900">Required Documents</h3>
          </div>

          {(
            <div className="space-y-4">
              {Object.entries(groupedDocs).map(([group, docs]) => (
                <div key={group}>
                  {group !== 'general' && (
                    <p className="text-xs font-medium text-gray-500 uppercase mb-2">
                      {group.replace('_', ' ')} Documents
                    </p>
                  )}
                  <div className="space-y-2">
                    {docs.map((doc) => {
                      const uploadedCount = getUploadedCount(doc.id);
                      const key = `${serviceName}_sidebar_${doc.id}`;
                      const files = uploadedFiles[key] || [];

                      return (
                        <div
                          key={doc.id}
                          className={`p-3 rounded-lg border-2 transition-colors ${
                            uploadedCount > 0
                              ? 'border-green-200 bg-green-50'
                              : doc.required
                              ? 'border-amber-200 bg-amber-50'
                              : 'border-gray-200 bg-gray-50'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1 min-w-0">
                              <p className={`text-sm font-medium truncate ${
                                uploadedCount > 0 ? 'text-green-700' : 'text-gray-700'
                              }`}>
                                {doc.name}
                                {doc.required && <span className="text-red-500 ml-1">*</span>}
                              </p>
                              {doc.helpText && (
                                <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">{doc.helpText}</p>
                              )}
                            </div>
                            {uploadedCount > 0 && (
                              <CheckCircleIcon className="h-5 w-5 text-green-500 shrink-0" />
                            )}
                          </div>

                          {/* Uploaded files */}
                          {files.length > 0 && (
                            <div className="mt-2 space-y-1">
                              {files.map((file, idx) => (
                                <div key={idx} className="flex items-center gap-1 text-xs bg-white rounded px-2 py-1">
                                  <DocumentTextIcon className="h-3 w-3 text-gray-400" />
                                  <span className="flex-1 truncate">{file.name}</span>
                                  <button
                                    type="button"
                                    onClick={() => removeSidebarFile(doc.id, idx)}
                                    className="text-red-500 hover:text-red-700"
                                  >
                                    <XMarkIcon className="h-3 w-3" />
                                  </button>
                                </div>
                              ))}
                            </div>
                          )}

                          {/* Upload button */}
                          <div className="mt-2">
                            <input
                              type="file"
                              multiple
                              onChange={(e) => handleSidebarFileUpload(doc.id, e.target.files)}
                              className="hidden"
                              id={`sidebar-upload-${doc.id}`}
                            />
                            <label
                              htmlFor={`sidebar-upload-${doc.id}`}
                              className="inline-flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 cursor-pointer"
                            >
                              <DocumentArrowUpIcon className="h-4 w-4" />
                              {uploadedCount > 0 ? 'Add more' : 'Upload'}
                            </label>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* General documents upload */}
          <div className="mt-4 pt-4 border-t">
            <p className="text-xs font-medium text-gray-500 uppercase mb-2">Other Documents</p>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-3 text-center hover:border-primary-400 transition-colors">
              <input
                type="file"
                multiple
                onChange={(e) => {
                  const key = `${serviceName}_general`;
                  setUploadedFiles(prev => ({
                    ...prev,
                    [key]: [...(prev[key] || []), ...Array.from(e.target.files)],
                  }));
                  toast.success(`${e.target.files.length} file(s) uploaded`);
                }}
                className="hidden"
                id="general-upload"
              />
              <label htmlFor="general-upload" className="cursor-pointer">
                <CloudArrowUpIcon className="h-6 w-6 text-gray-400 mx-auto mb-1" />
                <p className="text-xs text-gray-600">Upload additional files</p>
              </label>
            </div>
            {/* Show general uploaded files */}
            {uploadedFiles[`${serviceName}_general`]?.length > 0 && (
              <div className="mt-2 space-y-1">
                {uploadedFiles[`${serviceName}_general`].map((file, idx) => (
                  <div key={idx} className="flex items-center gap-1 text-xs bg-gray-50 rounded px-2 py-1">
                    <DocumentTextIcon className="h-3 w-3 text-gray-400" />
                    <span className="flex-1 truncate">{file.name}</span>
                    <button
                      type="button"
                      onClick={() => {
                        const key = `${serviceName}_general`;
                        setUploadedFiles(prev => ({
                          ...prev,
                          [key]: prev[key].filter((_, i) => i !== idx),
                        }));
                      }}
                      className="text-red-500 hover:text-red-700"
                    >
                      <XMarkIcon className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>
    );
  };

  const renderStepIndicator = () => (
    <div className="flex items-center justify-center mb-8">
      {STEPS.map((step, index) => (
        <React.Fragment key={step}>
          <div className="flex flex-col items-center">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-medium ${
                index < currentStep
                  ? 'bg-green-500 text-white'
                  : index === currentStep
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-500'
              }`}
            >
              {index < currentStep ? (
                <CheckIcon className="w-5 h-5" />
              ) : (
                index + 1
              )}
            </div>
            <span className={`text-xs mt-2 ${index === currentStep ? 'text-primary-600 font-medium' : 'text-gray-500'}`}>
              {step}
            </span>
          </div>
          {index < STEPS.length - 1 && (
            <div
              className={`w-16 md:w-24 h-1 mx-2 ${
                index < currentStep ? 'bg-green-500' : 'bg-gray-200'
              }`}
            />
          )}
        </React.Fragment>
      ))}
    </div>
  );

  // Client selection for admin
  const renderClientSelection = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Select Client</h2>
        <p className="text-gray-500 mt-2">Choose a client to create a service request for</p>
      </div>

      {/* Search input */}
      <div className="max-w-md mx-auto">
        <Input
          placeholder="Search clients by name or email..."
          value={userSearchQuery}
          onChange={(e) => setUserSearchQuery(e.target.value)}
          className="w-full"
        />
      </div>

      {isLoadingUsers ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
          {filteredUsers.map((user) => {
            const isSelected = selectedUser?.id === user.id;
            return (
              <div
                key={user.id}
                onClick={() => setSelectedUser(user)}
                className={`relative p-4 border-2 rounded-xl cursor-pointer transition-all ${
                  isSelected
                    ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                    : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                }`}
              >
                {isSelected && (
                  <div className="absolute top-3 right-3">
                    <CheckCircleIcon className="w-5 h-5 text-primary-600" />
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center">
                    <UserIcon className={`w-5 h-5 ${isSelected ? 'text-primary-600' : 'text-gray-400'}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium text-gray-900 truncate">
                        {user.full_name || `${user.first_name || ''} ${user.last_name || ''}`.trim() || 'No Name'}
                      </h3>
                      {user.role === 'external_accountant' && (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">
                          B2B
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-500 truncate">{user.email}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {filteredUsers.length === 0 && !isLoadingUsers && (
        <div className="text-center py-8">
          <UserIcon className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500 mb-4">
            {userSearchQuery ? 'No clients found matching your search' : 'No clients in your company yet'}
          </p>
          {!userSearchQuery && (
            <Button
              variant="secondary"
              onClick={() => navigate('/users?invite=true')}
            >
              Invite a Client
            </Button>
          )}
        </div>
      )}

      {selectedUser && (
        <div className="mt-6 space-y-4">
          <div className="p-4 bg-primary-50 rounded-lg border border-primary-200">
            <p className="text-sm text-primary-700">
              <span className="font-medium">Selected client:</span>{' '}
              {selectedUser.full_name || selectedUser.email}
            </p>
          </div>

          {/* Optional Client Entity Selection */}
          <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h4 className="text-sm font-medium text-gray-700 mb-2">
              Client Entity (Optional)
            </h4>
            <p className="text-xs text-gray-500 mb-3">
              Select or create a client organization (company, trust, SMSF, etc.) for this request.
              This helps track work for specific client entities.
            </p>
            <ClientEntitySelector
              value={selectedEntity}
              onChange={setSelectedEntity}
              onCreateNew={() => setShowEntityForm(true)}
              placeholder="Select client entity (optional)..."
              allowCreate={true}
              clearable={true}
            />
          </div>
        </div>
      )}

      {/* Create Entity Modal */}
      {showEntityForm && (
        <ClientEntityForm
          isModal
          onSave={(newEntity) => {
            setSelectedEntity(newEntity);
            setShowEntityForm(false);
          }}
          onCancel={() => setShowEntityForm(false)}
        />
      )}
    </div>
  );

  const renderServiceSelection = () => (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-900">Select Services</h2>
        <p className="text-gray-500 mt-2">
          {isAdmin && selectedUser
            ? `Choose services for ${selectedUser.full_name || selectedUser.email}`
            : 'Choose the services you need help with'}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {services.map((service) => {
          const isSelected = selectedServices.find(s => s.id === service.id);
          return (
            <div
              key={service.id}
              onClick={() => toggleService(service)}
              className={`relative p-6 border-2 rounded-xl cursor-pointer transition-all ${
                isSelected
                  ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200'
                  : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
              }`}
            >
              {isSelected && (
                <div className="absolute top-4 right-4">
                  <CheckCircleIcon className="w-6 h-6 text-primary-600" />
                </div>
              )}
              <DocumentTextIcon className={`w-10 h-10 mb-4 ${isSelected ? 'text-primary-600' : 'text-gray-400'}`} />
              <h3 className="font-semibold text-lg text-gray-900">{service.name}</h3>
              <p className="text-sm text-gray-500 mt-2">{service.description}</p>
              {/* Prices hidden from clients - only shown after invoice is raised */}
              {isAdmin && service.base_price && (
                <div className="mt-3">
                  <p className="text-primary-600 font-medium">
                    From {formatPrice(service.base_price)}
                  </p>
                  <p className="text-xs text-gray-400">excl. {taxLabel}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {selectedServices.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <p className="text-sm text-gray-600">
            <span className="font-medium">{selectedServices.length}</span> service(s) selected:
            <span className="ml-2 text-primary-600">
              {selectedServices.map(s => s.name).join(', ')}
            </span>
          </p>
        </div>
      )}

      {/* Entity selection for regular users (if they have linked entities) */}
      {!isAdmin && userEntities.length > 0 && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Business Entity (Optional)
          </h4>
          <p className="text-xs text-gray-500 mb-3">
            Select which of your business entities this request is for.
          </p>
          {isLoadingEntities ? (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600" />
              Loading your entities...
            </div>
          ) : (
            <Select
              value={selectedEntity?.id || ''}
              onChange={(e) => {
                const entity = userEntities.find(ent => ent.id === e.target.value);
                setSelectedEntity(entity || null);
              }}
              options={[
                { value: '', label: 'Select an entity (optional)' },
                ...userEntities.map(entity => ({
                  value: entity.id,
                  label: `${entity.name}${entity.trading_name ? ` (${entity.trading_name})` : ''} - ${entity.entity_type}`,
                })),
              ]}
            />
          )}
        </div>
      )}
    </div>
  );

  const renderQuestionField = (question, serviceName) => {
    const qId = question.id;
    const value = formAnswers[serviceName]?.[qId] || '';
    const questionType = question.question_type || question.type;
    const isRequired = question.is_required ?? question.required;
    const options = question.options || [];
    const placeholder = question.placeholder || '';
    const helpText = question.help_text;

    switch (questionType) {
      case 'text':
      case 'email':
      case 'phone':
        return (
          <Input
            type={questionType === 'email' ? 'email' : questionType === 'phone' ? 'tel' : 'text'}
            value={value}
            onChange={(e) => handleAnswerChange(serviceName, qId, e.target.value)}
            placeholder={placeholder}
            required={isRequired}
          />
        );
      case 'number':
        return (
          <Input
            type="number"
            step="0.01"
            value={value}
            onChange={(e) => handleAnswerChange(serviceName, qId, e.target.value)}
            placeholder={placeholder}
            required={isRequired}
          />
        );
      case 'date':
        return (
          <Input
            type="date"
            value={value}
            onChange={(e) => handleAnswerChange(serviceName, qId, e.target.value)}
            required={isRequired}
          />
        );
      case 'textarea':
        return (
          <TextArea
            value={value}
            onChange={(e) => handleAnswerChange(serviceName, qId, e.target.value)}
            rows={3}
            placeholder={placeholder}
          />
        );
      case 'select':
        return (
          <Select
            value={value}
            onChange={(e) => handleAnswerChange(serviceName, qId, e.target.value)}
            options={[
              { value: '', label: 'Select an option' },
              ...options.map(opt => ({ value: opt, label: opt })),
            ]}
            required={isRequired}
          />
        );
      case 'radio':
        return (
          <div className="flex flex-wrap gap-4">
            {options.map(option => (
              <label key={option} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name={`${serviceName}-${qId}`}
                  value={option}
                  checked={value === option}
                  onChange={(e) => handleAnswerChange(serviceName, qId, e.target.value)}
                  className="w-4 h-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                />
                <span className="text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        );
      case 'checkbox':
      case 'multiselect':
        const selectedOpts = formAnswers[serviceName]?.[qId] || [];
        return (
          <div className="flex flex-wrap gap-2">
            {options.map(option => (
              <button
                key={option}
                type="button"
                onClick={() => handleMultiSelectChange(serviceName, qId, option)}
                className={`px-3 py-2 rounded-lg border text-sm transition-colors ${
                  selectedOpts.includes(option)
                    ? 'bg-primary-100 border-primary-500 text-primary-700'
                    : 'bg-white border-gray-300 text-gray-700 hover:border-gray-400'
                }`}
              >
                {selectedOpts.includes(option) && (
                  <CheckIcon className="w-4 h-4 inline mr-1" />
                )}
                {option}
              </button>
            ))}
          </div>
        );
      default:
        return (
          <Input
            value={value}
            onChange={(e) => handleAnswerChange(serviceName, qId, e.target.value)}
            placeholder={placeholder}
          />
        );
    }
  };

  const renderFormQuestions = () => {
    const currentService = selectedServices[currentServiceIndex];
    const questions = getQuestionsForService(currentService);
    const hasDynamicForm = usesDynamicForm(currentService);

    return (
      <div className="flex gap-6">
        {/* Document Sidebar */}
        {renderDocumentSidebar()}

        {/* Main Form Content */}
        <div className="flex-1 min-w-0">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">{currentService?.name}</h2>
            <p className="text-gray-500 mt-1">
              Service {currentServiceIndex + 1} of {selectedServices.length}
            </p>
          </div>

          {/* Progress for multiple services */}
          {selectedServices.length > 1 && (
            <div className="flex gap-2 mb-6">
              {selectedServices.map((s, idx) => (
                <div
                  key={s.id}
                  className={`flex-1 h-2 rounded-full ${
                    idx < currentServiceIndex
                      ? 'bg-green-500'
                      : idx === currentServiceIndex
                      ? 'bg-primary-500'
                      : 'bg-gray-200'
                  }`}
                />
              ))}
            </div>
          )}

          {/* Use DynamicForm for multi-section forms */}
          {hasDynamicForm ? (
            <DynamicForm
              form={currentService.form}
              onSubmit={(data) => handleDynamicFormSubmit(currentService.name, data)}
              onSaveDraft={async (data) => {
                setDynamicFormData(prev => ({
                  ...prev,
                  [currentService.name]: data,
                }));
                // Pass data directly to avoid stale closure
                await handleSaveAndExit({ [currentService.name]: data });
              }}
              initialData={dynamicFormData[currentService.name]?.formData || {}}
              submitButtonText={
                currentServiceIndex < selectedServices.length - 1
                  ? `Continue to ${selectedServices[currentServiceIndex + 1]?.name}`
                  : 'Continue to Review'
              }
            />
          ) : (
            /* Simple form */
            <Card className="p-6">
              <div className="space-y-6">
                {questions.filter(q => q.question_type !== 'file').map((question) => {
                  const questionText = question.question_text || question.question;
                  const isRequired = question.is_required ?? question.required;
                  return (
                    <div key={question.id} className="space-y-2">
                      <label className="block text-sm font-medium text-gray-700">
                        {questionText}
                        {isRequired && <span className="text-red-500 ml-1">*</span>}
                      </label>
                      {renderQuestionField(question, currentService.name)}
                      {question.help_text && (
                        <p className="text-xs text-gray-500">{question.help_text}</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </Card>
          )}
        </div>
      </div>
    );
  };

  const renderReview = () => {
    return (
      <div className="space-y-6">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Review & Submit</h2>
          <p className="text-gray-500 mt-2">Review your information before submitting</p>
        </div>

        {selectedServices.map((service) => {
          const questions = getQuestionsForService(service);
          const dynamicData = dynamicFormData[service.name];
          const simpleAnswers = formAnswers[service.name];

          // Count all uploaded files for this service
          const fileCount = Object.keys(uploadedFiles)
            .filter(k => k.startsWith(service.name))
            .reduce((sum, k) => sum + (uploadedFiles[k]?.length || 0), 0);

          return (
            <Card key={service.id} className="p-6">
              <h3 className="font-semibold text-lg text-gray-900 mb-4 flex items-center gap-2">
                <CheckCircleIcon className="w-5 h-5 text-green-500" />
                {service.name}
              </h3>

              <div className="space-y-4">
                {/* Form Answers Summary */}
                <div className="border-b pb-4">
                  <h4 className="text-sm font-medium text-gray-500 mb-3">Information Provided</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Show simple answers */}
                    {simpleAnswers && Object.entries(simpleAnswers).map(([qId, answer]) => {
                      if (!answer || (Array.isArray(answer) && answer.length === 0)) return null;
                      const question = questions.find(q => String(q.id) === String(qId));
                      return (
                        <div key={qId}>
                          <p className="text-xs text-gray-500">{question?.question_text || qId}</p>
                          <p className="text-sm font-medium text-gray-900">
                            {Array.isArray(answer) ? answer.join(', ') : answer}
                          </p>
                        </div>
                      );
                    })}
                    {/* Show dynamic form answers */}
                    {dynamicData?.formData && Object.entries(dynamicData.formData).map(([key, value]) => {
                      if (!value || (Array.isArray(value) && value.length === 0)) return null;
                      return (
                        <div key={key}>
                          <p className="text-xs text-gray-500">Response</p>
                          <p className="text-sm font-medium text-gray-900">
                            {Array.isArray(value) ? value.join(', ') : String(value)}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Documents Summary */}
                <div>
                  <h4 className="text-sm font-medium text-gray-500 mb-3">Documents</h4>
                  {fileCount > 0 ? (
                    <p className="text-sm text-primary-600">{fileCount} document(s) uploaded</p>
                  ) : (
                    <p className="text-sm text-gray-400">No documents uploaded</p>
                  )}
                </div>
              </div>
            </Card>
          );
        })}

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            By submitting, you confirm that all information provided is accurate.
            Our team will review your request and contact you if additional information is needed.
          </p>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <DashboardLayout title="New Service Request">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  const currentService = selectedServices[currentServiceIndex];
  const detailsStep = isAdmin ? 2 : 1;
  const reviewStep = isAdmin ? 3 : 2;
  const showExternalNav = currentStep !== detailsStep || !currentService || !usesDynamicForm(currentService);

  return (
    <DashboardLayout title="New Service Request">
      <div className="max-w-6xl mx-auto">
        {/* Draft Resume Prompt */}
        {showDraftPrompt && hasDraft && (
          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-amber-800">You have an unfinished request</p>
                <p className="text-xs text-amber-600 mt-1">Would you like to continue where you left off?</p>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => { clearDraft(); setServerDrafts([]); setShowDraftPrompt(false); }}
                >
                  Start Fresh
                </Button>
                <Button
                  size="sm"
                  onClick={() => {
                    // Try localStorage first, then fallback to server drafts
                    const localLoaded = loadDraft(services);
                    if (localLoaded) {
                      toast.success('Draft restored!');
                    } else if (serverDrafts.length > 0) {
                      // Restore from server drafts
                      const restoredServices = serverDrafts
                        .map(d => services.find(s => s.id === d.service?.id))
                        .filter(Boolean);
                      if (restoredServices.length > 0) {
                        setSelectedServices(restoredServices);
                        // Restore form answers from server
                        const restoredAnswers = {};
                        const restoredDraftIds = {};
                        serverDrafts.forEach(d => {
                          if (d.service && d.form_response) {
                            restoredAnswers[d.service.name] = d.form_response.responses || {};
                            restoredDraftIds[d.service.id] = d.id;
                          }
                        });
                        setFormAnswers(restoredAnswers);
                        setDraftRequestIds(restoredDraftIds);
                        setDraftLoaded(true);
                        toast.success('Draft restored from server!');
                      }
                    }
                    setShowDraftPrompt(false);
                  }}
                >
                  Resume Draft
                </Button>
              </div>
            </div>
            {serverDrafts.length > 0 && (
              <div className="mt-2 pt-2 border-t border-amber-200">
                <p className="text-xs text-amber-700">
                  Saved drafts: {serverDrafts.map(d => d.service?.name).filter(Boolean).join(', ')}
                </p>
              </div>
            )}
          </div>
        )}

        {renderStepIndicator()}

        <div className="mb-8">
          {isAdmin ? (
            <>
              {currentStep === 0 && renderClientSelection()}
              {currentStep === 1 && renderServiceSelection()}
              {currentStep === 2 && renderFormQuestions()}
              {currentStep === 3 && renderReview()}
            </>
          ) : (
            <>
              {currentStep === 0 && renderServiceSelection()}
              {currentStep === 1 && renderFormQuestions()}
              {currentStep === 2 && renderReview()}
            </>
          )}
        </div>

        {/* Navigation Buttons - Hide when DynamicForm handles navigation */}
        {showExternalNav && (
          <div className="flex justify-between pt-6 border-t">
            <div className="flex gap-2">
              <Button
                variant="secondary"
                icon={ArrowLeftIcon}
                onClick={currentStep === 0 ? () => navigate('/dashboard') : handleBack}
              >
                {currentStep === 0 ? 'Cancel' : 'Back'}
              </Button>
              {selectedServices.length > 0 && currentStep > 0 && (
                <Button
                  variant="secondary"
                  icon={BookmarkIcon}
                  onClick={handleSaveAndExit}
                >
                  Save & Continue Later
                </Button>
              )}
            </div>

            {currentStep < reviewStep ? (
              <Button
                icon={ArrowRightIcon}
                iconPosition="right"
                onClick={handleNext}
              >
                {currentStep === detailsStep && currentServiceIndex < selectedServices.length - 1
                  ? `Next Service (${currentServiceIndex + 2}/${selectedServices.length})`
                  : 'Continue'}
              </Button>
            ) : (
              <Button
                onClick={handleSubmit}
                loading={isSubmitting}
                icon={CheckIcon}
              >
                Submit Request{selectedServices.length > 1 ? 's' : ''}
              </Button>
            )}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
