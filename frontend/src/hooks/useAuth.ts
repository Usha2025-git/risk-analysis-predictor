import { isAxiosError } from 'axios';
import { useAuthStore } from '../store/authStore';
import { useNotificationStore } from '../store/notificationStore';

const getErrorMessage = (error: unknown): string => {
  if (isAxiosError(error)) {
    return error.response?.data?.detail ?? error.message;
  }
  if (error instanceof Error) return error.message;
  return 'Request failed';
};

export const useLogin = () => {
  const { login } = useAuthStore();
  const { addNotification } = useNotificationStore();

  const handleLogin = async (email: string, password: string) => {
    try {
      await login(email, password);
      addNotification({
        type: 'success',
        title: 'Welcome',
        message: 'Logged in successfully',
      });
    } catch (error) {
      const message = getErrorMessage(error) || 'Login failed';
      addNotification({
        type: 'error',
        title: 'Login Error',
        message,
      });
    }
  };

  return { login: handleLogin };
};

export const useRegister = () => {
  const { register } = useAuthStore();
  const { addNotification } = useNotificationStore();

  const handleRegister = async (email: string, username: string, password: string) => {
    try {
      await register(email, username, password);
      addNotification({
        type: 'success',
        title: 'Welcome',
        message: 'Account created successfully',
      });
    } catch (error) {
      const message = getErrorMessage(error) || 'Registration failed';
      addNotification({
        type: 'error',
        title: 'Registration Error',
        message,
      });
    }
  };

  return { register: handleRegister };
};

export const useLogout = () => {
  const { logout } = useAuthStore();
  const { addNotification } = useNotificationStore();

  const handleLogout = () => {
    logout();
    addNotification({
      type: 'info',
      title: 'Logged Out',
      message: 'You have been logged out',
    });
  };

  return { logout: handleLogout };
};

export const useCurrentUser = () => {
  const { user, isAuthenticated, getCurrentUser, hydrate } = useAuthStore();

  return {
    user,
    isAuthenticated,
    getCurrentUser,
    hydrate,
  };
};
