import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import Input, { TextArea, Select, Checkbox } from '../../components/common/Input';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import { userAPI, servicesAPI, documentsAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';
import {
  CheckCircleIcon,
  DocumentIcon,
  ArrowUpTrayIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';

export default function Onboarding() {
  const navigate = useNavigate();
  const { user, updateUser } = useAuthStore();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [services, setServices] = useState([]);

  // Check if user is admin, senior_accountant, or accountant - they only need password reset
  const isStaffUser = user?.role === 'admin' || user?.role === 'senior_accountant' || user?.role === 'accountant';
  const isClient = user?.role === 'user';

  // Debug log to verify user role
  useEffect(() => {
    console.log('Onboarding - User data:', user);
    console.log('Onboarding - User role:', user?.role);
    console.log('Onboarding - isStaffUser:', isStaffUser);
  }, [user, isStaffUser]);

  // Form data
  const [formData, setFormData] = useState({
    // Step 1: Password
    new_password: '',
    confirm_password: '',
    // Step 2: Personal Information
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone: user?.phone || '',
    personal_email: '',
    address: user?.address || '',
    visa_status: '',
    // Step 3: Additional Details
    tfn: '',
    date_of_birth: '',
    occupation: '',
    // Step 4: Bank Account Details
    bsb: '',
    bank_account_number: '',
    bank_account_holder_name: '',
    // Step 5: Terms
    terms_accepted: false,
    // Service selection (optional)
    service_ids: [],
  });

  // Document uploads
  const [documents, setDocuments] = useState({
    passport: null,
    bank_statement: null,
    driving_licence: null,
  });
  const [uploadedDocUrls, setUploadedDocUrls] = useState({
    passport_url: '',
    bank_statement_url: '',
    driving_licence_url: '',
  });
  const [uploadingDoc, setUploadingDoc] = useState(null);

  const [errors, setErrors] = useState({});
  const [serverError, setServerError] = useState('');

  useEffect(() => {
    servicesAPI.list().then((response) => {
      setServices(response.data.data.services || []);
    });
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    setErrors((prev) => ({ ...prev, [name]: '' }));
  };

  const handleServiceToggle = (serviceId) => {
    setFormData((prev) => ({
      ...prev,
      service_ids: prev.service_ids.includes(serviceId)
        ? prev.service_ids.filter((id) => id !== serviceId)
        : [...prev.service_ids, serviceId],
    }));
  };

  const handleDocumentUpload = async (docType, file) => {
    if (!file) return;

    setUploadingDoc(docType);
    try {
      const response = await documentsAPI.upload(file, null, docType, `${docType} for onboarding`);
      const docUrl = response.data.document?.id || response.data.document?.file_url;

      setDocuments((prev) => ({ ...prev, [docType]: file }));
      setUploadedDocUrls((prev) => ({
        ...prev,
        [`${docType}_url`]: docUrl,
      }));
      toast.success(`${docType.replace('_', ' ')} uploaded successfully`);
    } catch (error) {
      toast.error(`Failed to upload ${docType.replace('_', ' ')}`);
    } finally {
      setUploadingDoc(null);
    }
  };

  const removeDocument = (docType) => {
    setDocuments((prev) => ({ ...prev, [docType]: null }));
    setUploadedDocUrls((prev) => ({ ...prev, [`${docType}_url`]: '' }));
  };

  const validateStep = () => {
    const newErrors = {};

    if (step === 1) {
      if (!formData.new_password) {
        newErrors.new_password = 'Password is required';
      } else if (formData.new_password.length < 8) {
        newErrors.new_password = 'Password must be at least 8 characters';
      } else if (!/[A-Z]/.test(formData.new_password)) {
        newErrors.new_password = 'Password must contain an uppercase letter';
      } else if (!/[a-z]/.test(formData.new_password)) {
        newErrors.new_password = 'Password must contain a lowercase letter';
      } else if (!/[0-9]/.test(formData.new_password)) {
        newErrors.new_password = 'Password must contain a number';
      }
      if (formData.new_password !== formData.confirm_password) {
        newErrors.confirm_password = 'Passwords do not match';
      }
    }

    if (step === 2) {
      if (!formData.first_name) newErrors.first_name = 'First name is required';
      if (!formData.last_name) newErrors.last_name = 'Last name is required';
      if (!formData.phone) newErrors.phone = 'Mobile number is required';
      if (!formData.address) newErrors.address = 'Address is required';
      // Visa status only required for clients, not for staff users
      if (!isStaffUser && !formData.visa_status) newErrors.visa_status = 'Visa status is required';
    }

    if (step === 3) {
      if (!formData.tfn) newErrors.tfn = 'Tax File Number is required';
      if (!formData.date_of_birth) newErrors.date_of_birth = 'Date of birth is required';
      if (!formData.occupation) newErrors.occupation = 'Occupation is required';
    }

    if (step === 4) {
      if (!formData.bsb) newErrors.bsb = 'BSB is required';
      if (!formData.bank_account_number) newErrors.bank_account_number = 'Account number is required';
      if (!formData.bank_account_holder_name) newErrors.bank_account_holder_name = 'Account holder name is required';
    }

    if (step === 5) {
      if (!formData.terms_accepted) {
        newErrors.terms_accepted = 'You must accept the terms and conditions';
      }
    }

    if (step === 6) {
      if (!documents.passport && !uploadedDocUrls.passport_url) {
        newErrors.passport = 'Passport copy is required';
      }
      if (!documents.bank_statement && !uploadedDocUrls.bank_statement_url) {
        newErrors.bank_statement = 'Bank statement is required';
      }
      if (!documents.driving_licence && !uploadedDocUrls.driving_licence_url) {
        newErrors.driving_licence = 'Driving licence or photo ID is required';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep()) {
      setServerError('');
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    setServerError('');
    setStep(step - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep()) return;

    setIsLoading(true);
    setServerError('');

    try {
      // Staff users (admin/accountant) only need password and personal details
      const submissionData = isStaffUser
        ? {
            new_password: formData.new_password,
            confirm_password: formData.confirm_password,
            first_name: formData.first_name,
            last_name: formData.last_name,
            phone: formData.phone,
            personal_email: formData.personal_email,
            address: formData.address,
            terms_accepted: true, // Staff users implicitly accept terms
          }
        : {
            ...formData,
            ...uploadedDocUrls,
          };

      const response = await userAPI.completeOnboarding(submissionData);
      updateUser(response.data.data.user);

      toast.success(isStaffUser ? 'Profile setup completed!' : 'Onboarding completed successfully!');
      navigate('/dashboard');
    } catch (error) {
      const errMsg = error.response?.data?.error || 'Something went wrong';
      const errCode = errMsg.toLowerCase();
      setServerError(errMsg);

      // Map backend errors to the relevant step and field
      if (errCode.includes('password')) {
        setStep(1);
        setErrors(prev => ({
          ...prev,
          new_password: errMsg,
        }));
      } else if (errCode.includes('terms')) {
        if (!isStaffUser) setStep(5);
      } else {
        toast.error(errMsg);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Define steps based on user role - staff users only need password and personal info
  const steps = isStaffUser
    ? [
        { number: 1, title: 'Password' },
        { number: 2, title: 'Personal Info' },
      ]
    : [
        { number: 1, title: 'Password' },
        { number: 2, title: 'Personal Info' },
        { number: 3, title: 'Details' },
        { number: 4, title: 'Bank' },
        { number: 5, title: 'Terms' },
        { number: 6, title: 'Documents' },
      ];

  const totalSteps = steps.length;

  const visaOptions = [
    { value: '', label: 'Select visa status' },
    { value: 'citizen', label: 'Australian Citizen' },
    { value: 'permanent_resident', label: 'Permanent Resident' },
    { value: 'temporary_resident', label: 'Temporary Resident' },
    { value: 'working_holiday', label: 'Working Holiday' },
    { value: 'student', label: 'Student' },
    { value: 'other', label: 'Other' },
  ];

  const DocumentUploadField = ({ label, docType, required, helpText }) => (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {helpText && <p className="text-xs text-gray-500">{helpText}</p>}

      {documents[docType] || uploadedDocUrls[`${docType}_url`] ? (
        <div className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center">
            <CheckCircleIcon className="h-5 w-5 text-green-600 mr-2" />
            <span className="text-sm text-green-700">
              {documents[docType]?.name || 'Document uploaded'}
            </span>
          </div>
          <button
            type="button"
            onClick={() => removeDocument(docType)}
            className="text-gray-400 hover:text-red-500"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
      ) : (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-primary-400 transition-colors">
          <input
            type="file"
            id={`doc_${docType}`}
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={(e) => handleDocumentUpload(docType, e.target.files[0])}
            className="hidden"
            disabled={uploadingDoc === docType}
          />
          <label htmlFor={`doc_${docType}`} className="cursor-pointer">
            {uploadingDoc === docType ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600 mr-2" />
                <span className="text-sm text-gray-600">Uploading...</span>
              </div>
            ) : (
              <div className="flex flex-col items-center">
                <ArrowUpTrayIcon className="h-8 w-8 text-gray-400 mb-2" />
                <span className="text-sm text-gray-600">Click to upload</span>
                <span className="text-xs text-gray-400 mt-1">PDF, PNG, JPG up to 16MB</span>
              </div>
            )}
          </label>
        </div>
      )}
      {errors[docType] && <p className="text-sm text-red-600">{errors[docType]}</p>}
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            {isStaffUser ? 'Complete Your Account Setup' : 'Complete Your Profile'}
          </h1>
          <p className="text-gray-500 mt-2">
            {isStaffUser
              ? 'Please set a password and add your personal details'
              : 'Please fill in your information to get started with our services'}
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center mb-8 overflow-x-auto pb-2">
          {steps.map((s, i) => (
            <React.Fragment key={s.number}>
              <div className="flex flex-col items-center min-w-[60px]">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${
                    step >= s.number
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-500'
                  }`}
                >
                  {step > s.number ? (
                    <CheckCircleIcon className="h-5 w-5" />
                  ) : (
                    s.number
                  )}
                </div>
                <span className="text-xs text-gray-500 mt-1 text-center">{s.title}</span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className={`w-8 h-0.5 mx-1 ${
                    step > s.number ? 'bg-primary-600' : 'bg-gray-200'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>

        <Card className="p-6">
          {/* Server Error Banner */}
          {serverError && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200">
              <p className="text-sm text-red-700 font-medium">{serverError}</p>
            </div>
          )}

          {/* Step 1: Set Password */}
          {step === 1 && (
            <div className="space-y-4">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Set Your Password</h2>
                <p className="text-sm text-gray-500 mt-1">
                  Create a secure password for your account
                </p>
              </div>

              <Input
                label="New Password"
                type="password"
                name="new_password"
                value={formData.new_password}
                onChange={handleChange}
                placeholder="Enter new password"
                error={errors.new_password}
                required
              />

              <Input
                label="Confirm Password"
                type="password"
                name="confirm_password"
                value={formData.confirm_password}
                onChange={handleChange}
                placeholder="Confirm new password"
                error={errors.confirm_password}
                required
              />

              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-blue-700 font-medium mb-2">Password requirements:</p>
                <ul className="text-sm text-blue-600 space-y-1">
                  <li className={formData.new_password.length >= 8 ? 'text-green-600' : ''}>
                    - At least 8 characters
                  </li>
                  <li className={/[A-Z]/.test(formData.new_password) ? 'text-green-600' : ''}>
                    - One uppercase letter
                  </li>
                  <li className={/[a-z]/.test(formData.new_password) ? 'text-green-600' : ''}>
                    - One lowercase letter
                  </li>
                  <li className={/[0-9]/.test(formData.new_password) ? 'text-green-600' : ''}>
                    - One number
                  </li>
                </ul>
              </div>
            </div>
          )}

          {/* Step 2: Personal Information */}
          {step === 2 && (
            <div className="space-y-4">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Personal Information</h2>
                <p className="text-sm text-gray-500 mt-1">
                  {isStaffUser
                    ? 'Please provide your contact details'
                    : 'Name should match with your photo ID and ATO records'}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="First Name"
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  placeholder="John"
                  error={errors.first_name}
                  required
                />

                <Input
                  label="Last / Family Name"
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  placeholder="Smith"
                  error={errors.last_name}
                  required
                />
              </div>

              <Input
                label="Mobile Number"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+61 400 123 456 or +1 555 123 4567"
                helpText="Enter your mobile number with country code (e.g., +61 for Australia, +1 for USA, +91 for India)"
                error={errors.phone}
                required
              />

              <Input
                label="Personal Email"
                type="email"
                name="personal_email"
                value={formData.personal_email}
                onChange={handleChange}
                placeholder="john@personal.com"
                helpText="Please provide your personal email (not official) which you use frequently"
              />

              <TextArea
                label="Current Residential Address"
                name="address"
                value={formData.address}
                onChange={handleChange}
                placeholder="123 Main Street, Sydney NSW 2000"
                rows={2}
                error={errors.address}
                required
              />

              {/* Visa status only shown for clients, not staff users */}
              {!isStaffUser && (
                <Select
                  label="Current Visa Status"
                  name="visa_status"
                  value={formData.visa_status}
                  onChange={handleChange}
                  options={visaOptions}
                  error={errors.visa_status}
                  required
                />
              )}
            </div>
          )}

          {/* Step 3: Additional Details */}
          {step === 3 && (
            <div className="space-y-4">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Additional Details</h2>
                <p className="text-sm text-gray-500 mt-1">
                  This information is required for ATO compliance
                </p>
              </div>

              <Input
                label="Tax File Number (TFN)"
                name="tfn"
                value={formData.tfn}
                onChange={handleChange}
                placeholder="123 456 789"
                helpText="Please fill in your TFN carefully. Any error will not allow us to add you to our ATO portal."
                error={errors.tfn}
                required
              />

              <Input
                label="Date of Birth"
                type="date"
                name="date_of_birth"
                value={formData.date_of_birth}
                onChange={handleChange}
                helpText="Please fill in your DOB carefully. Any error will not allow us to add you to our ATO portal."
                error={errors.date_of_birth}
                required
              />

              <Input
                label="Occupation"
                name="occupation"
                value={formData.occupation}
                onChange={handleChange}
                placeholder="Software Engineer"
                error={errors.occupation}
                required
              />
            </div>
          )}

          {/* Step 4: Bank Account Details */}
          {step === 4 && (
            <div className="space-y-4">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Bank Account Details</h2>
                <p className="text-sm text-gray-500 mt-1">
                  These details are required to receive tax refund from the ATO (if applicable).
                  Tax refund can only be transferred to the Taxpayer's bank account for security reasons.
                </p>
              </div>

              <div className="bg-amber-50 p-4 rounded-lg mb-4">
                <p className="text-sm text-amber-700">
                  A bank statement will be requested to verify the details.
                </p>
              </div>

              <Input
                label="BSB"
                name="bsb"
                value={formData.bsb}
                onChange={handleChange}
                placeholder="123-456"
                error={errors.bsb}
                required
              />

              <Input
                label="Account Number"
                name="bank_account_number"
                value={formData.bank_account_number}
                onChange={handleChange}
                placeholder="12345678"
                error={errors.bank_account_number}
                required
              />

              <Input
                label="Account Holder Name"
                name="bank_account_holder_name"
                value={formData.bank_account_holder_name}
                onChange={handleChange}
                placeholder="John Smith"
                error={errors.bank_account_holder_name}
                required
              />
            </div>
          )}

          {/* Step 5: Terms & Conditions */}
          {step === 5 && (
            <div className="space-y-4">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Terms & Conditions</h2>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-700 max-h-64 overflow-y-auto">
                <p className="mb-4">
                  I, hereby, appoint the Tax Agent and authorise them to access my ATO Tax portal
                  details to gather necessary information in order to complete my tax returns and
                  handle tax affairs for the period that I am a client.
                </p>
                <p className="mb-4">
                  I, do hereby confirm that all the information provided is true and correct to my
                  knowledge.
                </p>
                <p>
                  I am responsible to provide any supporting documents to the ATO in case of any
                  audit in the future.
                </p>
              </div>

              <div className="flex items-start space-x-3 mt-4">
                <input
                  type="checkbox"
                  id="terms_accepted"
                  name="terms_accepted"
                  checked={formData.terms_accepted}
                  onChange={handleChange}
                  className="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <label htmlFor="terms_accepted" className="text-sm text-gray-700">
                  I accept the terms & conditions <span className="text-red-500">*</span>
                </label>
              </div>
              {errors.terms_accepted && (
                <p className="text-sm text-red-600">{errors.terms_accepted}</p>
              )}
            </div>
          )}

          {/* Step 6: Upload Documents */}
          {step === 6 && (
            <div className="space-y-6">
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-gray-900">Upload Documents</h2>
                <p className="text-sm text-gray-500 mt-1">
                  These documents are needed for your personal identification and verification
                  purpose as required by ATO.
                </p>
              </div>

              <DocumentUploadField
                label="Passport Copy (Both pages)"
                docType="passport"
                required
              />

              <DocumentUploadField
                label="Bank Statement"
                docType="bank_statement"
                required
              />

              <DocumentUploadField
                label="Australian Driving Licence (both sides)"
                docType="driving_licence"
                required
                helpText="If Drivers Licence is not available, please attach any other photo ID"
              />
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between mt-8 pt-6 border-t border-gray-100">
            {step > 1 ? (
              <Button variant="secondary" onClick={handleBack}>
                Back
              </Button>
            ) : (
              <div />
            )}

            {step < totalSteps ? (
              <Button onClick={handleNext}>Continue</Button>
            ) : (
              <Button onClick={handleSubmit} loading={isLoading}>
                Complete Setup
              </Button>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
