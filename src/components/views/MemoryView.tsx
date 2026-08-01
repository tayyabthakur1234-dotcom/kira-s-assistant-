import React, { useState, useEffect } from 'react';
import { Database, Search, Plus, Trash2, Tag, Bookmark, Download, RefreshCw } from 'lucide-react';

export const MemoryView: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [memories, setMemories] = useState<any[]>([
    { id: 'mem_01', text: 'User prefers dark blue holographic neon theme for KIRA OS.', category: 'preference', importance: 'High', date: '2026-07-31' },
    { id: 'mem_02', text: 'Project KIRA AI Phase 6 Plugin & MCP integration deployed.', category: 'project', importance: 'Critical', date: '2026-07-31' },
    { id: 'mem_03', text: 'Git repository URL is kira-ai/kira-os on GitHub.', category: 'device', importance: 'Medium', date: '2026-07-30' },
  ]);
  const [newMemoryText, setNewMemoryText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/memory/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: searchQuery, top_k: 5 })
      });
      const data = res.ok ? await res.json() : {};
      if (data.status === 'success' && data.memories) {
        setMemories(data.memories.map((m: any) => ({
          id: m.id || 'mem_res',
          text: m.text,
          category: m.category || 'general',
          importance: m.importance || 'Medium',
          date: new Date().toISOString().split('T')[0]
        })));
      }
    } catch (err) {
      console.error('Memory search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStore = async () => {
    if (!newMemoryText.trim()) return;
    try {
      const res = await fetch('/api/memory/store', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: newMemoryText, category: 'preference', importance: 'High' })
      });
      const data = res.ok ? await res.json() : {};
      if (data.status === 'success') {
        setMemories((prev) => [
          { id: data.memory_id || `mem_${Date.now()}`, text: newMemoryText, category: 'preference', importance: 'High', date: new Date().toISOString().split('T')[0] },
          ...prev
        ]);
        setNewMemoryText('');
      }
    } catch (err) {
      console.error('Memory store error:', err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await fetch('/api/memory/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
      });
      setMemories((prev) => prev.filter((m) => m.id !== id));
    } catch (err) {
      console.error('Memory delete error:', err);
    }
  };

  return (
    <div className="space-y-4 text-slate-100">
      <div className="flex items-center justify-between border-b border-white/10 pb-2">
        <h3 className="text-sm font-semibold tracking-wider uppercase text-cyan-400 flex items-center gap-2">
          <Database className="w-4 h-4 text-cyan-400" />
          KIRA Long-Term Memory & Vector Index
        </h3>
        <span className="text-[10px] font-mono text-cyan-300 bg-cyan-950/60 border border-cyan-500/30 px-2 py-0.5 rounded-full">
          SQLite + Vector Embeddings
        </span>
      </div>

      {/* Search & Store Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Search */}
        <div className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Semantic vector search memories..."
            className="flex-1 bg-slate-900/80 border border-white/15 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-cyan-400"
          />
          <button onClick={handleSearch} className="bg-cyan-600 hover:bg-cyan-500 text-white font-mono text-xs px-3 py-2 rounded-xl flex items-center gap-1">
            <Search className="w-3.5 h-3.5" /> Search
          </button>
        </div>

        {/* Store */}
        <div className="flex gap-2">
          <input
            type="text"
            value={newMemoryText}
            onChange={(e) => setNewMemoryText(e.target.value)}
            placeholder="Add new persistent memory..."
            className="flex-1 bg-slate-900/80 border border-white/15 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-emerald-400"
          />
          <button onClick={handleStore} className="bg-emerald-600 hover:bg-emerald-500 text-white font-mono text-xs px-3 py-2 rounded-xl flex items-center gap-1">
            <Plus className="w-3.5 h-3.5" /> Store
          </button>
        </div>
      </div>

      {/* Memories List */}
      <div className="space-y-2 max-h-[220px] overflow-y-auto pr-1">
        {memories.map((mem) => (
          <div key={mem.id} className="p-3 bg-slate-950/70 border border-white/10 rounded-xl flex items-start justify-between gap-3 text-xs">
            <div className="space-y-1">
              <div className="text-slate-200">{mem.text}</div>
              <div className="flex items-center gap-2 text-[10px] font-mono text-slate-400">
                <span className="bg-white/5 border border-white/10 px-2 py-0.5 rounded text-cyan-300">{mem.category}</span>
                <span className="bg-white/5 border border-white/10 px-2 py-0.5 rounded text-amber-300">{mem.importance}</span>
                <span>{mem.date}</span>
              </div>
            </div>
            <button onClick={() => handleDelete(mem.id)} className="p-1 text-slate-400 hover:text-rose-400 transition-colors">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
