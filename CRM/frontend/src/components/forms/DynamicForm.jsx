import React, { useState, useEffect, useCallback } from 'react';
import {
  PlusIcon,
  TrashIcon,
  CheckCircleIcon,
  ArrowUpTrayIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  UserIcon,
} from '@heroicons/react/24/outline';
import Input, { TextArea, Select, Checkbox } from '../common/Input';
import Button from '../common/Button';
import Card from '../common/Card';

/**
 * DynamicForm - Renders forms with sections, repeatable sections, and conditional logic
 *
 * Features:
 * - Multi-section forms with step navigation
 * - Repeatable sections (e.g., add multiple directors)
 * - File uploads
 * - Conditional question display
 * - Form validation
 * - Draft saving support
 */
export default function DynamicForm({
  form,
  onSubmit,
  onSaveDraft,
  initialData = {},
  isLoading = false,
  submitButtonText = 'Submit',
}) {
  const [currentSection, setCurrentSection] = useState(1);
  const [formData, setFormData] = useState({});
  const [repeatableSections, setRepeatableSections] = useState({});
  const [errors, setErrors] = useState({});
  const [files, setFiles] = useState({});
  const [collapsedInstances, setCollapsedInstances] = useState({});

  // Group questions by section
  const sections = groupQuestionsBySection(form?.questions || []);
  const allSectionNumbers = Object.keys(sections).map(Number).sort((a, b) => a - b);

  // Check if a section should be visible based on conditional logic
  const isSectionVisible = useCallback((sectionNum) => {
    const sectionQuestions = sections[sectionNum] || [];
    if (sectionQuestions.length === 0) return false;

    const firstQuestion = sectionQuestions[0];
    const conditionalRule = firstQuestion.validation_rules?.section_conditional;

    if (!conditionalRule) return true;

    // Find the question this section depends on
    const conditionalQuestion = conditionalRule.conditional_question;
    const conditionalValue = conditionalRule.conditional_value;

    // Search for the answer to the conditional question
    for (const [key, value] of Object.entries(formData)) {
      // Find the question by checking all sections for the conditional question text
      for (const secNum of allSectionNumbers) {
        const questions = sections[secNum] || [];
        for (const q of questions) {
          if (q.question_text === conditionalQuestion && formData[q.id] !== undefined) {
            return formData[q.id] === conditionalValue;
          }
        }
      }
    }

    return true; // Show by default if condition can't be evaluated
  }, [formData, sections, allSectionNumbers]);

  // Filter visible sections
  const sectionNumbers = allSectionNumbers.filter(isSectionVisible);
  const totalSections = sectionNumbers.length;

  // Initialize form data and repeatable sections
  useEffect(() => {
    if (form?.questions) {
      const initial = { ...initialData };
      const repeatables = {};

      form.questions.forEach((q) => {
        if (q.is_section_repeatable && q.section_group) {
          if (!repeatables[q.section_group]) {
            repeatables[q.section_group] = {
              min: q.min_section_repeats || 1,
              max: q.max_section_repeats || 10,
              instances: [{ id: 1 }], // Start with one instance
            };
          }
        }
      });

      setFormData(initial);
      setRepeatableSections(repeatables);
    }
  }, [form, initialData]);

  // Get value for a question (handles repeatable sections)
  const getValue = (questionId, instanceId = null) => {
    const key = instanceId ? `${questionId}_${instanceId}` : String(questionId);
    return formData[key] || '';
  };

  // Set value for a question
  const handleChange = (questionId, value, instanceId = null) => {
    const key = instanceId ? `${questionId}_${instanceId}` : String(questionId);
    setFormData((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => ({ ...prev, [key]: '' }));
  };

  // Handle file upload
  const handleFileChange = (questionId, file, instanceId = null) => {
    const key = instanceId ? `${questionId}_${instanceId}` : String(questionId);
    setFiles((prev) => ({ ...prev, [key]: file }));
    setFormData((prev) => ({ ...prev, [key]: file?.name || '' }));
  };

  // Add instance to repeatable section
  const addRepeatableInstance = (groupName) => {
    setRepeatableSections((prev) => {
      const group = prev[groupName];
      if (group.instances.length >= group.max) return prev;

      const newId = Math.max(...group.instances.map((i) => i.id)) + 1;
      return {
        ...prev,
        [groupName]: {
          ...group,
          instances: [...group.instances, { id: newId }],
        },
      };
    });
  };

  // Remove instance from repeatable section
  const removeRepeatableInstance = (groupName, instanceId) => {
    setRepeatableSections((prev) => {
      const group = prev[groupName];
      if (group.instances.length <= group.min) return prev;

      return {
        ...prev,
        [groupName]: {
          ...group,
          instances: group.instances.filter((i) => i.id !== instanceId),
        },
      };
    });

    // Clean up form data for removed instance
    setFormData((prev) => {
      const cleaned = { ...prev };
      Object.keys(cleaned).forEach((key) => {
        if (key.endsWith(`_${instanceId}`)) {
          delete cleaned[key];
        }
      });
      return cleaned;
    });

    // Clean up collapsed state for removed instance
    setCollapsedInstances((prev) => {
      const cleaned = { ...prev };
      delete cleaned[`${groupName}_${instanceId}`];
      return cleaned;
    });
  };

  // Toggle collapse state for a repeatable section instance
  const toggleCollapse = (groupName, instanceId) => {
    const key = `${groupName}_${instanceId}`;
    setCollapsedInstances((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  // Check if an instance is collapsed
  const isInstanceCollapsed = (groupName, instanceId) => {
    return collapsedInstances[`${groupName}_${instanceId}`] || false;
  };

  // Get a summary of filled fields for a collapsed card
  const getInstanceSummary = (sectionQuestions, instanceId) => {
    const filledFields = [];
    for (const q of sectionQuestions) {
      if (q.validation_rules?.type === 'section_header') continue;
      const key = `${q.id}_${instanceId}`;
      const value = formData[key];
      if (value && q.question_text.toLowerCase().includes('name')) {
        filledFields.push(value);
        break; // Just get the name for summary
      }
    }
    return filledFields.length > 0 ? filledFields[0] : null;
  };

  // Validate current section
  const validateSection = (sectionNum) => {
    // Skip validation for hidden sections
    if (!isSectionVisible(sectionNum)) return true;

    const sectionQuestions = sections[sectionNum] || [];
    const newErrors = {};
    let isValid = true;

    sectionQuestions.forEach((question) => {
      if (question.validation_rules?.type === 'section_header') return;

      if (question.is_section_repeatable && question.section_group) {
        const group = repeatableSections[question.section_group];
        if (group) {
          group.instances.forEach((instance) => {
            const key = `${question.id}_${instance.id}`;
            const value = formData[key];
            if (question.is_required && !value) {
              newErrors[key] = `${question.question_text} is required`;
              isValid = false;
            }
          });
        }
      } else {
        const value = formData[question.id];
        if (question.is_required && !value) {
          newErrors[question.id] = `${question.question_text} is required`;
          isValid = false;
        }
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  // Navigate to next section
  const handleNext = () => {
    if (validateSection(currentSection)) {
      setCurrentSection((prev) => Math.min(prev + 1, totalSections));
    }
  };

  // Navigate to previous section
  const handleBack = () => {
    setCurrentSection((prev) => Math.max(prev - 1, 1));
  };

  // Handle form submission
  const handleSubmit = () => {
    if (!validateSection(currentSection)) return;

    // Build submission data
    const submissionData = {
      formData,
      files,
      repeatableSections,
    };

    onSubmit?.(submissionData);
  };

  // Render a single question field
  const renderQuestion = (question, instanceId = null) => {
    const key = instanceId ? `${question.id}_${instanceId}` : String(question.id);
    const value = getValue(question.id, instanceId);
    const error = errors[key];

    // Skip section headers
    if (question.validation_rules?.type === 'section_header') {
      return null;
    }

    const commonProps = {
      key: key,
      label: question.question_text,
      required: question.is_required,
      helpText: question.help_text,
      placeholder: question.placeholder,
      error: error,
    };

    switch (question.question_type) {
      case 'text':
      case 'email':
      case 'phone':
        return (
          <Input
            {...commonProps}
            type={question.question_type === 'phone' ? 'tel' : question.question_type}
            value={value}
            onChange={(e) => handleChange(question.id, e.target.value, instanceId)}
          />
        );

      case 'number':
        return (
          <Input
            {...commonProps}
            type="number"
            value={value}
            onChange={(e) => handleChange(question.id, e.target.value, instanceId)}
            min={question.validation_rules?.min}
            max={question.validation_rules?.max}
          />
        );

      case 'textarea':
        return (
          <TextArea
            {...commonProps}
            value={value}
            onChange={(e) => handleChange(question.id, e.target.value, instanceId)}
            rows={3}
          />
        );

      case 'date':
        return (
          <Input
            {...commonProps}
            type="date"
            value={value}
            onChange={(e) => handleChange(question.id, e.target.value, instanceId)}
          />
        );

      case 'select':
        return (
          <Select
            {...commonProps}
            value={value}
            onChange={(e) => handleChange(question.id, e.target.value, instanceId)}
            options={[
              { value: '', label: 'Select...' },
              ...(question.options || []).map((opt) => ({
                value: typeof opt === 'string' ? opt : opt.value,
                label: typeof opt === 'string' ? opt : opt.label,
              })),
            ]}
          />
        );

      case 'radio':
        return (
          <div key={key} className="space-y-2">
            <label className="label">
              {question.question_text}
              {question.is_required && <span className="text-red-500 ml-1">*</span>}
            </label>
            {question.help_text && (
              <p className="text-xs text-gray-500">{question.help_text}</p>
            )}
            <div className="space-y-2">
              {(question.options || []).map((option) => (
                <label
                  key={option}
                  className="flex items-center space-x-2 cursor-pointer"
                >
                  <input
                    type="radio"
                    name={key}
                    value={option}
                    checked={value === option}
                    onChange={() => handleChange(question.id, option, instanceId)}
                    className="h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">{option}</span>
                </label>
              ))}
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
          </div>
        );

      case 'multiselect':
      case 'checkbox':
        const selectedValues = Array.isArray(value) ? value : value ? [value] : [];
        return (
          <div key={key} className="space-y-2">
            <label className="label">
              {question.question_text}
              {question.is_required && <span className="text-red-500 ml-1">*</span>}
            </label>
            {question.help_text && (
              <p className="text-xs text-gray-500">{question.help_text}</p>
            )}
            <div className="space-y-2">
              {(question.options || []).map((option) => (
                <label
                  key={option}
                  className="flex items-center space-x-2 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedValues.includes(option)}
                    onChange={(e) => {
                      const newValues = e.target.checked
                        ? [...selectedValues, option]
                        : selectedValues.filter((v) => v !== option);
                      handleChange(question.id, newValues, instanceId);
                    }}
                    className="h-4 w-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700">{option}</span>
                </label>
              ))}
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
          </div>
        );

      case 'file':
        const fileKey = key;
        const uploadedFile = files[fileKey];
        return (
          <div key={key} className="space-y-2">
            <label className="label">
              {question.question_text}
              {question.is_required && <span className="text-red-500 ml-1">*</span>}
            </label>
            {question.help_text && (
              <p className="text-xs text-gray-500">{question.help_text}</p>
            )}
            {uploadedFile ? (
              <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center">
                  <CheckCircleIcon className="h-5 w-5 text-green-600 mr-2" />
                  <span className="text-sm text-green-700">{uploadedFile.name}</span>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setFiles((prev) => ({ ...prev, [fileKey]: null }));
                    setFormData((prev) => ({ ...prev, [key]: '' }));
                  }}
                  className="text-gray-400 hover:text-red-500"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-primary-400 transition-colors">
                <input
                  type="file"
                  id={`file_${fileKey}`}
                  accept=".pdf,.png,.jpg,.jpeg,.doc,.docx"
                  onChange={(e) => handleFileChange(question.id, e.target.files[0], instanceId)}
                  className="hidden"
                />
                <label htmlFor={`file_${fileKey}`} className="cursor-pointer">
                  <div className="flex flex-col items-center">
                    <ArrowUpTrayIcon className="h-8 w-8 text-gray-400 mb-2" />
                    <span className="text-sm text-gray-600">Click to upload</span>
                    <span className="text-xs text-gray-400 mt-1">
                      PDF, PNG, JPG, DOC up to 16MB
                    </span>
                  </div>
                </label>
              </div>
            )}
            {error && <p className="text-sm text-red-600">{error}</p>}
          </div>
        );

      default:
        return (
          <Input
            {...commonProps}
            value={value}
            onChange={(e) => handleChange(question.id, e.target.value, instanceId)}
          />
        );
    }
  };

  // Render a section with its questions
  const renderSection = (sectionNum) => {
    const sectionQuestions = sections[sectionNum] || [];
    if (sectionQuestions.length === 0) return null;

    const firstQuestion = sectionQuestions[0];
    const sectionTitle = firstQuestion.section_title;
    const sectionDescription = firstQuestion.section_description;
    const isRepeatable = firstQuestion.is_section_repeatable;
    const sectionGroup = firstQuestion.section_group;

    // Check if this is a section header only
    const isSectionHeader = firstQuestion.validation_rules?.type === 'section_header';

    if (isSectionHeader) {
      return (
        <div className="space-y-4">
          {sectionTitle && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900">{sectionTitle}</h2>
              {sectionDescription && (
                <p className="text-sm text-gray-500 mt-1">{sectionDescription}</p>
              )}
            </div>
          )}
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm text-blue-700">{sectionDescription || 'Continue to the next section.'}</p>
          </div>
        </div>
      );
    }

    if (isRepeatable && sectionGroup) {
      const group = repeatableSections[sectionGroup];
      if (!group) return null;

      // Determine icon and color based on section type
      const isDirector = sectionGroup.toLowerCase().includes('director');
      const isMember = sectionGroup.toLowerCase().includes('member');
      const isShareholder = sectionGroup.toLowerCase().includes('shareholder');

      const getCardColors = (idx) => {
        const colors = [
          { bg: 'bg-blue-50', border: 'border-blue-200', header: 'bg-blue-100', icon: 'text-blue-600' },
          { bg: 'bg-green-50', border: 'border-green-200', header: 'bg-green-100', icon: 'text-green-600' },
          { bg: 'bg-purple-50', border: 'border-purple-200', header: 'bg-purple-100', icon: 'text-purple-600' },
          { bg: 'bg-amber-50', border: 'border-amber-200', header: 'bg-amber-100', icon: 'text-amber-600' },
          { bg: 'bg-rose-50', border: 'border-rose-200', header: 'bg-rose-100', icon: 'text-rose-600' },
          { bg: 'bg-cyan-50', border: 'border-cyan-200', header: 'bg-cyan-100', icon: 'text-cyan-600' },
        ];
        return colors[idx % colors.length];
      };

      const getEntityLabel = () => {
        if (isDirector) return 'Director';
        if (isMember) return 'Member';
        if (isShareholder) return 'Shareholder';
        return sectionTitle?.replace(' Details', '') || 'Entry';
      };

      return (
        <div className="space-y-6">
          {sectionTitle && (
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900">{sectionTitle}</h2>
              {sectionDescription && (
                <p className="text-sm text-gray-500 mt-1">{sectionDescription}</p>
              )}
            </div>
          )}

          {/* Cards Grid for multiple instances */}
          <div className="grid grid-cols-1 gap-4">
            {group.instances.map((instance, idx) => {
              const isCollapsed = isInstanceCollapsed(sectionGroup, instance.id);
              const summary = getInstanceSummary(sectionQuestions, instance.id);
              const colors = getCardColors(idx);
              const entityLabel = getEntityLabel();

              return (
                <div
                  key={instance.id}
                  className={`rounded-xl border-2 ${colors.border} overflow-hidden shadow-sm hover:shadow-md transition-shadow`}
                >
                  {/* Card Header - Always visible */}
                  <div
                    className={`${colors.header} px-4 py-3 flex items-center justify-between cursor-pointer`}
                    onClick={() => toggleCollapse(sectionGroup, instance.id)}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-full ${colors.bg}`}>
                        <UserIcon className={`h-5 w-5 ${colors.icon}`} />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-800">
                          {entityLabel} {idx + 1}
                        </h3>
                        {isCollapsed && summary && (
                          <p className="text-sm text-gray-600">{summary}</p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {group.instances.length > group.min && (
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            removeRepeatableInstance(sectionGroup, instance.id);
                          }}
                          className="p-1.5 rounded-full hover:bg-red-100 text-gray-400 hover:text-red-600 transition-colors"
                          title={`Remove ${entityLabel} ${idx + 1}`}
                        >
                          <TrashIcon className="h-5 w-5" />
                        </button>
                      )}
                      <button
                        type="button"
                        className={`p-1.5 rounded-full ${colors.bg} ${colors.icon} transition-transform duration-200`}
                      >
                        {isCollapsed ? (
                          <ChevronDownIcon className="h-5 w-5" />
                        ) : (
                          <ChevronUpIcon className="h-5 w-5" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Card Body - Collapsible */}
                  <div
                    className={`transition-all duration-300 ease-in-out ${
                      isCollapsed ? 'max-h-0 overflow-hidden' : 'max-h-[2000px]'
                    }`}
                  >
                    <div className={`${colors.bg} px-4 py-4`}>
                      <div className="space-y-4">
                        {sectionQuestions.map((q) => renderQuestion(q, instance.id))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Add Another Button */}
          {group.instances.length < group.max && (
            <button
              type="button"
              onClick={() => addRepeatableInstance(sectionGroup)}
              className="w-full py-4 border-2 border-dashed border-gray-300 rounded-xl text-gray-600 hover:border-primary-400 hover:text-primary-600 hover:bg-primary-50 transition-all flex items-center justify-center space-x-2"
            >
              <PlusIcon className="h-5 w-5" />
              <span className="font-medium">Add Another {getEntityLabel()}</span>
            </button>
          )}
        </div>
      );
    }

    // Regular section
    return (
      <div className="space-y-4">
        {sectionTitle && (
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-900">{sectionTitle}</h2>
            {sectionDescription && (
              <p className="text-sm text-gray-500 mt-1">{sectionDescription}</p>
            )}
          </div>
        )}
        {sectionQuestions.map((q) => renderQuestion(q))}
      </div>
    );
  };

  if (!form) {
    return <div className="text-gray-500">No form available</div>;
  }

  const currentSectionNum = sectionNumbers[currentSection - 1];

  return (
    <div className="space-y-6">
      {/* Progress Steps */}
      <div className="flex items-center justify-center overflow-x-auto pb-2">
        {sectionNumbers.map((secNum, idx) => {
          const secQuestions = sections[secNum] || [];
          const secTitle = secQuestions[0]?.section_title || `Section ${secNum}`;
          const stepNum = idx + 1;

          return (
            <React.Fragment key={secNum}>
              <div className="flex flex-col items-center min-w-[60px]">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors cursor-pointer ${
                    currentSection >= stepNum
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                  onClick={() => currentSection > stepNum && setCurrentSection(stepNum)}
                >
                  {currentSection > stepNum ? (
                    <CheckCircleIcon className="h-5 w-5" />
                  ) : (
                    stepNum
                  )}
                </div>
                <span className="text-xs text-gray-500 mt-1 text-center truncate max-w-[80px]">
                  {secTitle}
                </span>
              </div>
              {idx < sectionNumbers.length - 1 && (
                <div
                  className={`w-8 h-0.5 mx-1 ${
                    currentSection > stepNum ? 'bg-primary-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* Current Section Content */}
      <Card className="p-6">{renderSection(currentSectionNum)}</Card>

      {/* Navigation Buttons */}
      <div className="flex justify-between pt-4">
        {currentSection > 1 ? (
          <Button variant="secondary" onClick={handleBack}>
            Back
          </Button>
        ) : (
          <div />
        )}

        <div className="flex gap-2">
          {onSaveDraft && (
            <Button variant="secondary" onClick={() => onSaveDraft({ formData, files })}>
              Save Draft
            </Button>
          )}

          {currentSection < totalSections ? (
            <Button onClick={handleNext}>Continue</Button>
          ) : (
            <Button onClick={handleSubmit} loading={isLoading}>
              {submitButtonText}
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Helper function to group questions by section number
 */
function groupQuestionsBySection(questions) {
  const sections = {};
  questions.forEach((q) => {
    const secNum = q.section_number || 1;
    if (!sections[secNum]) {
      sections[secNum] = [];
    }
    sections[secNum].push(q);
  });
  return sections;
}
