import React, { useState, useEffect } from 'react';
import { Cpu, HardDrive, Zap, Wifi, Volume2, Sun, Thermometer, CloudSun, Activity, Download } from 'lucide-react';

export const SystemDashboardView: React.FC = () => {
  const [stats, setStats] = useState({
    cpuUsage: 18,
    gpuUsage: 24,
    ramUsage: 42,
    diskUsage: 58,
    temp: 46,
    battery: 92,
    wifiSignal: 95,
    volume: 75,
    brightness: 80,
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setStats({
        cpuUsage: Math.floor(15 + Math.random() * 25),
        gpuUsage: Math.floor(20 + Math.random() * 30),
        ramUsage: 42,
        diskUsage: 58,
        temp: Math.floor(44 + Math.random() * 6),
        battery: 92,
        wifiSignal: 95,
        volume: 75,
        brightness: 80,
      });
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-4 text-slate-100">
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <h3 className="text-sm font-semibold tracking-wider uppercase text-cyan-400 flex items-center gap-2">
          <Activity className="w-4 h-4 text-cyan-400" />
          KIRA System Telemetry & Performance
        </h3>
        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 rounded-full">
          60 FPS • Optimal
        </span>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* CPU */}
        <div className="bg-white/5 border border-cyan-500/20 rounded-xl p-3 backdrop-blur-md">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-cyan-400" /> CPU Core</span>
            <span className="font-mono text-cyan-300">{stats.cpuUsage}%</span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
            <div className="bg-cyan-400 h-1.5 rounded-full transition-all duration-500" style={{ width: `${stats.cpuUsage}%` }} />
          </div>
        </div>

        {/* GPU */}
        <div className="bg-white/5 border border-indigo-500/20 rounded-xl p-3 backdrop-blur-md">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="flex items-center gap-1.5"><Zap className="w-3.5 h-3.5 text-indigo-400" /> GPU Load</span>
            <span className="font-mono text-indigo-300">{stats.gpuUsage}%</span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
            <div className="bg-indigo-400 h-1.5 rounded-full transition-all duration-500" style={{ width: `${stats.gpuUsage}%` }} />
          </div>
        </div>

        {/* RAM */}
        <div className="bg-white/5 border border-purple-500/20 rounded-xl p-3 backdrop-blur-md">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="flex items-center gap-1.5"><Activity className="w-3.5 h-3.5 text-purple-400" /> RAM Memory</span>
            <span className="font-mono text-purple-300">13.4 / 32 GB ({stats.ramUsage}%)</span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
            <div className="bg-purple-400 h-1.5 rounded-full transition-all duration-500" style={{ width: `${stats.ramUsage}%` }} />
          </div>
        </div>

        {/* Disk */}
        <div className="bg-white/5 border border-emerald-500/20 rounded-xl p-3 backdrop-blur-md">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="flex items-center gap-1.5"><HardDrive className="w-3.5 h-3.5 text-emerald-400" /> NVMe Disk</span>
            <span className="font-mono text-emerald-300">{stats.diskUsage}%</span>
          </div>
          <div className="w-full bg-slate-800/80 rounded-full h-1.5 overflow-hidden">
            <div className="bg-emerald-400 h-1.5 rounded-full transition-all duration-500" style={{ width: `${stats.diskUsage}%` }} />
          </div>
        </div>
      </div>

      {/* Auxiliary Status Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-xs font-mono">
        <div className="bg-slate-900/60 border border-white/10 rounded-lg p-2.5 flex items-center justify-between">
          <span className="text-slate-400 flex items-center gap-1.5"><Thermometer className="w-3.5 h-3.5 text-rose-400" /> Temp</span>
          <span className="text-white font-semibold">{stats.temp}°C</span>
        </div>
        <div className="bg-slate-900/60 border border-white/10 rounded-lg p-2.5 flex items-center justify-between">
          <span className="text-slate-400 flex items-center gap-1.5"><Wifi className="w-3.5 h-3.5 text-blue-400" /> Wi-Fi 6</span>
          <span className="text-emerald-400 font-semibold">{stats.wifiSignal}%</span>
        </div>
        <div className="bg-slate-900/60 border border-white/10 rounded-lg p-2.5 flex items-center justify-between">
          <span className="text-slate-400 flex items-center gap-1.5"><Volume2 className="w-3.5 h-3.5 text-cyan-400" /> Master Vol</span>
          <span className="text-white font-semibold">{stats.volume}%</span>
        </div>
        <div className="bg-slate-900/60 border border-white/10 rounded-lg p-2.5 flex items-center justify-between">
          <span className="text-slate-400 flex items-center gap-1.5"><Sun className="w-3.5 h-3.5 text-amber-400" /> Display</span>
          <span className="text-white font-semibold">{stats.brightness}%</span>
        </div>
        <div className="bg-slate-900/60 border border-white/10 rounded-lg p-2.5 flex items-center justify-between">
          <span className="text-slate-400 flex items-center gap-1.5"><CloudSun className="w-3.5 h-3.5 text-sky-400" /> Weather</span>
          <span className="text-sky-300 font-semibold">21°C Sunny</span>
        </div>
      </div>

      {/* Active System Tasks */}
      <div className="bg-slate-950/60 border border-white/10 rounded-xl p-3">
        <div className="text-[11px] font-mono text-slate-400 uppercase tracking-widest mb-2 flex items-center justify-between">
          <span>Active Microservices & Background Threads</span>
          <span className="text-cyan-400">4 Active</span>
        </div>
        <div className="space-y-1.5 text-xs font-mono">
          <div className="flex items-center justify-between p-2 rounded bg-white/5 border border-white/5">
            <span>FastAPI Phase 1-6 Engine</span>
            <span className="text-emerald-400">Port 3000 • Running</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded bg-white/5 border border-white/5">
            <span>Faster Whisper Voice STT Engine</span>
            <span className="text-cyan-400">Low Latency • Ready</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded bg-white/5 border border-white/5">
            <span>ChromaDB Vector Memory Store</span>
            <span className="text-purple-400">SQLite + Embeddings</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded bg-white/5 border border-white/5">
            <span>Model Context Protocol (MCP) Client</span>
            <span className="text-amber-400">Brave + Filesystem</span>
          </div>
        </div>
      </div>
    </div>
  );
};
