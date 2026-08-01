import React from 'react';
import { motion } from 'motion/react';
import { Settings, Brain, Monitor, Cpu } from 'lucide-react';
import { AssistantState, ThemeMode, VoiceSettings } from '../types';
import { THEMES } from '../lib/theme';

interface HeaderHUDProps {
  state: AssistantState;
  theme: ThemeMode;
  voiceSettings: VoiceSettings;
  isSharingScreen?: boolean;
  onOpenSettings: () => void;
  onOpenBrain?: () => void;
  onOpenOSDashboard?: () => void;
  onToggleScreenShare?: () => void;
}

export const HeaderHUD: React.FC<HeaderHUDProps> = ({
  state,
  theme,
  voiceSettings,
  isSharingScreen = false,
  onOpenSettings,
  onOpenBrain,
  onOpenOSDashboard,
  onToggleScreenShare,
}) => {
  const themeConfig = THEMES[theme];

  return (
    <header className="w-full max-w-5xl mx-auto px-6 pt-6 pb-2 flex items-center justify-between z-20">
      {/* Brand Title */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-fuchsia-500 flex items-center justify-center shadow-[0_0_25px_rgba(99,102,241,0.5)]">
          <div className="w-4 h-4 bg-white rounded-full animate-pulse"></div>
        </div>
        <div className="flex flex-col">
          <span className="text-2xl font-bold tracking-tighter text-white font-sans flex items-center gap-1.5">
            Kira's
            <span className="text-[10px] font-mono font-medium px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
              JARVIS OS CORE
            </span>
          </span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-3">
        {/* Phase 7 OS Dashboard & 3D Hologram Button */}
        {onOpenOSDashboard && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onOpenOSDashboard}
            className="px-3.5 py-1.5 rounded-full bg-cyan-600/30 hover:bg-cyan-600/50 backdrop-blur-md border border-cyan-400/40 flex items-center space-x-1.5 text-cyan-200 text-xs font-mono transition-all shadow-lg cursor-pointer ring-1 ring-cyan-400/30"
            title="Open Phase 7 JARVIS OS Dashboard & 3D Avatar"
          >
            <Cpu className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            <span className="font-semibold hidden sm:inline">KIRA OS Core</span>
          </motion.button>
        )}

        {/* Screen Share Vision Button */}
        {onToggleScreenShare && (
          <motion.button
            type="button"
            id="screen-share-btn"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={(e) => {
              e.stopPropagation();
              onToggleScreenShare();
            }}
            className={`px-3.5 py-1.5 rounded-full backdrop-blur-md border flex items-center space-x-2 text-xs font-mono transition-all shadow-lg cursor-pointer ${
              isSharingScreen
                ? 'bg-red-600/30 border-red-500/60 text-red-200 animate-pulse ring-2 ring-red-500/30'
                : 'bg-indigo-600/20 hover:bg-indigo-600/30 border-indigo-500/40 text-indigo-200 hover:text-white'
            }`}
            title={isSharingScreen ? 'Kira Screen Vision Active - Click to stop' : 'Share Screen with Kira'}
          >
            <Monitor className={`w-3.5 h-3.5 ${isSharingScreen ? 'text-red-400' : 'text-indigo-400'}`} />
            <span className="font-semibold">
              {isSharingScreen ? 'Vision Active' : 'Share Screen'}
            </span>
          </motion.button>
        )}

        {/* Session Status Pill */}
        <div className="bg-white/5 backdrop-blur-md border border-white/10 px-3.5 py-1.5 rounded-full flex items-center space-x-2 shadow-lg">
          <div
            className={`w-2 h-2 rounded-full ${
              state === 'disconnected' ? 'bg-slate-500' : 'bg-emerald-400 animate-ping'
            }`}
          />
          <span
            className={`text-[11px] uppercase tracking-widest font-semibold hidden md:inline ${
              state === 'disconnected' ? 'text-slate-400' : 'text-emerald-100'
            }`}
          >
            {state === 'disconnected' ? 'Offline' : 'Session Live'}
          </span>
        </div>

        {/* Voice Info Pill */}
        <div className="hidden lg:flex bg-white/5 backdrop-blur-md border border-white/10 px-3.5 py-1.5 rounded-full items-center space-x-2">
          <span className="text-[11px] uppercase tracking-widest text-white/60">Voice</span>
          <span className="text-[11px] font-mono text-indigo-300 font-semibold">
            {voiceSettings.voice}
          </span>
        </div>

        {/* Brain Modal Button */}
        {onOpenBrain && (
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onOpenBrain}
            className="px-3 py-1.5 rounded-full bg-indigo-600/30 hover:bg-indigo-600/50 backdrop-blur-md border border-indigo-500/40 flex items-center space-x-1.5 text-indigo-200 text-xs font-mono transition-all shadow-lg"
            aria-label="Kira's Brain"
            title="Open Kira's Persistent Memory Brain"
          >
            <Brain className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
            <span className="hidden sm:inline">Brain</span>
          </motion.button>
        )}

        {/* Settings Modal Button */}
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={onOpenSettings}
          className="w-9 h-9 rounded-full bg-white/5 backdrop-blur-md border border-white/10 flex items-center justify-center text-slate-300 hover:text-white hover:border-white/20 transition-all"
          aria-label="Open Settings"
        >
          <Settings className="w-4 h-4" />
        </motion.button>
      </div>
    </header>
  );
};


