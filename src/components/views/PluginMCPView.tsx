import React, { useState, useEffect } from 'react';
import { Blocks, ToggleLeft, ToggleRight, Play, ShieldCheck, Terminal, Server, CheckCircle2, RefreshCw } from 'lucide-react';

export const PluginMCPView: React.FC = () => {
  const [plugins, setPlugins] = useState<any[]>([]);
  const [mcpTools, setMcpTools] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [testOutput, setTestOutput] = useState<string | null>(null);

  const fetchPluginsAndMCP = async () => {
    setLoading(true);
    try {
      const [pRes, mRes] = await Promise.all([
        fetch('/api/plugins/list'),
        fetch('/api/mcp/tools')
      ]);
      const pData = pRes.ok ? await pRes.json() : {};
      const mData = mRes.ok ? await mRes.json() : {};

      if (pData.installed_plugins) {
        setPlugins(pData.installed_plugins);
      }
      if (mData.discovered_mcp_tools) {
        setMcpTools(mData.discovered_mcp_tools);
      }
    } catch (err) {
      console.error('Fetch plugins error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPluginsAndMCP();
  }, []);

  const handleTogglePlugin = async (pluginId: string, currentEnabled: boolean) => {
    const endpoint = currentEnabled ? '/api/plugins/disable' : '/api/plugins/enable';
    try {
      await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plugin_id: pluginId })
      });
      fetchPluginsAndMCP();
    } catch (err) {
      console.error('Toggle plugin error:', err);
    }
  };

  const handleTestExecute = async (pluginId: string, action: string) => {
    try {
      const res = await fetch('/api/plugins/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          plugin_id: pluginId,
          action: action,
          params: { repo: 'kira-ai/kira-os' },
          confirmed: true
        })
      });
      const data = await res.json();
      setTestOutput(JSON.stringify(data, null, 2));
    } catch (err) {
      console.error('Test execute error:', err);
    }
  };

  return (
    <div className="space-y-4 text-slate-100">
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <h3 className="text-sm font-semibold tracking-wider uppercase text-emerald-400 flex items-center gap-2">
          <Blocks className="w-4 h-4 text-emerald-400" />
          Plugin Ecosystem & Model Context Protocol (MCP)
        </h3>
        <button onClick={fetchPluginsAndMCP} className="p-1 text-slate-400 hover:text-white transition-colors">
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Installed Plugins Catalog */}
      <div className="space-y-2">
        <div className="text-[11px] font-mono text-slate-400 uppercase tracking-widest flex items-center justify-between">
          <span>Active Phase 6 Installed Plugins ({plugins.length})</span>
          <span className="text-emerald-400">Sandbox Protected</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 max-h-[180px] overflow-y-auto pr-1">
          {plugins.slice(0, 8).map((p) => {
            const m = p.manifest;
            return (
              <div key={m.id} className="p-3 bg-slate-950/70 border border-white/10 rounded-xl flex items-center justify-between gap-2 text-xs">
                <div>
                  <div className="font-semibold text-slate-100 flex items-center gap-1.5">
                    {m.name}
                    <span className="text-[9px] font-mono bg-white/10 px-1.5 py-0.2 rounded text-slate-300">v{m.version}</span>
                  </div>
                  <div className="text-[11px] text-slate-400 line-clamp-1">{m.description}</div>
                </div>
                <div className="flex items-center gap-1.5">
                  <button onClick={() => handleTestExecute(m.id, 'get_repo')} className="p-1 bg-white/10 hover:bg-white/20 rounded text-cyan-300" title="Run Sandbox Test">
                    <Play className="w-3.5 h-3.5" />
                  </button>
                  <button onClick={() => handleTogglePlugin(m.id, m.is_enabled)} className="text-emerald-400">
                    {m.is_enabled ? <ToggleRight className="w-6 h-6 text-emerald-400" /> : <ToggleLeft className="w-6 h-6 text-slate-600" />}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Discovered MCP Servers & Tools */}
      <div className="bg-slate-950/70 border border-white/10 rounded-xl p-3 space-y-2">
        <div className="text-[11px] font-mono text-amber-400 uppercase tracking-widest flex items-center gap-2">
          <Server className="w-3.5 h-3.5" /> Model Context Protocol (MCP) Discovered Tools
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono">
          <div className="p-2 bg-white/5 rounded border border-white/5 flex items-center justify-between">
            <span>Brave Search MCP</span>
            <span className="text-emerald-400">Connected</span>
          </div>
          <div className="p-2 bg-white/5 rounded border border-white/5 flex items-center justify-between">
            <span>Local Filesystem MCP</span>
            <span className="text-emerald-400">Connected</span>
          </div>
        </div>
      </div>

      {/* Test Execution Output Console */}
      {testOutput && (
        <div className="bg-black/90 border border-cyan-500/30 rounded-xl p-3 font-mono text-[10px] text-cyan-300 overflow-x-auto">
          <div className="text-slate-400 mb-1">Sandbox Execution Log:</div>
          <pre>{testOutput}</pre>
        </div>
      )}
    </div>
  );
};
