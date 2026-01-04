import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLogin, useRegister } from '../hooks/useAuth';
import { validateEmail, validatePassword, getPasswordStrength } from '../utils/validators';
import { Mail, Lock, User } from 'lucide-react';

type Mode = 'login' | 'register';

export default function Login() {
  const navigate = useNavigate();
  const { login: loginAction } = useLogin();
  const { register: registerAction } = useRegister();
  
  const [mode, setMode] = useState<Mode>('login');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    if (!validateEmail(email)) {
      newErrors.email = 'Invalid email address';
    }
    
    // For login, only require a non-empty password to allow legacy demo creds
    if (mode === 'login') {
      if (!password.trim()) {
        newErrors.password = 'Password is required';
      }
    } else {
      if (!validatePassword(password)) {
        newErrors.password = 'Password must be at least 8 characters';
      }
    }
    
    if (mode === 'register') {
      if (!username.trim()) {
        newErrors.username = 'Username is required';
      }
      if (password !== confirmPassword) {
        newErrors.confirmPassword = 'Passwords do not match';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    try {
      if (mode === 'login') {
        await loginAction(email, password);
      } else {
        await registerAction(email, username, password);
      }
      navigate('/');
    } catch (error) {
      // Error is handled by the hook
    } finally {
      setLoading(false);
    }
  };

  const passwordStrength = getPasswordStrength(password);
  const strengthColors = {
    weak: 'bg-red-500',
    fair: 'bg-yellow-500',
    good: 'bg-blue-500',
    strong: 'bg-green-500',
  };
  const strengthWidths = {
    weak: 'w-1/4',
    fair: 'w-1/2',
    good: 'w-3/4',
    strong: 'w-full',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-600 to-primary-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-8 text-center">
          <h1 className="text-3xl font-bold text-white">Risk Analyzer</h1>
          <p className="text-primary-100 mt-2">Predictive Risk & Resource Management</p>
        </div>

        {/* Content */}
        <div className="p-8">
          {/* Tabs */}
          <div className="flex gap-4 mb-8">
            <button
              onClick={() => setMode('login')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                mode === 'login'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setMode('register')}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors ${
                mode === 'register'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Register
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 text-gray-400" size={18} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="your@email.com"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                />
              </div>
              {errors.email && <p className="text-red-500 text-sm mt-1">{errors.email}</p>}
            </div>

            {/* Username (Register only) */}
            {mode === 'register' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 text-gray-400" size={18} />
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    placeholder="your username"
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                  />
                </div>
                {errors.username && <p className="text-red-500 text-sm mt-1">{errors.username}</p>}
              </div>
            )}

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 text-gray-400" size={18} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                />
              </div>
              {errors.password && <p className="text-red-500 text-sm mt-1">{errors.password}</p>}
              
              {/* Password Strength (Register only) */}
              {mode === 'register' && password && (
                <div className="mt-2">
                  <div className="flex items-center space-x-2">
                    <div className="h-2 flex-1 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full ${strengthColors[passwordStrength]} ${strengthWidths[passwordStrength]} transition-all`}
                      />
                    </div>
                    <span className="text-xs font-medium text-gray-600 capitalize">
                      {passwordStrength}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Confirm Password (Register only) */}
            {mode === 'register' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 text-gray-400" size={18} />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                  />
                </div>
                {errors.confirmPassword && (
                  <p className="text-red-500 text-sm mt-1">{errors.confirmPassword}</p>
                )}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-2 rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Please wait...' : mode === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          {/* Demo Credentials */}
          {mode === 'login' && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-gray-700 mb-2">
                <strong>Demo Credentials:</strong>
              </p>
              <p className="text-xs text-gray-600">Email: demo@example.com</p>
              <p className="text-xs text-gray-600">Password: Demo!2026#01</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
