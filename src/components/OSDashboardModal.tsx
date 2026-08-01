import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Activity, GitFork, Database, Blocks, Terminal, Layers, Sparkles, UserCheck, Code2, Network, Building2 } from 'lucide-react';
import { SystemDashboardView } from './views/SystemDashboardView';
import { TaskDAGView } from './views/TaskDAGView';
import { MemoryView } from './views/MemoryView';
import { PluginMCPView } from './views/PluginMCPView';
import { ModelRouterAgentView } from './views/ModelRouterAgentView';
import { CommandCenterView } from './views/CommandCenterView';
import { OverlayControlView } from './views/OverlayControlView';
import { DeveloperEngineView } from './views/DeveloperEngineView';
import { ProductionEnterpriseView } from './views/ProductionEnterpriseView';
import { ThreeAvatar } from './ThreeAvatar';
import { AssistantState } from '../types';

interface OSDashboardModalProps {
  isOpen: boolean;
  onClose: () => void;
  assistantState: AssistantState;
  outputVolume: number;
  micVolume: number;
}

type OSTab = 'hologram' | 'dashboard' | 'enterprise' | 'developer' | 'tasks' | 'memory' | 'plugins' | 'router' | 'command' | 'overlay';

export const OSDashboardModal: React.FC<OSDashboardModalProps> = ({
  isOpen,
  onClose,
  assistantState,
  outputVolume,
  micVolume,
}) => {
  const [activeTab, setActiveTab] = useState<OSTab>('hologram');

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="relative w-full max-w-4xl bg-slate-950/90 border border-cyan-500/30 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[85vh] text-slate-100"
        >
          {/* Header Bar */}
          <div className="p-4 border-b border-white/10 flex items-center justify-between bg-white/5">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-cyan-400 animate-ping" />
              <h2 className="text-sm font-semibold tracking-wider uppercase text-cyan-300 font-mono flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                KIRA AI Operating System • Phase 7 JARVIS Control Core
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-white/5 hover:bg-white/15 text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Navigation Bar */}
          <div className="flex items-center gap-1 p-2 bg-slate-900/80 border-b border-white/10 overflow-x-auto text-xs font-mono">
            <button
              onClick={() => setActiveTab('hologram')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'hologram'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <UserCheck className="w-3.5 h-3.5" /> 3D Avatar
            </button>

            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Activity className="w-3.5 h-3.5" /> Telemetry
            </button>

            <button
              onClick={() => setActiveTab('enterprise')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'enterprise'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Building2 className="w-3.5 h-3.5 text-emerald-400" /> Enterprise
            </button>

            <button
              onClick={() => setActiveTab('developer')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'developer'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Code2 className="w-3.5 h-3.5 text-cyan-400" /> Dev Engine
            </button>

            <button
              onClick={() => setActiveTab('tasks')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'tasks'
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-400/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <GitFork className="w-3.5 h-3.5" /> Tasks & DAG
            </button>

            <button
              onClick={() => setActiveTab('memory')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'memory'
                  ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-400/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Database className="w-3.5 h-3.5" /> Memory Engine
            </button>

            <button
              onClick={() => setActiveTab('plugins')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'plugins'
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Blocks className="w-3.5 h-3.5" /> Plugins & MCP
            </button>

            <button
              onClick={() => setActiveTab('router')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'router'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Network className="w-3.5 h-3.5" /> AI Router & Agents
            </button>

            <button
              onClick={() => setActiveTab('command')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'command'
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" /> Console
            </button>

            <button
              onClick={() => setActiveTab('overlay')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-all ${
                activeTab === 'overlay'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-400/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Layers className="w-3.5 h-3.5" /> Overlays
            </button>
          </div>

          {/* Modal Content Area */}
          <div className="p-4 flex-1 overflow-y-auto min-h-[360px]">
            {activeTab === 'hologram' && (
              <div className="flex flex-col items-center justify-center space-y-3 py-2">
                <div className="w-full h-[280px] bg-slate-900/60 border border-cyan-500/20 rounded-2xl flex items-center justify-center relative overflow-hidden">
                  <ThreeAvatar state={assistantState} outputVolume={outputVolume} micVolume={micVolume} />
                  <div className="absolute top-3 left-3 text-[10px] font-mono text-cyan-400 bg-black/60 px-2 py-0.5 rounded border border-cyan-500/30">
                    Real-time Holographic Projection • 60 FPS
                  </div>
                  <div className="absolute bottom-3 right-3 text-[10px] font-mono text-emerald-400 bg-black/60 px-2 py-0.5 rounded border border-emerald-500/30">
                    Lip Sync: Active • Eye Tracking: Active
                  </div>
                </div>
                <div className="text-xs text-center text-slate-400 font-mono">
                  JARVIS Blue Hologram Avatar responding to audio frequency & AI Assistant State (<span className="text-cyan-300">{assistantState}</span>)
                </div>
              </div>
            )}

            {activeTab === 'dashboard' && <SystemDashboardView />}
            {activeTab === 'enterprise' && <ProductionEnterpriseView />}
            {activeTab === 'developer' && <DeveloperEngineView />}
            {activeTab === 'tasks' && <TaskDAGView />}
            {activeTab === 'memory' && <MemoryView />}
            {activeTab === 'plugins' && <PluginMCPView />}
            {activeTab === 'router' && <ModelRouterAgentView />}
            {activeTab === 'command' && <CommandCenterView />}
            {activeTab === 'overlay' && <OverlayControlView />}
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
