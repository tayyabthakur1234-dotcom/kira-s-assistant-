import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Brain,
  Search,
  Plus,
  Trash2,
  X,
  Sparkles,
  ShieldAlert,
  User,
  Heart,
  Users,
  FolderGit2,
  Target,
  Clock,
  Cpu,
  MessageSquare,
  Smile,
  RefreshCw,
} from 'lucide-react';
import { MemoryItem, MemoryCategory, ImportanceLevel } from '../types';

interface BrainModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const CATEGORIES: { id: MemoryCategory | 'all'; label: string; icon: React.FC<{ className?: string }> }[] = [
  { id: 'all', label: 'All Memories', icon: Brain },
  { id: 'identity', label: 'Identity', icon: User },
  { id: 'preference', label: 'Preferences', icon: Heart },
  { id: 'relationship', label: 'Relationships', icon: Users },
  { id: 'project', label: 'Projects', icon: FolderGit2 },
  { id: 'goal', label: 'Goals', icon: Target },
  { id: 'routine', label: 'Routines', icon: Clock },
  { id: 'device', label: 'Devices', icon: Cpu },
  { id: 'conversation', label: 'Key Decisions', icon: MessageSquare },
  { id: 'emotional', label: 'Traits & Moods', icon: Smile },
];

export const BrainModal: React.FC<BrainModalProps> = ({ isOpen, onClose }) => {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState<MemoryCategory | 'all'>('all');
  const [isAdding, setIsAdding] = useState(false);

  // New Memory Form State
  const [newTitle, setNewTitle] = useState('');
  const [newCategory, setNewCategory] = useState<MemoryCategory>('identity');
  const [newValue, setNewValue] = useState('');
  const [newImportance, setNewImportance] = useState<ImportanceLevel>('Medium');
  const [newConfidence, setNewConfidence] = useState(90);

  const fetchMemories = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/memories');
      const data = await res.json();
      if (data.memories) {
        setMemories(data.memories);
      }
    } catch (e) {
      console.error('Failed to load memories:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchMemories();
    }
  }, [isOpen]);

  const handleDeleteMemory = async (id: string) => {
    try {
      await fetch(`/api/memories/${id}`, { method: 'DELETE' });
      setMemories((prev) => prev.filter((m) => m.id !== id));
    } catch (e) {
      console.error('Failed to delete memory:', e);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm("Are you sure you want to wipe Kira's entire memory brain? This cannot be undone.")) {
      return;
    }
    try {
      await fetch('/api/memories/forget', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ deleteAll: true }),
      });
      setMemories([]);
    } catch (e) {
      console.error('Failed to wipe brain:', e);
    }
  };

  const handleAddMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newValue.trim()) return;

    try {
      const res = await fetch('/api/memories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newTitle,
          category: newCategory,
          value: newValue,
          importance: newImportance,
          confidence: newConfidence,
          summary: `${newTitle}: ${newValue}`,
        }),
      });
      const data = await res.json();
      if (data.memory) {
        setMemories((prev) => [data.memory, ...prev]);
        setNewTitle('');
        setNewValue('');
        setIsAdding(false);
      }
    } catch (e) {
      console.error('Failed to add memory:', e);
    }
  };

  const filteredMemories = memories.filter((m) => {
    const matchesCat = activeCategory === 'all' || m.category === activeCategory;
    const q = searchQuery.toLowerCase();
    const matchesSearch =
      !q ||
      m.title.toLowerCase().includes(q) ||
      m.value.toLowerCase().includes(q) ||
      m.category.toLowerCase().includes(q) ||
      m.tags.some((t) => t.toLowerCase().includes(q));
    return matchesCat && matchesSearch;
  });

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="w-full max-w-4xl max-h-[85vh] bg-slate-900/95 border border-indigo-500/30 rounded-3xl shadow-2xl flex flex-col overflow-hidden"
        >
          {/* Header */}
          <div className="px-6 py-5 border-b border-white/10 flex items-center justify-between bg-gradient-to-r from-indigo-950/60 to-fuchsia-950/60">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-2xl bg-indigo-500/20 border border-indigo-400/30 flex items-center justify-center text-indigo-400">
                <Brain className="w-5 h-5 animate-pulse" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  Kira's Memory Brain
                  <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                    Persistent Facts
                  </span>
                </h2>
                <p className="text-xs text-slate-400">
                  Everything Kira has learned about you across conversations.
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <button
                onClick={fetchMemories}
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 border border-white/10 text-xs transition-all"
                title="Refresh Memory"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
              <button
                onClick={() => setIsAdding(true)}
                className="px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs flex items-center gap-1.5 transition-all shadow-lg"
              >
                <Plus className="w-4 h-4" />
                Add Fact
              </button>
              <button
                onClick={onClose}
                className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Search & Stats Bar */}
          <div className="p-6 border-b border-white/5 bg-slate-950/50 space-y-4">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="relative w-full sm:w-80">
                <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search facts, projects, preferences..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-9 pr-4 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-all"
                />
              </div>

              {/* Stat Counters */}
              <div className="flex items-center space-x-4 text-xs text-slate-400 font-mono">
                <div>
                  Total Facts: <span className="text-indigo-400 font-bold">{memories.length}</span>
                </div>
                <div>•</div>
                <div>
                  Critical Facts:{' '}
                  <span className="text-rose-400 font-bold">
                    {memories.filter((m) => m.importance === 'Critical').length}
                  </span>
                </div>
              </div>
            </div>

            {/* Category Filter Pills */}
            <div className="flex items-center space-x-2 overflow-x-auto pb-1 scrollbar-none">
              {CATEGORIES.map((cat) => {
                const Icon = cat.icon;
                const isActive = activeCategory === cat.id;
                return (
                  <button
                    key={cat.id}
                    onClick={() => setActiveCategory(cat.id)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium flex items-center space-x-1.5 shrink-0 transition-all border ${
                      isActive
                        ? 'bg-indigo-600 text-white border-indigo-400'
                        : 'bg-white/5 text-slate-400 border-white/5 hover:bg-white/10 hover:text-white'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{cat.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Memory Items Grid */}
          <div className="flex-1 overflow-y-auto p-6 space-y-3">
            {filteredMemories.length === 0 ? (
              <div className="py-12 flex flex-col items-center justify-center text-center">
                <Brain className="w-12 h-12 text-slate-600 mb-3 animate-pulse" />
                <p className="text-sm font-medium text-slate-300">No memories found</p>
                <p className="text-xs text-slate-500 max-w-xs mt-1">
                  Kira automatically saves facts during conversations. You can also manually add a fact above.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {filteredMemories.map((mem) => (
                  <div
                    key={mem.id}
                    className="p-4 rounded-2xl bg-white/5 border border-white/10 hover:border-indigo-500/40 transition-all flex flex-col justify-between group relative overflow-hidden"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[10px] uppercase tracking-wider px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 font-mono border border-indigo-500/30">
                          {mem.category}
                        </span>
                        <div className="flex items-center space-x-2">
                          <span
                            className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${
                              mem.importance === 'Critical'
                                ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                                : mem.importance === 'High'
                                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                                : 'bg-slate-500/20 text-slate-300 border border-slate-500/30'
                            }`}
                          >
                            {mem.importance}
                          </span>
                          <button
                            onClick={() => handleDeleteMemory(mem.id)}
                            className="p-1 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 opacity-0 group-hover:opacity-100 transition-all"
                            title="Forget Memory"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>

                      <h4 className="text-sm font-semibold text-white mb-1">{mem.title}</h4>
                      <p className="text-xs text-slate-300 font-sans leading-relaxed mb-3">
                        {mem.value}
                      </p>
                    </div>

                    <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[10px] font-mono text-slate-500">
                      <span>Confidence: {mem.confidence}%</span>
                      <span>Updated: {new Date(mem.lastUpdated).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer Controls */}
          <div className="px-6 py-4 border-t border-white/10 bg-slate-950/80 flex items-center justify-between">
            <button
              onClick={handleClearAll}
              className="text-xs font-mono text-rose-400 hover:text-rose-300 flex items-center gap-1.5 transition-colors"
            >
              <ShieldAlert className="w-4 h-4" />
              Wipe Kira's Brain
            </button>

            <span className="text-[11px] font-mono text-slate-500">
              Kira Brain v1.0 • Hybrid Memory Persistence
            </span>
          </div>

          {/* Add Memory Modal Overlay */}
          <AnimatePresence>
            {isAdding && (
              <div className="absolute inset-0 bg-slate-950/90 backdrop-blur-md p-6 z-20 flex flex-col justify-center">
                <div className="max-w-md mx-auto w-full bg-slate-900 border border-white/10 p-6 rounded-2xl shadow-2xl">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-indigo-400" />
                      Teach Kira a Fact Directly
                    </h3>
                    <button
                      onClick={() => setIsAdding(false)}
                      className="p-1 text-slate-400 hover:text-white"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  <form onSubmit={handleAddMemory} className="space-y-4">
                    <div>
                      <label className="block text-xs text-slate-400 mb-1">Title / Topic</label>
                      <input
                        type="text"
                        placeholder="e.g. Favorite Coding Language"
                        value={newTitle}
                        onChange={(e) => setNewTitle(e.target.value)}
                        className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs text-slate-400 mb-1">Category</label>
                        <select
                          value={newCategory}
                          onChange={(e) => setNewCategory(e.target.value as MemoryCategory)}
                          className="w-full px-3 py-2 bg-slate-800 border border-white/10 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-500"
                        >
                          <option value="identity">Identity</option>
                          <option value="preference">Preference</option>
                          <option value="relationship">Relationship</option>
                          <option value="project">Project</option>
                          <option value="goal">Goal</option>
                          <option value="routine">Routine</option>
                          <option value="device">Device</option>
                          <option value="conversation">Key Decision</option>
                          <option value="emotional">Emotional Trait</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-xs text-slate-400 mb-1">Importance</label>
                        <select
                          value={newImportance}
                          onChange={(e) => setNewImportance(e.target.value as ImportanceLevel)}
                          className="w-full px-3 py-2 bg-slate-800 border border-white/10 rounded-xl text-xs text-white focus:outline-none focus:border-indigo-500"
                        >
                          <option value="Critical">Critical</option>
                          <option value="High">High</option>
                          <option value="Medium">Medium</option>
                          <option value="Low">Low</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs text-slate-400 mb-1">Detail / Value</label>
                      <textarea
                        placeholder="e.g. Tayyab prefers TypeScript and React for building Web AI apps."
                        value={newValue}
                        onChange={(e) => setNewValue(e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                        required
                      />
                    </div>

                    <div className="flex space-x-2 pt-2">
                      <button
                        type="button"
                        onClick={() => setIsAdding(false)}
                        className="flex-1 py-2 rounded-xl bg-white/5 border border-white/10 text-slate-300 text-xs hover:bg-white/10"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="flex-1 py-2 rounded-xl bg-indigo-600 text-white text-xs font-semibold hover:bg-indigo-500"
                      >
                        Save Memory
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
