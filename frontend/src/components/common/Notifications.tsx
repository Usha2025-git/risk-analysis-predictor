import { useNotificationStore } from '../../store/notificationStore';

export default function Notifications() {
  const { notifications } = useNotificationStore();

  return (
    <div className="fixed top-4 right-4 z-50 max-w-md space-y-2">
      {notifications.map((notification) => (
        <div
          key={notification.id}
          className={`p-4 rounded-lg shadow-lg text-white animate-pulse ${
            notification.type === 'success'
              ? 'bg-green-500'
              : notification.type === 'error'
              ? 'bg-red-500'
              : notification.type === 'warning'
              ? 'bg-yellow-500'
              : 'bg-blue-500'
          }`}
        >
          <div className="font-semibold">{notification.title}</div>
          <div className="text-sm">{notification.message}</div>
        </div>
      ))}
    </div>
  );
}
