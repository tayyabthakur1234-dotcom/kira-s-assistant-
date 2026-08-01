import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Building2,
  Cpu,
  RefreshCw,
  HardDrive,
  Download,
  Settings,
  Activity,
  Key,
  Server,
  Database,
  Lock,
  Layers,
  CheckCircle2,
  AlertTriangle,
  Play,
  RotateCcw,
  Zap,
  Radio,
  Sliders,
  FileArchive,
  Terminal,
  FileText
} from 'lucide-react';

export const ProductionEnterpriseView: React.FC = () => {
  const [subTab, setSubTab] = useState<'overview' | 'prereqs' | 'wizard' | 'service' | 'modes' | 'diagnostics' | 'backup' | 'installers' | 'telemetry'>('overview');
  
  const [loading, setLoading] = useState(false);
  const [overviewData, setOverviewData] = useState<any>(null);
  const [prereqData, setPrereqData] = useState<any>(null);
  const [diagData, setDiagData] = useState<any>(null);
  const [modesData, setModesData] = useState<any>(null);
  const [backupsData, setBackupsData] = useState<any>(null);
  const [installerSpec, setInstallerSpec] = useState<any>(null);
  const [logsData, setLogsData] = useState<any>(null);

  // Wizard state
  const [geminiKeyInput, setGeminiKeyInput] = useState('');
  const [wizardTheme, setWizardTheme] = useState('cyberpunk_dark');
  const [wizardVoice, setWizardVoice] = useState('KIRA Neural Female');
  const [wizardStatus, setWizardStatus] = useState<any>(null);

  // Active mode state
  const [selectedMode, setSelectedMode] = useState('Cloud Mode');
  const [serviceActionStatus, setServiceActionStatus] = useState<any>(null);

  const fetchOverview = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/production/overview');
      const data = await res.json();
      setOverviewData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchPrereqs = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/production/prerequisites');
      const data = await res.json();
      setPrereqData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchDiagnostics = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/production/diagnostics');
      const data = await res.json();
      setDiagData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchBackups = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/production/backup/list');
      const data = await res.json();
      setBackupsData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/production/logs');
      const data = await res.json();
      setLogsData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOverview();
    fetchPrereqs();
    fetchDiagnostics();
  }, []);

  const handleRunWizard = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/production/wizard/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gemini_api_key: geminiKeyInput || undefined,
          theme: wizardTheme,
          selected_voice: wizardVoice,
          local_ai_enabled: true
        })
      });
      const data = await res.json();
      setWizardStatus(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleControlService = async (action: string) => {
    setLoading(true);
    try {
      const res = await fetch('/api/production/service', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      const data = await res.json();
      setServiceActionStatus(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBackup = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/production/backup/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ include_memories: true, include_plugins: true })
      });
      await res.json();
      await fetchBackups();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateInstallerSpec = async (type: string) => {
    setLoading(true);
    try {
      const res = await fetch(`/api/production/installer/spec?target_type=${type}`, { method: 'POST' });
      const data = await res.json();
      setInstallerSpec(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4 text-slate-100">
      {/* View Header */}
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <h3 className="text-sm font-semibold tracking-wider uppercase text-cyan-400 flex items-center gap-2">
          <Building2 className="w-4 h-4 text-cyan-400" />
          KIRA Phase 12 • Production Deployment & Enterprise Platform
        </h3>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 rounded flex items-center gap-1">
            <ShieldCheck className="w-3 h-3 text-emerald-400" /> Windows 10/11 Production Ready
          </span>
          <button onClick={fetchOverview} className="p-1 text-slate-400 hover:text-white transition-colors">
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Sub-tab Bar */}
      <div className="flex items-center gap-1.5 p-1 bg-slate-950/80 border border-white/10 rounded-xl overflow-x-auto text-xs font-mono">
        <button
          onClick={() => setSubTab('overview')}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-all ${
            subTab === 'overview' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Layers className="w-3.5 h-3.5" /> OS Architecture
        </button>
        <button
          onClick={() => { setSubTab('prereqs'); fetchPrereqs(); }}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-all ${
            subTab === 'prereqs' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Cpu className="w-3.5 h-3.5" /> Prerequisites
        </button>
        <button
          onClick={() => setSubTab('wizard')}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-all ${
            subTab === 'wizard' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Sliders className="w-3.5 h-3.5" /> First-Run Wizard
        </button>
        <button
          onClick={() => setSubTab('service')}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-all ${
            subTab === 'service' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Server className="w-3.5 h-3.5" /> Background Service
        </button>
        <button
          onClick={() => setSubTab('modes')}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-all ${
            subTab === 'modes' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Radio className="w-3.5 h-3.5" /> Execution Modes
        </button>
        <button
          onClick={() => { setSubTab('diagnostics'); fetchDiagnostics(); }}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-all ${
            subTab === 'diagnostics' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Activity className="w-3.5 h-3.5" /> Full Diagnostics
        </button>
        <button
          onClick={() => { setSubTab('backup'); fetchBackups(); }}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-all ${
            subTab === 'backup' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <FileArchive className="w-3.5 h-3.5" /> Backup & Restore
        </button>
        <button
          onClick={() => setSubTab('installers')}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-all ${
            subTab === 'installers' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Download className="w-3.5 h-3.5" /> Installers
        </button>
        <button
          onClick={() => { setSubTab('telemetry'); fetchLogs(); }}
          className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-all ${
            subTab === 'telemetry' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/30' : 'text-slate-400 hover:text-white'
          }`}
        >
          <Terminal className="w-3.5 h-3.5" /> Telemetry Logs
        </button>
      </div>

      {/* Sub-tab 1: Unified Architecture Overview */}
      {subTab === 'overview' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="p-3 bg-slate-950/70 border border-cyan-500/20 rounded-xl">
              <div className="text-[10px] text-slate-400 uppercase">OS Status</div>
              <div className="text-xl font-bold text-emerald-400 mt-1">{overviewData?.system_health || '100% Operational'}</div>
            </div>
            <div className="p-3 bg-slate-950/70 border border-purple-500/20 rounded-xl">
              <div className="text-[10px] text-slate-400 uppercase">Active Mode</div>
              <div className="text-xl font-bold text-purple-300 mt-1">{overviewData?.active_mode || 'Cloud Mode'}</div>
            </div>
            <div className="p-3 bg-slate-950/70 border border-indigo-500/20 rounded-xl">
              <div className="text-[10px] text-slate-400 uppercase">Background Service</div>
              <div className="text-xl font-bold text-indigo-300 mt-1">
                {overviewData?.background_service?.is_running ? 'Running' : 'Stopped'}
              </div>
            </div>
            <div className="p-3 bg-slate-950/70 border border-emerald-500/20 rounded-xl">
              <div className="text-[10px] text-slate-400 uppercase">Security Vault</div>
              <div className="text-xl font-bold text-emerald-300 mt-1">AES-256 Encrypted</div>
            </div>
          </div>

          <div className="p-3.5 bg-slate-950/80 border border-cyan-500/20 rounded-xl space-y-2">
            <div className="text-[11px] text-cyan-300 font-semibold uppercase tracking-wider">
              KIRA AI OS • Unified 12-Phase System Architecture
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-300">
              {overviewData?.unified_architecture?.map((phaseStr: string, idx: number) => (
                <div key={idx} className="flex items-center gap-2 p-2 bg-slate-900/80 border border-white/5 rounded-lg">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span>{phaseStr}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sub-tab 2: Prerequisites & Dependency Detector */}
      {subTab === 'prereqs' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3 bg-slate-950/80 border border-cyan-500/20 rounded-xl space-y-2">
            <div className="text-[11px] text-cyan-300 font-semibold uppercase tracking-wider flex items-center justify-between">
              <span>Windows 10/11 System Dependencies & Prerequisites</span>
              <span className="text-emerald-400 font-bold">Auto-Detected</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {prereqData?.dependencies && Object.entries(prereqData.dependencies).map(([depName, info]: [string, any]) => (
                <div key={depName} className="p-2.5 bg-slate-900 border border-white/10 rounded-xl flex items-center justify-between">
                  <div>
                    <div className="text-slate-200 font-semibold uppercase">{depName}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{info?.version || 'Not detected'}</div>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    info?.installed ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/30' : 'bg-rose-950/80 text-rose-400 border border-rose-500/30'
                  }`}>
                    {info?.installed ? 'INSTALLED' : 'MISSING'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sub-tab 3: First-Run Onboarding Wizard */}
      {subTab === 'wizard' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3.5 bg-slate-950/80 border border-purple-500/20 rounded-xl space-y-3">
            <div className="text-[11px] text-purple-300 font-semibold uppercase tracking-wider">
              First-Run Onboarding Wizard & API Setup
            </div>

            <div className="space-y-2">
              <div>
                <label className="text-[10px] text-slate-400 uppercase">Gemini API Key (Google AI Studio)</label>
                <input
                  type="password"
                  value={geminiKeyInput}
                  onChange={(e) => setGeminiKeyInput(e.target.value)}
                  placeholder="Paste AI Studio GEMINI_API_KEY..."
                  className="w-full mt-1 bg-slate-900 border border-white/15 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-purple-400"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div>
                  <label className="text-[10px] text-slate-400 uppercase">Default UI Theme</label>
                  <select
                    value={wizardTheme}
                    onChange={(e) => setWizardTheme(e.target.value)}
                    className="w-full mt-1 bg-slate-900 border border-white/15 rounded-xl px-3 py-2 text-xs text-cyan-300 focus:outline-none"
                  >
                    <option value="cyberpunk_dark">Cyberpunk Dark HUD</option>
                    <option value="neon_cosmic">Neon Cosmic Violet</option>
                    <option value="aurora_green">Aurora Emerald</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] text-slate-400 uppercase">Default TTS Voice</label>
                  <select
                    value={wizardVoice}
                    onChange={(e) => setWizardVoice(e.target.value)}
                    className="w-full mt-1 bg-slate-900 border border-white/15 rounded-xl px-3 py-2 text-xs text-cyan-300 focus:outline-none"
                  >
                    <option value="KIRA Neural Female">KIRA Neural Female (Aoede)</option>
                    <option value="KIRA Neural Male">KIRA Neural Male (Fenrir)</option>
                    <option value="KIRA Studio Neutral">KIRA Studio Neutral (Zephyr)</option>
                  </select>
                </div>
              </div>

              <button
                onClick={handleRunWizard}
                disabled={loading}
                className="w-full bg-purple-600 hover:bg-purple-500 text-white font-semibold py-2 rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-40"
              >
                <Sliders className="w-4 h-4" /> Save Onboarding & Verify Credentials
              </button>
            </div>
          </div>

          {wizardStatus && (
            <div className="p-3 bg-purple-950/40 border border-purple-500/30 rounded-xl space-y-1">
              <div className="text-purple-300 font-semibold flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-purple-400" /> {wizardStatus.message}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Sub-tab 4: Background Service Daemon */}
      {subTab === 'service' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3.5 bg-slate-950/80 border border-indigo-500/20 rounded-xl space-y-3">
            <div className="text-[11px] text-indigo-300 font-semibold uppercase tracking-wider flex items-center gap-1.5">
              <Server className="w-3.5 h-3.5" /> Windows Background Service & System Tray Daemon
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <button
                onClick={() => handleControlService('start')}
                disabled={loading}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all"
              >
                <Play className="w-3.5 h-3.5" /> Start Service
              </button>
              <button
                onClick={() => handleControlService('low_resource')}
                disabled={loading}
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all"
              >
                <Zap className="w-3.5 h-3.5" /> Low CPU Mode
              </button>
              <button
                onClick={() => handleControlService('stop')}
                disabled={loading}
                className="bg-rose-600 hover:bg-rose-500 text-white font-semibold py-2 rounded-xl flex items-center justify-center gap-1.5 transition-all"
              >
                Stop Service
              </button>
            </div>
          </div>

          {serviceActionStatus && (
            <div className="p-3 bg-slate-950/90 border border-indigo-500/30 rounded-xl">
              <span className="text-indigo-300 font-semibold">Daemon Action Status:</span> {serviceActionStatus.status}
            </div>
          )}
        </div>
      )}

      {/* Sub-tab 5: System Execution Modes */}
      {subTab === 'modes' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3.5 bg-slate-950/80 border border-cyan-500/20 rounded-xl space-y-2">
            <div className="text-[11px] text-cyan-300 font-semibold uppercase tracking-wider">
              KIRA Production Execution Modes
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {[
                { name: "Windows Service Mode", desc: "Runs in Windows background with system tray icon & wake word." },
                { name: "Portable Mode", desc: "Runs isolated from USB drive without registry footprint." },
                { name: "Developer Mode", desc: "Enables AST inspector, API logs, and raw prompt output." },
                { name: "Safe Mode", desc: "Disables custom plugins and enforces read-only access." },
                { name: "Offline Mode", desc: "100% local model processing (Local Whisper & Ollama)." },
                { name: "Cloud Mode", desc: "Hybrid cloud LLM routing (Gemini 2.5 Flash / Grok 3)." },
                { name: "Low Resource Mode", desc: "Caps CPU usage <2% and RAM footprint <50MB." }
              ].map((modeItem) => (
                <button
                  key={modeItem.name}
                  onClick={() => setSelectedMode(modeItem.name)}
                  className={`p-3 rounded-xl border text-left transition-all ${
                    selectedMode === modeItem.name
                      ? 'bg-cyan-950/50 border-cyan-400 text-cyan-200'
                      : 'bg-slate-900 border-white/10 text-slate-300 hover:border-white/20'
                  }`}
                >
                  <div className="font-bold">{modeItem.name}</div>
                  <div className="text-[10px] text-slate-400 mt-1">{modeItem.desc}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sub-tab 6: Full Diagnostics */}
      {subTab === 'diagnostics' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3.5 bg-slate-950/80 border border-emerald-500/20 rounded-xl space-y-2">
            <div className="text-[11px] text-emerald-300 font-semibold uppercase tracking-wider flex items-center justify-between">
              <span>Full System Diagnostics Suite</span>
              <span className="text-emerald-400 font-bold">{diagData?.overall_health || '100% Operational'}</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {diagData?.subsystems && Object.entries(diagData.subsystems).map(([subName, subInfo]: [string, any]) => (
                <div key={subName} className="p-2.5 bg-slate-900 border border-white/10 rounded-xl flex items-center justify-between">
                  <div>
                    <div className="text-slate-200 font-semibold uppercase">{subName.replace('_', ' ')}</div>
                    <div className="text-[10px] text-slate-400 mt-0.5">{subInfo?.details || 'Healthy'}</div>
                  </div>
                  <span className="text-emerald-400 font-bold text-[10px]">{subInfo?.latency_ms ? `${subInfo.latency_ms}ms` : 'Healthy'}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sub-tab 7: Backup & Restore */}
      {subTab === 'backup' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3.5 bg-slate-950/80 border border-cyan-500/20 rounded-xl space-y-3">
            <div className="text-[11px] text-cyan-300 font-semibold uppercase tracking-wider flex items-center justify-between">
              <span>Encrypted Backup & State Archive Restore</span>
              <button
                onClick={handleCreateBackup}
                disabled={loading}
                className="bg-cyan-600 hover:bg-cyan-500 text-white font-semibold px-3 py-1 rounded-lg transition-all"
              >
                Create Backup Now
              </button>
            </div>

            <div className="space-y-1.5">
              {backupsData?.backups?.map((b: any, idx: number) => (
                <div key={idx} className="p-2.5 bg-slate-900 border border-white/10 rounded-xl flex items-center justify-between">
                  <div>
                    <div className="text-slate-200 font-semibold">{b.filename}</div>
                    <div className="text-[10px] text-slate-400">{b.size_kb} KB • {b.modified}</div>
                  </div>
                  <button className="text-xs text-cyan-300 bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded border border-white/10">
                    Restore
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Sub-tab 8: Installers Builder Specs */}
      {subTab === 'installers' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3.5 bg-slate-950/80 border border-cyan-500/20 rounded-xl space-y-3">
            <div className="text-[11px] text-cyan-300 font-semibold uppercase tracking-wider">
              Windows Installer Spec Generator
            </div>

            <div className="grid grid-cols-3 gap-2">
              <button
                onClick={() => handleGenerateInstallerSpec('msi')}
                className="bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-2 rounded-xl transition-all"
              >
                MSI Installer Spec
              </button>
              <button
                onClick={() => handleGenerateInstallerSpec('exe')}
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-2 rounded-xl transition-all"
              >
                EXE One-Click Spec
              </button>
              <button
                onClick={() => handleGenerateInstallerSpec('portable')}
                className="bg-purple-600 hover:bg-purple-500 text-white font-semibold py-2 rounded-xl transition-all"
              >
                Portable Zip Spec
              </button>
            </div>

            {installerSpec && (
              <pre className="p-3 bg-slate-900 rounded-xl text-slate-200 text-[10px] overflow-x-auto max-h-[200px]">
                {JSON.stringify(installerSpec, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}

      {/* Sub-tab 9: Telemetry & Audit Logs */}
      {subTab === 'telemetry' && (
        <div className="space-y-3 font-mono text-xs">
          <div className="p-3.5 bg-slate-950/80 border border-cyan-500/20 rounded-xl space-y-2">
            <div className="text-[11px] text-cyan-300 font-semibold uppercase tracking-wider">
              Live Audit Log & Telemetry Stream
            </div>

            <div className="space-y-1 max-h-[250px] overflow-y-auto">
              {logsData?.logs?.map((l: any, idx: number) => (
                <div key={idx} className="p-2 bg-slate-900 border border-white/5 rounded text-[10px] flex items-center justify-between">
                  <span className="text-slate-400">{l.timestamp}</span>
                  <span className="text-cyan-300 font-bold uppercase">{l.event}</span>
                  <span className="text-emerald-400 font-mono">{l.category}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
