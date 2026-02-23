import {
  ListBulletIcon,
  Squares2X2Icon,
  ArrowsPointingOutIcon
} from '@heroicons/react/24/outline';

const views = [
  { id: 'list', label: 'List', icon: ListBulletIcon },
  { id: 'board', label: 'Board', icon: Squares2X2Icon },
  { id: 'workflow', label: 'Workflow', icon: ArrowsPointingOutIcon },
];

export default function ViewToggle({ currentView, onChange }) {
  return (
    <div className="inline-flex rounded-lg border border-gray-200 bg-white p-1">
      {views.map((view) => {
        const Icon = view.icon;
        const isActive = currentView === view.id;

        return (
          <button
            key={view.id}
            onClick={() => onChange(view.id)}
            className={`
              inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium
              transition-colors duration-150
              ${isActive
                ? 'bg-blue-50 text-blue-700'
                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }
            `}
            title={view.label}
          >
            <Icon className="w-4 h-4" />
            <span className="hidden sm:inline">{view.label}</span>
          </button>
        );
      })}
    </div>
  );
}
