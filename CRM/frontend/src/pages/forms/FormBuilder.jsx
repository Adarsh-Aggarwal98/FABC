import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  PlusIcon,
  TrashIcon,
  Bars3Icon,
  ArrowLeftIcon,
} from '@heroicons/react/24/outline';
import DashboardLayout from '../../components/layout/DashboardLayout';
import Card, { CardHeader } from '../../components/common/Card';
import Button from '../../components/common/Button';
import Input, { TextArea, Select, Checkbox } from '../../components/common/Input';
import Modal from '../../components/common/Modal';
import { formsAPI } from '../../services/api';

const QUESTION_TYPES = [
  { value: 'text', label: 'Short Text' },
  { value: 'textarea', label: 'Long Text' },
  { value: 'email', label: 'Email' },
  { value: 'phone', label: 'Phone Number' },
  { value: 'number', label: 'Number' },
  { value: 'date', label: 'Date' },
  { value: 'select', label: 'Dropdown' },
  { value: 'radio', label: 'Single Choice' },
  { value: 'checkbox', label: 'Multiple Choice' },
  { value: 'file', label: 'File Upload' },
  { value: 'multiselect', label: 'Multi-Select' },
];

export default function FormBuilder() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState(null);
  const [isLoading, setIsLoading] = useState(!!id);
  const [isSaving, setIsSaving] = useState(false);
  const [isAddQuestionModalOpen, setIsAddQuestionModalOpen] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);

  // Form data for create/edit
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    form_type: 'service',
  });

  // Question data
  const [questionData, setQuestionData] = useState({
    question_text: '',
    question_type: 'text',
    is_required: false,
    allow_attachment: false,
    options: [],
    placeholder: '',
    help_text: '',
  });

  const [newOption, setNewOption] = useState('');

  useEffect(() => {
    if (id) {
      fetchForm();
    }
  }, [id]);

  const fetchForm = async () => {
    setIsLoading(true);
    try {
      const response = await formsAPI.get(id);
      const formData = response.data.data.form;
      setForm(formData);
      setFormData({
        name: formData.name,
        description: formData.description || '',
        form_type: formData.form_type,
      });
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to fetch form');
      navigate('/forms');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveForm = async () => {
    if (!formData.name) {
      toast.error('Form name is required');
      return;
    }

    setIsSaving(true);
    try {
      if (id) {
        await formsAPI.update(id, formData);
        toast.success('Form updated');
      } else {
        const response = await formsAPI.create(formData);
        toast.success('Form created');
        navigate(`/forms/${response.data.data.form.id}`);
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save form');
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddQuestion = async () => {
    if (!questionData.question_text) {
      toast.error('Question text is required');
      return;
    }

    // For types that need options, validate
    const needsOptions = ['select', 'radio', 'checkbox', 'multiselect'];
    if (needsOptions.includes(questionData.question_type) && questionData.options.length < 2) {
      toast.error('Please add at least 2 options');
      return;
    }

    try {
      if (editingQuestion) {
        await formsAPI.updateQuestion(editingQuestion.id, questionData);
        toast.success('Question updated');
      } else {
        await formsAPI.addQuestion(id, questionData);
        toast.success('Question added');
      }
      setIsAddQuestionModalOpen(false);
      resetQuestionForm();
      fetchForm();
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save question');
    }
  };

  const handleDeleteQuestion = async (questionId) => {
    if (!confirm('Are you sure you want to delete this question?')) return;

    try {
      await formsAPI.deleteQuestion(questionId);
      toast.success('Question deleted');
      fetchForm();
    } catch (error) {
      toast.error('Failed to delete question');
    }
  };

  const handleEditQuestion = (question) => {
    setEditingQuestion(question);
    setQuestionData({
      question_text: question.question_text,
      question_type: question.question_type,
      is_required: question.is_required,
      allow_attachment: question.allow_attachment || false,
      options: question.options || [],
      placeholder: question.placeholder || '',
      help_text: question.help_text || '',
    });
    setIsAddQuestionModalOpen(true);
  };

  const resetQuestionForm = () => {
    setEditingQuestion(null);
    setQuestionData({
      question_text: '',
      question_type: 'text',
      is_required: false,
      allow_attachment: false,
      options: [],
      placeholder: '',
      help_text: '',
    });
    setNewOption('');
  };

  const addOption = () => {
    if (!newOption.trim()) return;
    setQuestionData({
      ...questionData,
      options: [...questionData.options, newOption.trim()],
    });
    setNewOption('');
  };

  const removeOption = (index) => {
    setQuestionData({
      ...questionData,
      options: questionData.options.filter((_, i) => i !== index),
    });
  };

  const needsOptions = ['select', 'radio', 'checkbox', 'multiselect'].includes(
    questionData.question_type
  );

  if (isLoading) {
    return (
      <DashboardLayout title="Form Builder">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title={id ? 'Edit Form' : 'Create Form'}>
      <div className="space-y-6 max-w-3xl mx-auto">
        {/* Back Button */}
        <Button
          variant="ghost"
          icon={ArrowLeftIcon}
          onClick={() => navigate('/forms')}
        >
          Back to Forms
        </Button>

        {/* Form Details */}
        <Card>
          <CardHeader
            title="Form Details"
            action={
              <Button onClick={handleSaveForm} loading={isSaving}>
                Save Form
              </Button>
            }
          />
          <div className="space-y-4">
            <Input
              label="Form Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Client Information Form"
              required
            />
            <TextArea
              label="Description"
              value={formData.description}
              onChange={(e) =>
                setFormData({ ...formData, description: e.target.value })
              }
              placeholder="Describe the purpose of this form..."
              rows={2}
            />
            <Select
              label="Form Type"
              options={[
                { value: 'service', label: 'Service Form' },
                { value: 'onboarding', label: 'Onboarding Form' },
                { value: 'general', label: 'General Form' },
              ]}
              value={formData.form_type}
              onChange={(e) =>
                setFormData({ ...formData, form_type: e.target.value })
              }
            />
          </div>
        </Card>

        {/* Questions */}
        {id && (
          <Card>
            <CardHeader
              title="Questions"
              action={
                <Button
                  icon={PlusIcon}
                  onClick={() => {
                    resetQuestionForm();
                    setIsAddQuestionModalOpen(true);
                  }}
                >
                  Add Question
                </Button>
              }
            />

            {!form?.questions || form.questions.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">No questions yet</p>
                <Button
                  variant="secondary"
                  className="mt-4"
                  onClick={() => {
                    resetQuestionForm();
                    setIsAddQuestionModalOpen(true);
                  }}
                >
                  Add your first question
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {form.questions.map((question, index) => (
                  <div
                    key={question.id}
                    className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg"
                  >
                    <div className="text-gray-400 cursor-move">
                      <Bars3Icon className="h-5 w-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-gray-500">
                          {index + 1}.
                        </span>
                        <span className="font-medium">{question.question_text}</span>
                        {question.is_required && (
                          <span className="text-red-500">*</span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs bg-gray-200 px-2 py-0.5 rounded">
                          {QUESTION_TYPES.find((t) => t.value === question.question_type)
                            ?.label || question.question_type}
                        </span>
                        {question.options?.length > 0 && (
                          <span className="text-xs text-gray-400">
                            {question.options.length} options
                          </span>
                        )}
                        {question.allow_attachment && (
                          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                            Allows Attachment
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditQuestion(question)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteQuestion(question.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        )}
      </div>

      {/* Add/Edit Question Modal */}
      <Modal
        isOpen={isAddQuestionModalOpen}
        onClose={() => {
          setIsAddQuestionModalOpen(false);
          resetQuestionForm();
        }}
        title={editingQuestion ? 'Edit Question' : 'Add Question'}
        size="lg"
      >
        <div className="space-y-4">
          <TextArea
            label="Question"
            value={questionData.question_text}
            onChange={(e) =>
              setQuestionData({ ...questionData, question_text: e.target.value })
            }
            placeholder="Enter your question..."
            rows={2}
            required
          />

          <Select
            label="Question Type"
            options={QUESTION_TYPES}
            value={questionData.question_type}
            onChange={(e) =>
              setQuestionData({
                ...questionData,
                question_type: e.target.value,
                options: [],
              })
            }
          />

          {needsOptions && (
            <div>
              <label className="label">Options</label>
              <div className="space-y-2">
                {questionData.options.map((option, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Input
                      value={option}
                      onChange={(e) => {
                        const updated = [...questionData.options];
                        updated[index] = e.target.value;
                        setQuestionData({ ...questionData, options: updated });
                      }}
                      className="flex-1"
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeOption(index)}
                    >
                      <TrashIcon className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                ))}
                <div className="flex items-center gap-2">
                  <Input
                    value={newOption}
                    onChange={(e) => setNewOption(e.target.value)}
                    placeholder="Add option..."
                    className="flex-1"
                    onKeyPress={(e) => e.key === 'Enter' && addOption()}
                  />
                  <Button variant="secondary" size="sm" onClick={addOption}>
                    Add
                  </Button>
                </div>
              </div>
            </div>
          )}

          <Input
            label="Placeholder"
            value={questionData.placeholder}
            onChange={(e) =>
              setQuestionData({ ...questionData, placeholder: e.target.value })
            }
            placeholder="Enter placeholder text..."
          />

          <Input
            label="Help Text"
            value={questionData.help_text}
            onChange={(e) =>
              setQuestionData({ ...questionData, help_text: e.target.value })
            }
            placeholder="Additional instructions for the user..."
          />

          <div className="flex flex-col gap-3">
            <Checkbox
              label="Required"
              checked={questionData.is_required}
              onChange={(e) =>
                setQuestionData({ ...questionData, is_required: e.target.checked })
              }
            />

            <Checkbox
              label="Allow user to attach files to this question"
              checked={questionData.allow_attachment}
              onChange={(e) =>
                setQuestionData({ ...questionData, allow_attachment: e.target.checked })
              }
            />
            {questionData.allow_attachment && (
              <p className="text-xs text-gray-500 ml-6">
                Users will be able to upload supporting documents for this question (PDF, Images, Word, Excel)
              </p>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-4">
            <Button
              variant="secondary"
              onClick={() => {
                setIsAddQuestionModalOpen(false);
                resetQuestionForm();
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleAddQuestion}>
              {editingQuestion ? 'Update' : 'Add'} Question
            </Button>
          </div>
        </div>
      </Modal>
    </DashboardLayout>
  );
}
