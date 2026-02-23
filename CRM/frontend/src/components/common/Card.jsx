import React from 'react';

export default function Card({ children, className = '', padding = true, variant = 'default' }) {
  const variants = {
    default: 'bg-white border border-gray-100',
    gradient: 'bg-gradient-to-br from-white to-gray-50 border border-gray-100',
    elevated: 'bg-white border border-gray-100 shadow-lg shadow-gray-100/50',
  };

  return (
    <div className={`rounded-xl ${variants[variant]} ${padding ? 'p-4 lg:p-5' : ''} ${className}`}>
      {children}
    </div>
  );
}

export function CardHeader({ title, subtitle, action }) {
  return (
    <div className="flex items-center justify-between mb-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

const STAT_COLORS = {
  blue: { bg: 'from-blue-500 to-blue-600', light: 'bg-blue-50', text: 'text-blue-600' },
  green: { bg: 'from-emerald-500 to-emerald-600', light: 'bg-emerald-50', text: 'text-emerald-600' },
  purple: { bg: 'from-purple-500 to-purple-600', light: 'bg-purple-50', text: 'text-purple-600' },
  orange: { bg: 'from-orange-500 to-orange-600', light: 'bg-orange-50', text: 'text-orange-600' },
  pink: { bg: 'from-pink-500 to-pink-600', light: 'bg-pink-50', text: 'text-pink-600' },
  indigo: { bg: 'from-indigo-500 to-indigo-600', light: 'bg-indigo-50', text: 'text-indigo-600' },
};

export function StatCard({ title, value, icon: Icon, trend, trendUp, color = 'blue' }) {
  const colorScheme = STAT_COLORS[color] || STAT_COLORS.blue;

  return (
    <Card className="relative overflow-hidden group hover:shadow-lg transition-shadow duration-300">
      {/* Decorative gradient blob */}
      <div className={`absolute -right-4 -top-4 w-24 h-24 bg-gradient-to-br ${colorScheme.bg} rounded-full opacity-10 group-hover:opacity-20 transition-opacity`} />

      <div className="flex items-center justify-between relative">
        <div>
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
          {trend && (
            <p
              className={`text-sm mt-2 flex items-center gap-1 ${
                trendUp ? 'text-emerald-600' : 'text-red-500'
              }`}
            >
              <span className={`inline-block w-0 h-0 border-l-4 border-r-4 border-transparent ${trendUp ? 'border-b-4 border-b-emerald-600' : 'border-t-4 border-t-red-500'}`} />
              {trendUp ? '+' : ''}{trend}
            </p>
          )}
        </div>
        {Icon && (
          <div className={`p-3 ${colorScheme.light} rounded-xl`}>
            <Icon className={`h-6 w-6 ${colorScheme.text}`} />
          </div>
        )}
      </div>
    </Card>
  );
}
