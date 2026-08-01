import React, { useState } from 'react';
import { Layers, Eye, Shield, Sliders, Monitor, Maximize2, Minimize2, Sparkles } from 'lucide-react';

export const OverlayControlView: React.FC = () => {
  const [clickThrough, setClickThrough] = useState(false);
  const [alwaysOnTop, setAlwaysOnTop] = useState(true);
  const [transparency, setTransparency] = useState(85);
  const [showCursorPath, setShowCursorPath] = useState(true);
  const [highlightTargets, setHighlightTargets] = useState(true);

  return (
    <div className="space-y-4 text-slate-100">
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <h3 className="text-sm font-semibold tracking-wider uppercase text-amber-400 flex items-center gap-2">
          <Layers className="w-4 h-4 text-amber-400" />
          Desktop Overlay & Window Geometry Settings
        </h3>
        <span className="text-[10px] font-mono text-amber-300 bg-amber-950/60 border border-amber-500/30 px-2 py-0.5 rounded-full">
          Electron Framing
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
        {/* Click Through Toggle */}
        <div className="bg-slate-950/70 border border-white/10 rounded-xl p-3 flex items-center justify-between">
          <div>
            <div className="font-semibold text-slate-100">Click-Through Mode</div>
            <div className="text-[11px] text-slate-400">Pass mouse clicks directly to underlying desktop applications</div>
          </div>
          <button
            onClick={() => setClickThrough(!clickThrough)}
            className={`px-3 py-1 rounded-lg font-mono text-xs transition-colors ${
              clickThrough ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400'
            }`}
          >
            {clickThrough ? 'ENABLED' : 'DISABLED'}
          </button>
        </div>

        {/* Always On Top Toggle */}
        <div className="bg-slate-950/70 border border-white/10 rounded-xl p-3 flex items-center justify-between">
          <div>
            <div className="font-semibold text-slate-100">Always-On-Top Layer</div>
            <div className="text-[11px] text-slate-400">Floating JARVIS HUD above all open windows</div>
          </div>
          <button
            onClick={() => setAlwaysOnTop(!alwaysOnTop)}
            className={`px-3 py-1 rounded-lg font-mono text-xs transition-colors ${
              alwaysOnTop ? 'bg-cyan-600 text-white' : 'bg-slate-800 text-slate-400'
            }`}
          >
            {alwaysOnTop ? 'ENABLED' : 'DISABLED'}
          </button>
        </div>

        {/* Highlight Targets */}
        <div className="bg-slate-950/70 border border-white/10 rounded-xl p-3 flex items-center justify-between">
          <div>
            <div className="font-semibold text-slate-100">Show Vision Target Bounding Boxes</div>
            <div className="text-[11px] text-slate-400">Highlight UI elements during automated desktop execution</div>
          </div>
          <button
            onClick={() => setHighlightTargets(!highlightTargets)}
            className={`px-3 py-1 rounded-lg font-mono text-xs transition-colors ${
              highlightTargets ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
            }`}
          >
            {highlightTargets ? 'ENABLED' : 'DISABLED'}
          </button>
        </div>

        {/* Cursor Trail */}
        <div className="bg-slate-950/70 border border-white/10 rounded-xl p-3 flex items-center justify-between">
          <div>
            <div className="font-semibold text-slate-100">Holographic Cursor Trail</div>
            <div className="text-[11px] text-slate-400">Draw particle path during automated mouse movements</div>
          </div>
          <button
            onClick={() => setShowCursorPath(!showCursorPath)}
            className={`px-3 py-1 rounded-lg font-mono text-xs transition-colors ${
              showCursorPath ? 'bg-purple-600 text-white' : 'bg-slate-800 text-slate-400'
            }`}
          >
            {showCursorPath ? 'ENABLED' : 'DISABLED'}
          </button>
        </div>
      </div>

      {/* Glassmorphism Transparency Slider */}
      <div className="bg-slate-950/70 border border-white/10 rounded-xl p-3 space-y-2">
        <div className="flex justify-between text-xs font-mono">
          <span className="text-slate-300">Glass Transparency Index</span>
          <span className="text-amber-300">{transparency}%</span>
        </div>
        <input
          type="range"
          min="20"
          max="100"
          value={transparency}
          onChange={(e) => setTransparency(Number(e.target.value))}
          className="w-full accent-amber-400 bg-slate-800 rounded-lg cursor-pointer h-1.5"
        />
      </div>
    </div>
  );
};
