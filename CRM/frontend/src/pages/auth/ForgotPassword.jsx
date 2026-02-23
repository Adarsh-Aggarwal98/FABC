import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import Input from '../../components/common/Input';
import Button from '../../components/common/Button';
import Card from '../../components/common/Card';
import { authAPI } from '../../services/api';

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [step, setStep] = useState('email'); // 'email', 'otp', 'reset'
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await authAPI.forgotPassword(email);
      toast.success('If the email exists, an OTP has been sent');
      setStep('otp');
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    if (!newPassword || newPassword.length < 8) {
      setError('Password must be at least 8 characters');
      setIsLoading(false);
      return;
    }
    if (!/[A-Z]/.test(newPassword)) {
      setError('Password must contain at least one uppercase letter');
      setIsLoading(false);
      return;
    }
    if (!/[a-z]/.test(newPassword)) {
      setError('Password must contain at least one lowercase letter');
      setIsLoading(false);
      return;
    }
    if (!/[0-9]/.test(newPassword)) {
      setError('Password must contain at least one number');
      setIsLoading(false);
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      setIsLoading(false);
      return;
    }

    try {
      await authAPI.resetPassword({
        email,
        otp,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      toast.success('Password reset successfully');
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#0B1A3B] via-[#1A3A6B] to-[#0891B2] py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <img
            src="/crm/assets/aussupersource-logo.png"
            alt="AusSuperSource"
            className="h-20 w-auto mx-auto mb-6"
          />
          <h2 className="text-2xl font-semibold text-gray-900">Reset Password</h2>
          <p className="text-gray-500 mt-2">We'll send you a verification code</p>
        </div>

        <Card>
          {step === 'email' && (
            <form onSubmit={handleEmailSubmit} className="space-y-4">
              <p className="text-gray-600 text-sm mb-4">
                Enter your email address and we'll send you a verification code to reset your password.
              </p>

              <Input
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />

              {error && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-100">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <Button type="submit" className="w-full" loading={isLoading}>
                Send Code
              </Button>

              <div className="text-center">
                <Link to="/login" className="text-sm text-primary-600 hover:text-primary-700">
                  Back to login
                </Link>
              </div>
            </form>
          )}

          {step === 'otp' && (
            <form onSubmit={handleResetSubmit} className="space-y-4">
              <p className="text-gray-600 text-sm mb-4">
                Enter the verification code sent to <strong>{email}</strong> and your new password.
              </p>

              <Input
                label="Verification Code"
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="Enter 6-digit code"
                maxLength={6}
                required
              />

              <Input
                label="New Password"
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="Enter new password"
                required
              />

              <Input
                label="Confirm Password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                required
              />

              <div className="bg-blue-50 p-3 rounded-lg">
                <p className="text-xs text-blue-700 font-medium mb-1.5">Password requirements:</p>
                <ul className="text-xs space-y-0.5">
                  <li className={newPassword.length >= 8 ? 'text-green-600' : 'text-blue-600'}>
                    - At least 8 characters
                  </li>
                  <li className={/[A-Z]/.test(newPassword) ? 'text-green-600' : 'text-blue-600'}>
                    - One uppercase letter
                  </li>
                  <li className={/[a-z]/.test(newPassword) ? 'text-green-600' : 'text-blue-600'}>
                    - One lowercase letter
                  </li>
                  <li className={/[0-9]/.test(newPassword) ? 'text-green-600' : 'text-blue-600'}>
                    - One number
                  </li>
                </ul>
              </div>

              {error && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-100">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <Button type="submit" className="w-full" loading={isLoading}>
                Reset Password
              </Button>

              <div className="text-center">
                <button
                  type="button"
                  onClick={() => setStep('email')}
                  className="text-sm text-primary-600 hover:text-primary-700"
                >
                  Try different email
                </button>
              </div>
            </form>
          )}
        </Card>
      </div>
    </div>
  );
}
