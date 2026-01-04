export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validatePassword = (password: string): boolean => {
  return password.length >= 8;
};

export const validateProjectName = (name: string): boolean => {
  return name.trim().length > 0 && name.trim().length <= 255;
};

export const validateNumber = (value: unknown): boolean => {
  if (value === null || value === undefined) return false;
  const num = Number(value);
  return Number.isFinite(num);
};

export const validateAllocation = (allocation: number, maxAllocation: number): boolean => {
  return allocation >= 0 && allocation <= maxAllocation;
};

export const getPasswordStrength = (password: string): 'weak' | 'fair' | 'good' | 'strong' => {
  if (password.length < 8) return 'weak';
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*]/.test(password);
  
  const strength = [hasUpperCase, hasLowerCase, hasNumbers, hasSpecialChar].filter(Boolean).length;
  
  if (strength === 4) return 'strong';
  if (strength === 3) return 'good';
  if (strength === 2) return 'fair';
  return 'weak';
};
