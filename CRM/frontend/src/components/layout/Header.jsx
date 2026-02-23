import React, { useState, useEffect } from 'react';
import { BellIcon, Bars3Icon } from '@heroicons/react/24/outline';
import useNotificationStore from '../../store/notificationStore';

export default function Header({ onMenuClick, title }) {
  const { unreadCount, fetchUnreadCount, notifications, fetchNotifications, markAsRead } =
    useNotificationStore();
  const [showNotifications, setShowNotifications] = useState(false);

  useEffect(() => {
    fetchUnreadCount();
    const interval = setInterval(fetchUnreadCount, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const handleNotificationClick = () => {
    setShowNotifications(!showNotifications);
    if (!showNotifications) {
      fetchNotifications({ per_page: 10 });
    }
  };

  return (
    <header className="h-16 bg-white/80 backdrop-blur-sm border-b border-gray-200/50 flex items-center justify-between px-6 sticky top-0 z-30">
      <div className="flex items-center">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 rounded-lg hover:bg-gray-100 mr-4"
        >
          <Bars3Icon className="h-6 w-6 text-gray-600" />
        </button>
        <div>
          <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
        </div>
      </div>

      {/* Notifications */}
      <div className="relative">
        <button
          onClick={handleNotificationClick}
          className="p-2 rounded-xl hover:bg-gray-100 relative transition-colors"
        >
          <BellIcon className="h-6 w-6 text-gray-500" />
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 h-5 w-5 bg-gradient-to-r from-red-500 to-pink-500 rounded-full text-xs text-white flex items-center justify-center font-medium shadow-lg shadow-red-500/25">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>

        {/* Notifications dropdown */}
        {showNotifications && (
          <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-100 z-50 overflow-hidden">
            <div className="p-4 border-b border-gray-100 bg-gradient-to-r from-slate-50 to-gray-50">
              <h3 className="font-semibold text-gray-900">Notifications</h3>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center text-gray-400">
                  <BellIcon className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  No notifications
                </div>
              ) : (
                notifications.map((notification) => (
                  <div
                    key={notification.id}
                    onClick={() => markAsRead(notification.id)}
                    className={`p-4 border-b border-gray-50 hover:bg-gray-50 cursor-pointer transition-colors ${
                      !notification.is_read ? 'bg-gradient-to-r from-blue-50 to-indigo-50 border-l-2 border-l-primary-500' : ''
                    }`}
                  >
                    <p className="text-sm font-medium text-gray-900">
                      {notification.title}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">
                      {notification.message}
                    </p>
                    <p className="text-xs text-gray-400 mt-2">
                      {new Date(notification.created_at).toLocaleDateString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
