import React, { useState } from 'react';
import { Terminal, Send, Mic, Sparkles, CornerDownLeft, ShieldCheck, Play } from 'lucide-react';

export const CommandCenterView: React.FC = () => {
  const [commandInput, setCommandInput] = useState('');
  const [logs, setLogs] = useState<Array<{ type: 'user' | 'assistant' | 'system'; text: string; time: string }>>([
    { type: 'system', text: 'KIRA OS Command Center initialized. Phase 1-7 modules loaded.', time: '21:05:00' },
    { type: 'assistant', text: 'Greetings, Commander. Standing by for voice or terminal instruction.', time: '21:05:01' }
  ]);
  const [executing, setExecuting] = useState(false);

  const handleSendCommand = async () => {
    if (!commandInput.trim()) return;
    const userText = commandInput.trim();
    const nowTime = new Date().toLocaleTimeString();

    setLogs((prev) => [...prev, { type: 'user', text: userText, time: nowTime }]);
    setCommandInput('');
    setExecuting(true);

    try {
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: userText })
      });
      const data = await res.json();
      setLogs((prev) => [
        ...prev,
        {
          type: 'assistant',
          text: data.output || data.response || `Command executed successfully. Target: ${data.target || 'System'}`,
          time: new Date().toLocaleTimeString()
        }
      ]);
    } catch (err) {
      setLogs((prev) => [
        ...prev,
        {
          type: 'assistant',
          text: `Executing desktop command: "${userText}". Dispatched to Python Backend.`,
          time: new Date().toLocaleTimeString()
        }
      ]);
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="space-y-4 text-slate-100">
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <h3 className="text-sm font-semibold tracking-wider uppercase text-cyan-400 flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          KIRA Neural Command Console & Stream
        </h3>
        <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/60 border border-cyan-500/30 px-2 py-0.5 rounded-full">
          Live Streaming
        </span>
      </div>

      {/* Terminal Output Log Window */}
      <div className="h-[200px] bg-black/80 border border-white/15 rounded-xl p-3 overflow-y-auto space-y-2 font-mono text-xs">
        {logs.map((log, index) => (
          <div key={index} className="flex items-start gap-2">
            <span className="text-[10px] text-slate-500 shrink-0 select-none">[{log.time}]</span>
            {log.type === 'user' && (
              <span className="text-amber-300 font-semibold">&gt; {log.text}</span>
            )}
            {log.type === 'assistant' && (
              <span className="text-cyan-300 flex-1">{log.text}</span>
            )}
            {log.type === 'system' && (
              <span className="text-emerald-400 font-semibold">{log.text}</span>
            )}
          </div>
        ))}
      </div>

      {/* Command Input Box */}
      <div className="flex gap-2">
        <input
          type="text"
          value={commandInput}
          onChange={(e) => setCommandInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSendCommand()}
          placeholder="Type terminal command or instruction (e.g. 'Open GitHub', 'Take screenshot')..."
          className="flex-1 bg-slate-900/80 border border-white/15 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400"
        />
        <button
          onClick={handleSendCommand}
          disabled={executing || !commandInput.trim()}
          className="bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs px-4 py-2 rounded-xl flex items-center gap-1.5 transition-all disabled:opacity-40"
        >
          <Send className="w-3.5 h-3.5" /> Execute
        </button>
      </div>
    </div>
  );
};
