import React, { useState } from 'react';
import { GitFork, Play, Pause, XCircle, CheckCircle, Clock, Loader2, Sparkles } from 'lucide-react';

export const TaskDAGView: React.FC = () => {
  const [goalPrompt, setGoalPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [activePlan, setActivePlan] = useState<any>({
    plan_id: 'plan_demo_01',
    goal: 'Automate weekly code commit, test suite execution, and Slack notification',
    status: 'running',
    progress_percentage: 66,
    tasks: [
      { id: 'task_1', description: 'Detect local Git changes & run unit test suite', engine_type: 'coding', status: 'completed' },
      { id: 'task_2', description: 'Commit changes with message and push to GitHub repository', engine_type: 'plugin', status: 'running' },
      { id: 'task_3', description: 'Post summary message to #dev-updates on Slack', engine_type: 'plugin', status: 'pending' },
    ]
  });

  const handleCreatePlan = async () => {
    if (!goalPrompt.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/planner/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ goal: goalPrompt })
      });
      const data = res.ok ? await res.json() : {};
      if (data.status === 'success') {
        setActivePlan(data.plan);
      }
    } catch (err) {
      console.error('Failed to create plan:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskAction = async (action: 'pause' | 'resume' | 'cancel') => {
    try {
      const res = await fetch('/api/tasks/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan_id: activePlan.plan_id, action })
      });
      const data = res.ok ? await res.json() : {};
      if (data.status === 'success') {
        setActivePlan((prev: any) => ({ ...prev, status: action === 'cancel' ? 'cancelled' : action === 'pause' ? 'paused' : 'running' }));
      }
    } catch (err) {
      console.error('Task action error:', err);
    }
  };

  return (
    <div className="space-y-4 text-slate-100">
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <h3 className="text-sm font-semibold tracking-wider uppercase text-purple-400 flex items-center gap-2">
          <GitFork className="w-4 h-4 text-purple-400" />
          Autonomous DAG Planning & Task Graph
        </h3>
        <span className="text-[10px] font-mono text-purple-300 bg-purple-950/60 border border-purple-500/30 px-2 py-0.5 rounded-full">
          Phase 5 Engine
        </span>
      </div>

      {/* Plan Creator Form */}
      <div className="flex gap-2">
        <input
          type="text"
          value={goalPrompt}
          onChange={(e) => setGoalPrompt(e.target.value)}
          placeholder="Enter high-level autonomous goal e.g. 'Push latest code to GitHub & notify team on Slack'"
          className="flex-1 bg-slate-900/80 border border-white/15 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-purple-400"
        />
        <button
          onClick={handleCreatePlan}
          disabled={loading || !goalPrompt.trim()}
          className="bg-purple-600 hover:bg-purple-500 text-white font-mono text-xs px-4 py-2 rounded-xl flex items-center gap-1.5 transition-all disabled:opacity-40"
        >
          {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
          Decompose DAG Plan
        </button>
      </div>

      {/* Active Plan Overview */}
      {activePlan && (
        <div className="bg-slate-950/70 border border-purple-500/20 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-[10px] font-mono text-slate-400 uppercase">Active DAG Plan ID: {activePlan.plan_id}</div>
              <div className="text-sm font-medium text-purple-200 mt-0.5">{activePlan.goal}</div>
            </div>
            <div className="flex items-center gap-1.5">
              <button onClick={() => handleTaskAction('resume')} className="p-1.5 bg-emerald-600/30 hover:bg-emerald-600/50 border border-emerald-500/30 text-emerald-300 rounded-lg text-xs flex items-center gap-1">
                <Play className="w-3 h-3" /> Resume
              </button>
              <button onClick={() => handleTaskAction('pause')} className="p-1.5 bg-amber-600/30 hover:bg-amber-600/50 border border-amber-500/30 text-amber-300 rounded-lg text-xs flex items-center gap-1">
                <Pause className="w-3 h-3" /> Pause
              </button>
              <button onClick={() => handleTaskAction('cancel')} className="p-1.5 bg-rose-600/30 hover:bg-rose-600/50 border border-rose-500/30 text-rose-300 rounded-lg text-xs flex items-center gap-1">
                <XCircle className="w-3 h-3" /> Cancel
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          <div>
            <div className="flex justify-between text-[11px] font-mono text-slate-400 mb-1">
              <span>Execution Progress</span>
              <span className="text-purple-300">{activePlan.progress_percentage}%</span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
              <div className="bg-gradient-to-r from-purple-500 to-cyan-400 h-2 transition-all duration-500" style={{ width: `${activePlan.progress_percentage}%` }} />
            </div>
          </div>

          {/* Sub-tasks DAG Sequence */}
          <div className="space-y-2 pt-1">
            {activePlan.tasks.map((task: any, idx: number) => (
              <div key={task.id} className="flex items-center justify-between p-2.5 rounded-lg bg-white/5 border border-white/5 text-xs font-mono">
                <div className="flex items-center gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-slate-800 flex items-center justify-center text-[10px] text-slate-300 border border-white/10">{idx + 1}</span>
                  <div>
                    <div className="text-slate-200">{task.description}</div>
                    <div className="text-[10px] text-slate-400">Target Engine: <span className="text-cyan-400">{task.engine_type}</span></div>
                  </div>
                </div>
                <div>
                  {task.status === 'completed' && <span className="text-emerald-400 flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" /> Completed</span>}
                  {task.status === 'running' && <span className="text-cyan-400 flex items-center gap-1 animate-pulse"><Loader2 className="w-3.5 h-3.5 animate-spin" /> Executing...</span>}
                  {task.status === 'pending' && <span className="text-slate-400 flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> Pending</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
