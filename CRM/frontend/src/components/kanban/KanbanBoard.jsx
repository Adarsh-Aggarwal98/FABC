import { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import KanbanColumn from './KanbanColumn';
import { statusAPI, requestsAPI, userAPI, tasksAPI } from '../../services/api';
import useAuthStore from '../../store/authStore';

export default function KanbanBoard({ requests, onStatusChange, isLoading, tasks = [], onTaskStatusChange, onTaskClick }) {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [statuses, setStatuses] = useState([]);
  const [statusLoading, setStatusLoading] = useState(true);
  const [updatingRequest, setUpdatingRequest] = useState(null);
  const [accountants, setAccountants] = useState([]);
  const [allowedTargets, setAllowedTargets] = useState(null); // status keys allowed for current drag

  const isAdmin = user?.role === 'super_admin' || user?.role === 'admin';

  // Fetch statuses and accountants on mount
  useEffect(() => {
    fetchStatuses();
    if (isAdmin) {
      fetchAccountants();
    }
  }, [isAdmin]);

  const fetchAccountants = async () => {
    try {
      const response = await userAPI.getAccountants();
      setAccountants(response.data.data?.accountants || []);
    } catch (error) {
      console.error('Failed to fetch accountants:', error);
    }
  };

  const fetchStatuses = async () => {
    try {
      setStatusLoading(true);
      const response = await statusAPI.list();
      setStatuses(response.data.statuses || []);
    } catch (error) {
      console.error('Failed to fetch statuses:', error);
      setStatuses([
        { status_key: 'pending', display_name: 'Pending', color: '#F59E0B', position: 1 },
        { status_key: 'in_progress', display_name: 'In Progress', color: '#3B82F6', position: 2 },
        { status_key: 'review', display_name: 'Under Review', color: '#8B5CF6', position: 3 },
        { status_key: 'completed', display_name: 'Completed', color: '#10B981', position: 5 },
        { status_key: 'cancelled', display_name: 'Cancelled', color: '#EF4444', position: 6 },
      ]);
    } finally {
      setStatusLoading(false);
    }
  };

  // Group requests and tasks by status directly (unified status keys, no mapping needed)
  const requestsByStatus = useMemo(() => {
    const grouped = {};
    statuses.forEach((status) => {
      grouped[status.status_key] = [];
    });

    // Group requests by their status directly
    requests.forEach((req) => {
      if (grouped[req.status]) {
        grouped[req.status].push(req);
      } else {
        // Status doesn't have a column - put in first non-final column
        const firstNonFinal = statuses.find(s => !s.is_final);
        if (firstNonFinal) {
          grouped[firstNonFinal.status_key]?.push(req);
        } else if (statuses.length > 0) {
          grouped[statuses[0].status_key]?.push(req);
        }
      }
    });

    // Merge tasks into the same columns (tasks now use unified status keys)
    tasks.forEach((task) => {
      const taskItem = { ...task, _isTask: true };
      if (grouped[task.status]) {
        grouped[task.status].push(taskItem);
      } else {
        // Fallback: put in first non-final column
        const firstNonFinal = statuses.find(s => !s.is_final);
        const fallbackKey = firstNonFinal?.status_key || statuses[0]?.status_key;
        if (fallbackKey && grouped[fallbackKey]) {
          grouped[fallbackKey].push(taskItem);
        }
      }
    });

    return grouped;
  }, [requests, tasks, statuses]);

  // Fetch allowed transitions when drag starts
  const handleDragStart = useCallback(async (fromStatus) => {
    try {
      const response = await statusAPI.getAllowedTransitions(fromStatus);
      setAllowedTargets(response.data.allowed_targets || null);
    } catch (error) {
      // If fetch fails, allow all (permissive fallback)
      setAllowedTargets(null);
    }
  }, []);

  const handleDragEnd = useCallback(() => {
    setAllowedTargets(null);
  }, []);

  // Handle card drop (status change) - supports both requests and tasks
  // With unified statuses, column keys ARE the backend status keys directly
  const handleDrop = async (rawItemId, newColumnKey) => {
    setAllowedTargets(null);
    // dataTransfer returns strings; coerce to number so === matches numeric IDs
    const itemId = isNaN(rawItemId) ? rawItemId : Number(rawItemId);
    const targetStatus = statuses.find((s) => s.status_key === newColumnKey);

    // Check if it's a task
    const task = tasks.find((t) => t.id === itemId);
    if (task) {
      if (task.status === newColumnKey) return;

      setUpdatingRequest(itemId);
      try {
        await tasksAPI.updateStatus(itemId, newColumnKey);
        toast.success(`Task moved to ${targetStatus?.display_name || newColumnKey}`);
        if (onTaskStatusChange) {
          onTaskStatusChange(itemId, newColumnKey);
        }
      } catch (error) {
        console.error('Failed to update task status:', error);
        toast.error(error.response?.data?.error || 'Failed to update task status');
      } finally {
        setUpdatingRequest(null);
      }
      return;
    }

    // It's a request - send column key directly as backend status
    const req = requests.find((r) => r.id === itemId);
    if (!req) return;

    if (req.status === newColumnKey) return;

    if (targetStatus?.wip_limit) {
      const currentCount = requestsByStatus[newColumnKey]?.length || 0;
      if (currentCount >= targetStatus.wip_limit) {
        toast.error(`${targetStatus.display_name} column has reached its WIP limit of ${targetStatus.wip_limit}`);
        return;
      }
    }

    setUpdatingRequest(itemId);

    try {
      await requestsAPI.updateStatus(itemId, newColumnKey);
      toast.success(`Request moved to ${targetStatus?.display_name || newColumnKey}`);

      if (onStatusChange) {
        onStatusChange(itemId, newColumnKey);
      }
    } catch (error) {
      console.error('Failed to update status:', error);
      toast.error(error.response?.data?.error || 'Failed to update status');
    } finally {
      setUpdatingRequest(null);
    }
  };

  // Handle card click (navigate to detail or open task edit)
  const handleCardClick = (item) => {
    if (item._isTask) {
      if (onTaskClick) onTaskClick(item);
    } else {
      navigate(`/requests/${item.id}`);
    }
  };

  // Handle staff assignment from card
  const handleAssign = async (requestId, accountantId) => {
    try {
      await requestsAPI.assign(requestId, accountantId);
      const accountant = accountants.find(a => a.id === accountantId);
      toast.success(`Assigned to ${accountant?.full_name || 'staff member'}`);

      // Notify parent to refresh data
      if (onStatusChange) {
        onStatusChange(requestId, null, true); // third param indicates refresh needed
      }
    } catch (error) {
      console.error('Failed to assign request:', error);
      toast.error(error.response?.data?.error || 'Failed to assign request');
      throw error;
    }
  };

  // Handle task assignment from card
  const handleTaskAssign = async (taskId, accountantId) => {
    try {
      await tasksAPI.update(taskId, { assigned_to_id: accountantId });
      const accountant = accountants.find(a => a.id === accountantId);
      toast.success(`Task assigned to ${accountant?.full_name || 'staff member'}`);

      if (onTaskStatusChange) {
        // Trigger a refresh by passing the updated assignment
        onTaskStatusChange(taskId, null, true);
      }
    } catch (error) {
      console.error('Failed to assign task:', error);
      toast.error(error.response?.data?.error || 'Failed to assign task');
      throw error;
    }
  };

  if (statusLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin h-8 w-8 border-2 border-blue-500 rounded-full border-t-transparent"></div>
        <span className="ml-3 text-gray-500">Loading board...</span>
      </div>
    );
  }

  return (
    <div className="flex gap-4 overflow-x-auto pb-4 min-h-[400px]">
      {statuses
        .filter((status) => !status.is_final || requestsByStatus[status.status_key]?.length > 0)
        .sort((a, b) => a.position - b.position)
        .map((status) => (
          <KanbanColumn
            key={status.status_key}
            status={status}
            requests={requestsByStatus[status.status_key] || []}
            onDrop={handleDrop}
            onCardClick={handleCardClick}
            isLoading={isLoading || updatingRequest !== null}
            accountants={isAdmin ? accountants : []}
            onAssign={isAdmin ? handleAssign : null}
            onTaskAssign={isAdmin ? handleTaskAssign : null}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
            isDropDisabled={allowedTargets !== null && !allowedTargets.includes(status.status_key)}
          />
        ))}
    </div>
  );
}
