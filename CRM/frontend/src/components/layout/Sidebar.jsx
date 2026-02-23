import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  HomeIcon,
  UserIcon,
  UsersIcon,
  FolderIcon,
  DocumentTextIcon,
  ClipboardDocumentListIcon,
  Cog6ToothIcon,
  ArrowLeftOnRectangleIcon,
  PlusCircleIcon,
  BuildingOffice2Icon,
  ChevronLeftIcon,
  ChevronRightIcon,
  EnvelopeIcon,
  DocumentCurrencyDollarIcon,
  SwatchIcon,
  ChartBarIcon,
  CloudIcon,
  ArrowPathIcon,
  Squares2X2Icon,
  UserGroupIcon,
  InboxIcon,
  PencilSquareIcon,
  NewspaperIcon,
  BellAlertIcon,
} from '@heroicons/react/24/outline';
import useAuthStore from '../../store/authStore';
import useThemeStore from '../../store/themeStore';

const navigation = {
  super_admin: [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Companies', href: '/companies', icon: BuildingOffice2Icon },
    { name: 'Users', href: '/users', icon: UsersIcon },
    { name: 'Client Entities', href: '/client-entities', icon: FolderIcon },
    { name: 'Requests', href: '/requests', icon: FolderIcon },
    { name: 'Services', href: '/services', icon: ClipboardDocumentListIcon },
    { name: 'Workflows', href: '/settings/workflows', icon: ArrowPathIcon },
    { name: 'Board Statuses', href: '/settings/statuses', icon: Squares2X2Icon },
    { name: 'Forms', href: '/forms', icon: DocumentTextIcon },
    { name: 'Job Analytics', href: '/settings/analytics', icon: ChartBarIcon },
    { name: 'Client Analytics', href: '/settings/admin-analytics', icon: UserGroupIcon },
    { name: 'Company Settings', href: '/settings/company', icon: BuildingOffice2Icon },
    { name: 'Invoice Settings', href: '/settings/invoice', icon: DocumentCurrencyDollarIcon },
    { name: 'Email Templates', href: '/settings/email-templates', icon: EnvelopeIcon },
    // { name: 'Email & Storage', href: '/settings/email-storage', icon: CloudIcon }, // Using Graph API & SharePoint via env vars
    { name: 'Branding', href: '/settings/branding', icon: SwatchIcon },
    { name: 'Data Import', href: '/settings/import', icon: ArrowPathIcon },
    { name: 'Leads', href: '/leads', icon: InboxIcon },
    { name: 'Audit Letters', href: '/letters', icon: PencilSquareIcon },
    { name: 'SMSF Data Sheet', href: '/smsf-data-sheet', icon: DocumentTextIcon },
    { name: 'Blog Posts', href: '/settings/blogs', icon: NewspaperIcon },
    { name: 'ATO Alerts', href: '/settings/ato-alerts', icon: BellAlertIcon },
  ],
  admin: [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Users', href: '/users', icon: UsersIcon },
    { name: 'Client Entities', href: '/client-entities', icon: FolderIcon },
    { name: 'Requests', href: '/requests', icon: FolderIcon },
    { name: 'Services', href: '/services', icon: ClipboardDocumentListIcon },
    { name: 'Forms', href: '/forms', icon: DocumentTextIcon },
    { name: 'Workflows', href: '/settings/workflows', icon: ArrowPathIcon },
    { name: 'Board Statuses', href: '/settings/statuses', icon: Squares2X2Icon },
    { name: 'Job Analytics', href: '/settings/analytics', icon: ChartBarIcon },
    { name: 'Client Analytics', href: '/settings/admin-analytics', icon: UserGroupIcon },
    { name: 'Company Settings', href: '/settings/company', icon: BuildingOffice2Icon },
    { name: 'Invoice Settings', href: '/settings/invoice', icon: DocumentCurrencyDollarIcon },
    { name: 'Email Templates', href: '/settings/email-templates', icon: EnvelopeIcon },
    // { name: 'Email & Storage', href: '/settings/email-storage', icon: CloudIcon }, // Using Graph API & SharePoint via env vars
    { name: 'Branding', href: '/settings/branding', icon: SwatchIcon },
    { name: 'Leads', href: '/leads', icon: InboxIcon },
    { name: 'Audit Letters', href: '/letters', icon: PencilSquareIcon },
    { name: 'SMSF Data Sheet', href: '/smsf-data-sheet', icon: DocumentTextIcon },
    { name: 'Blog Posts', href: '/settings/blogs', icon: NewspaperIcon },
    { name: 'ATO Alerts', href: '/settings/ato-alerts', icon: BellAlertIcon },
  ],
  senior_accountant: [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Users', href: '/users', icon: UsersIcon },
    { name: 'Client Entities', href: '/client-entities', icon: FolderIcon },
    { name: 'Requests', href: '/requests', icon: FolderIcon },
    { name: 'Services', href: '/services', icon: ClipboardDocumentListIcon },
    { name: 'Forms', href: '/forms', icon: DocumentTextIcon },
    { name: 'Workflows', href: '/settings/workflows', icon: ArrowPathIcon },
    { name: 'Board Statuses', href: '/settings/statuses', icon: Squares2X2Icon },
    { name: 'Email Templates', href: '/settings/email-templates', icon: EnvelopeIcon },
    { name: 'Audit Letters', href: '/letters', icon: PencilSquareIcon },
    { name: 'SMSF Data Sheet', href: '/smsf-data-sheet', icon: DocumentTextIcon },
  ],
  accountant: [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Client Entities', href: '/client-entities', icon: FolderIcon },
    { name: 'Requests', href: '/requests', icon: FolderIcon },
    { name: 'Services', href: '/services', icon: ClipboardDocumentListIcon },
    { name: 'Job Analytics', href: '/settings/analytics', icon: ChartBarIcon },
    { name: 'Audit Letters', href: '/letters', icon: PencilSquareIcon },
    { name: 'SMSF Data Sheet', href: '/smsf-data-sheet', icon: DocumentTextIcon },
  ],
  external_accountant: [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Requests', href: '/requests', icon: FolderIcon },
  ],
  user: [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'New Request', href: '/services/new', icon: PlusCircleIcon },
    { name: 'My Requests', href: '/requests', icon: FolderIcon },
    { name: 'My Profile', href: '/profile', icon: UserIcon },
  ],
};

export default function Sidebar({ collapsed = false, onToggleCollapse }) {
  const { user, logout } = useAuthStore();
  const { logoUrl, companyName, primaryColor, sidebarBgColor, sidebarTextColor, sidebarHoverBgColor } = useThemeStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const userNav = navigation[user?.role] || navigation.user;

  // Get initials for fallback logo
  const getInitials = (name) => {
    if (!name) return 'AC';
    const words = name.split(' ');
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  // Calculate a slightly lighter shade for gradient effect
  const adjustBrightness = (hex, percent) => {
    const num = parseInt(hex.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = Math.min(255, Math.max(0, (num >> 16) + amt));
    const G = Math.min(255, Math.max(0, ((num >> 8) & 0x00ff) + amt));
    const B = Math.min(255, Math.max(0, (num & 0x0000ff) + amt));
    return `#${(0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1)}`;
  };

  const sidebarGradientMid = adjustBrightness(sidebarBgColor || '#0f172a', 5);

  return (
    <div
      className={`flex flex-col h-full transition-all duration-300 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
      style={{
        background: `linear-gradient(to bottom, ${sidebarBgColor}, ${sidebarGradientMid}, ${sidebarBgColor})`
      }}
    >
      {/* Logo */}
      <div
        className={`flex-shrink-0 flex items-center h-16 ${collapsed ? 'justify-center px-2' : 'px-6'}`}
        style={{ borderBottom: `1px solid ${sidebarHoverBgColor}50` }}
      >
        <div className="flex items-center gap-2">
          {logoUrl ? (
            <img
              src={logoUrl}
              alt={companyName}
              className="w-8 h-8 rounded-lg object-contain flex-shrink-0 bg-white"
            />
          ) : (
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
              style={{ backgroundColor: primaryColor || '#4F46E5' }}
            >
              <span className="text-white font-bold text-sm">{getInitials(companyName)}</span>
            </div>
          )}
          {!collapsed && (
            <h1
              className="text-lg font-bold whitespace-nowrap truncate max-w-[160px]"
              style={{ color: sidebarTextColor }}
            >
              {companyName || 'AusSuperSource'}
            </h1>
          )}
        </div>
      </div>

      {/* Navigation - scrollable */}
      <nav className={`flex-1 overflow-y-auto py-4 space-y-1 ${collapsed ? 'px-2' : 'px-3'}`}>
        {userNav.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            title={collapsed ? item.name : undefined}
            className={({ isActive }) =>
              `flex items-center ${collapsed ? 'justify-center px-2' : 'px-3'} py-2.5 text-sm font-medium rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-primary-600 to-primary-500 text-white shadow-lg shadow-primary-500/25'
                  : ''
              }`
            }
            style={({ isActive }) =>
              isActive
                ? {}
                : { color: `${sidebarTextColor}cc` }
            }
            onMouseEnter={(e) => {
              if (!e.currentTarget.classList.contains('from-primary-600')) {
                e.currentTarget.style.backgroundColor = `${sidebarHoverBgColor}80`;
                e.currentTarget.style.color = sidebarTextColor;
              }
            }}
            onMouseLeave={(e) => {
              if (!e.currentTarget.classList.contains('from-primary-600')) {
                e.currentTarget.style.backgroundColor = 'transparent';
                e.currentTarget.style.color = `${sidebarTextColor}cc`;
              }
            }}
          >
            <item.icon className={`h-5 w-5 flex-shrink-0 ${collapsed ? '' : 'mr-3'}`} />
            {!collapsed && <span>{item.name}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Collapse Toggle Button */}
      <div className={`flex-shrink-0 px-3 pb-2 ${collapsed ? 'px-2' : 'px-3'}`}>
        <button
          onClick={onToggleCollapse}
          className={`flex items-center ${collapsed ? 'justify-center w-full' : 'w-full'} px-3 py-2 text-sm font-medium rounded-lg transition-colors`}
          style={{ color: `${sidebarTextColor}99` }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = `${sidebarHoverBgColor}80`;
            e.currentTarget.style.color = sidebarTextColor;
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = 'transparent';
            e.currentTarget.style.color = `${sidebarTextColor}99`;
          }}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? (
            <ChevronRightIcon className="h-5 w-5" />
          ) : (
            <>
              <ChevronLeftIcon className="h-5 w-5 mr-3" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>

      {/* User info & Logout */}
      <div
        className={`flex-shrink-0 p-4 ${collapsed ? 'px-2' : 'p-4'}`}
        style={{ borderTop: `1px solid ${sidebarHoverBgColor}50` }}
      >
        {!collapsed && (
          <NavLink to="/profile" className="flex items-center mb-4 hover:opacity-80 transition-opacity">
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center ring-2 ring-primary-400/20 flex-shrink-0">
              <span className="text-white font-semibold">
                {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase()}
              </span>
            </div>
            <div className="ml-3 overflow-hidden">
              <p className="text-sm font-medium truncate" style={{ color: sidebarTextColor }}>
                {user?.full_name || user?.email}
              </p>
              <p className="text-xs capitalize" style={{ color: `${sidebarTextColor}99` }}>
                {user?.role?.replace(/_/g, ' ')}
              </p>
            </div>
          </NavLink>
        )}
        <button
          onClick={handleLogout}
          title={collapsed ? 'Logout' : undefined}
          className={`flex items-center ${collapsed ? 'justify-center' : ''} w-full px-3 py-2 text-sm font-medium rounded-lg hover:bg-red-500/10 hover:text-red-400 transition-colors`}
          style={{ color: `${sidebarTextColor}cc` }}
        >
          <ArrowLeftOnRectangleIcon className={`h-5 w-5 flex-shrink-0 ${collapsed ? '' : 'mr-3'}`} />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </div>
  );
}
