import React from 'react';
import { Layers, Plus, Trash2 } from 'lucide-react';
import type { WorkflowTask } from '../types';

interface WorkflowBuilderProps {
  workflowId: string;
  onWorkflowIdChange: (id: string) => void;
  tasks: WorkflowTask[];
  onTasksChange: (tasks: WorkflowTask[]) => void;
}

export const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({
  workflowId,
  onWorkflowIdChange,
  tasks,
  onTasksChange,
}) => {
  const handleTaskChange = (index: number, field: keyof WorkflowTask, value: any) => {
    const updated = [...tasks];
    updated[index] = {
      ...updated[index],
      [field]: value,
    };
    onTasksChange(updated);
  };

  const handleAddTask = () => {
    const nextIdx = tasks.length + 1;
    const newTask: WorkflowTask = {
      step_id: `step-${nextIdx}-inference`,
      task_type: 'inference',
      description: `Run agent reasoning analysis step ${nextIdx}`,
      input_text: 'Context prompt and input data payload for agent execution...',
      estimated_tokens: 2000,
      minimum_accuracy: 0.85,
      deadline_seconds: 5,
      delay_tolerance_seconds: 30,
      priority: 'normal',
    };
    onTasksChange([...tasks, newTask]);
  };

  const handleRemoveTask = (index: number) => {
    if (tasks.length <= 1) return;
    const updated = tasks.filter((_, i) => i !== index);
    onTasksChange(updated);
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800/90 rounded-2xl p-5 shadow-xl backdrop-blur-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-800/80 gap-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Layers className="h-4 w-4" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-white tracking-tight m-0">
              Workflow Configuration & Task DAG
            </h2>
            <p className="text-xs text-slate-400 m-0">
              Specify workflow parameters, SLA deadlines, token volume, and accuracy thresholds
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="flex items-center bg-slate-950/80 border border-slate-800 rounded-lg px-2.5 py-1">
            <span className="text-xs text-slate-400 mr-2">Workflow ID:</span>
            <input
              type="text"
              value={workflowId}
              onChange={(e) => onWorkflowIdChange(e.target.value)}
              className="bg-transparent text-xs font-mono text-indigo-300 focus:outline-none w-32 sm:w-40"
              placeholder="e.g. wf-demo-001"
            />
          </div>

          <button
            type="button"
            onClick={handleAddTask}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 text-xs font-medium transition cursor-pointer"
          >
            <Plus className="h-3.5 w-3.5" />
            Add Task
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {tasks.map((task, index) => (
          <div
            key={task.step_id || index}
            className="bg-slate-950/70 border border-slate-800/90 rounded-xl p-4 transition-all hover:border-slate-700"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2.5">
                <span className="h-6 w-6 rounded-md bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs font-bold font-mono">
                  {index + 1}
                </span>
                <span className="font-mono text-sm font-semibold text-white">
                  {task.step_id}
                </span>
                <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {task.task_type}
                </span>
              </div>

              {tasks.length > 1 && (
                <button
                  type="button"
                  onClick={() => handleRemoveTask(index)}
                  className="p-1 rounded text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition cursor-pointer"
                  title="Remove task"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
              <div>
                <label className="block text-slate-400 mb-1">Step ID</label>
                <input
                  type="text"
                  value={task.step_id}
                  onChange={(e) => handleTaskChange(index, 'step_id', e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 font-mono text-slate-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Task Type</label>
                <input
                  type="text"
                  value={task.task_type}
                  onChange={(e) => handleTaskChange(index, 'task_type', e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Estimated Tokens</label>
                <input
                  type="number"
                  min="1"
                  step="100"
                  value={task.estimated_tokens}
                  onChange={(e) => handleTaskChange(index, 'estimated_tokens', parseInt(e.target.value) || 1)}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 font-mono text-slate-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">
                  Min Accuracy: <span className="text-emerald-400 font-mono">{(task.minimum_accuracy * 100).toFixed(0)}%</span>
                </label>
                <input
                  type="range"
                  min="0.50"
                  max="0.95"
                  step="0.01"
                  value={task.minimum_accuracy}
                  onChange={(e) => handleTaskChange(index, 'minimum_accuracy', parseFloat(e.target.value))}
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Deadline (Seconds)</label>
                <input
                  type="number"
                  min="1"
                  value={task.deadline_seconds}
                  onChange={(e) => handleTaskChange(index, 'deadline_seconds', parseInt(e.target.value) || 1)}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 font-mono text-slate-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-slate-400 mb-1">Delay Tolerance (Seconds)</label>
                <input
                  type="number"
                  min="0"
                  value={task.delay_tolerance_seconds}
                  onChange={(e) => handleTaskChange(index, 'delay_tolerance_seconds', parseInt(e.target.value) || 0)}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 font-mono text-slate-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>

              <div className="sm:col-span-2">
                <label className="block text-slate-400 mb-1">Task Description</label>
                <input
                  type="text"
                  value={task.description}
                  onChange={(e) => handleTaskChange(index, 'description', e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:border-indigo-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
