import React from 'react';
import Input, { TextArea, Select, Checkbox } from '../../common/Input';

export default function FormRenderer({ form, responses, onChange }) {
  const handleChange = (questionId, value) => {
    onChange({
      ...responses,
      [questionId]: value,
    });
  };

  const handleMultiSelectChange = (questionId, option, checked) => {
    const current = responses[questionId] || [];
    const updated = checked
      ? [...current, option]
      : current.filter((o) => o !== option);
    handleChange(questionId, updated);
  };

  const renderQuestion = (question) => {
    const value = responses[question.id];

    switch (question.question_type) {
      case 'text':
        return (
          <Input
            value={value || ''}
            onChange={(e) => handleChange(question.id, e.target.value)}
            placeholder={question.placeholder}
            required={question.is_required}
          />
        );

      case 'email':
        return (
          <Input
            type="email"
            value={value || ''}
            onChange={(e) => handleChange(question.id, e.target.value)}
            placeholder={question.placeholder}
            required={question.is_required}
          />
        );

      case 'phone':
        return (
          <Input
            type="tel"
            value={value || ''}
            onChange={(e) => handleChange(question.id, e.target.value)}
            placeholder={question.placeholder}
            required={question.is_required}
          />
        );

      case 'number':
        return (
          <Input
            type="number"
            value={value || ''}
            onChange={(e) => handleChange(question.id, e.target.value)}
            placeholder={question.placeholder}
            required={question.is_required}
          />
        );

      case 'textarea':
        return (
          <TextArea
            value={value || ''}
            onChange={(e) => handleChange(question.id, e.target.value)}
            placeholder={question.placeholder}
            required={question.is_required}
            rows={4}
          />
        );

      case 'date':
        return (
          <Input
            type="date"
            value={value || ''}
            onChange={(e) => handleChange(question.id, e.target.value)}
            required={question.is_required}
          />
        );

      case 'select':
        return (
          <Select
            value={value || ''}
            onChange={(e) => handleChange(question.id, e.target.value)}
            options={[
              { value: '', label: 'Select an option' },
              ...(question.options || []).map((opt) => ({
                value: opt,
                label: opt,
              })),
            ]}
            required={question.is_required}
          />
        );

      case 'radio':
        return (
          <div className="space-y-2">
            {(question.options || []).map((option, idx) => (
              <label key={idx} className="flex items-center">
                <input
                  type="radio"
                  name={`question_${question.id}`}
                  value={option}
                  checked={value === option}
                  onChange={(e) => handleChange(question.id, e.target.value)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300"
                  required={question.is_required}
                />
                <span className="ml-2 text-sm text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        );

      case 'checkbox':
        return (
          <div className="space-y-2">
            {(question.options || []).map((option, idx) => (
              <Checkbox
                key={idx}
                label={option}
                checked={(value || []).includes(option)}
                onChange={(e) =>
                  handleMultiSelectChange(question.id, option, e.target.checked)
                }
              />
            ))}
          </div>
        );

      case 'multiselect':
        return (
          <div className="space-y-2">
            {(question.options || []).map((option, idx) => (
              <Checkbox
                key={idx}
                label={option}
                checked={(value || []).includes(option)}
                onChange={(e) =>
                  handleMultiSelectChange(question.id, option, e.target.checked)
                }
              />
            ))}
          </div>
        );

      case 'file':
        return (
          <Input
            type="file"
            onChange={(e) => handleChange(question.id, e.target.files[0]?.name)}
            required={question.is_required}
          />
        );

      default:
        return (
          <Input
            value={value || ''}
            onChange={(e) => handleChange(question.id, e.target.value)}
            placeholder={question.placeholder}
            required={question.is_required}
          />
        );
    }
  };

  if (!form?.questions || form.questions.length === 0) {
    return <p className="text-gray-500">No questions in this form</p>;
  }

  return (
    <div className="space-y-6">
      {form.questions.map((question) => (
        <div key={question.id}>
          <label className="label">
            {question.question_text}
            {question.is_required && <span className="text-red-500 ml-1">*</span>}
          </label>
          {question.help_text && (
            <p className="text-sm text-gray-400 mb-2">{question.help_text}</p>
          )}
          {renderQuestion(question)}
        </div>
      ))}
    </div>
  );
}
