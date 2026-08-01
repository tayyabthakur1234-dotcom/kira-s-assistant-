import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { X, Palette, Mic, Wrench, ShieldCheck, Sparkles, User, Volume2, Gauge, Flame } from 'lucide-react';
import {
  PrebuiltVoice,
  SpeakingSpeed,
  SpeakingStyle,
  ThemeMode,
  VoiceGender,
  VoiceSettings,
  VoiceWarmth,
} from '../types';
import { THEMES } from '../lib/theme';

interface SettingsModalProps {
  isOpen: boolean;
  theme: ThemeMode;
  voiceSettings: VoiceSettings;
  hasApiKey: boolean;
  onClose: () => void;
  onChangeTheme: (theme: ThemeMode) => void;
  onChangeVoiceSettings: (settings: Partial<VoiceSettings>) => void;
}

const FEMALE_VOICES: { id: PrebuiltVoice; name: string; desc: string }[] = [
  { id: 'Aoede', name: 'Aoede', desc: 'Soft, gentle, warm & expressive' },
  { id: 'Kore', name: 'Kore', desc: 'Bright, cheerful & friendly' },
  { id: 'Zephyr', name: 'Zephyr', desc: 'Calm, smooth & elegant' },
];

const MALE_VOICES: { id: PrebuiltVoice; name: string; desc: string }[] = [
  { id: 'Fenrir', name: 'Fenrir', desc: 'Deep, crisp & confident' },
  { id: 'Puck', name: 'Puck', desc: 'Playful, upbeat & energetic' },
];

const STYLES: SpeakingStyle[] = ['Calm', 'Friendly', 'Professional', 'Energetic', 'Cheerful'];
const SPEEDS: SpeakingSpeed[] = ['Slow', 'Normal', 'Fast'];
const WARMTHS: VoiceWarmth[] = ['Soft', 'Neutral', 'Deep'];

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  theme,
  voiceSettings,
  hasApiKey,
  onClose,
  onChangeTheme,
  onChangeVoiceSettings,
}) => {
  if (!isOpen) return null;

  const currentVoices = voiceSettings.gender === 'Female' ? FEMALE_VOICES : MALE_VOICES;

  const handleGenderChange = (gender: VoiceGender) => {
    let defaultVoice: PrebuiltVoice = gender === 'Female' ? 'Aoede' : 'Fenrir';
    onChangeVoiceSettings({
      gender,
      voice: defaultVoice,
    });
  };

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
        <motion.div
          initial={{ opacity: 0, scale: 0.9, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.9, y: 20 }}
          className="relative w-full max-w-lg rounded-3xl glassmorphism border border-white/15 bg-slate-900/95 p-6 shadow-2xl backdrop-blur-2xl text-white max-h-[85vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="flex items-center justify-between pb-4 border-b border-white/10">
            <div className="flex items-center gap-2.5">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              <h3 className="text-lg font-bold tracking-tight">Kira Settings</h3>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-xl bg-white/10 text-slate-400 hover:text-white transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="py-5 space-y-6">
            {/* Voice System Settings */}
            <div>
              <label className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-indigo-300 mb-3">
                <Mic className="w-4 h-4 text-indigo-400" />
                Voice Profile & Gender
              </label>

              {/* Gender Selector Toggle */}
              <div className="grid grid-cols-2 gap-2 mb-3 bg-white/5 p-1 rounded-2xl border border-white/10">
                <button
                  onClick={() => handleGenderChange('Female')}
                  className={`py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                    voiceSettings.gender === 'Female'
                      ? 'bg-fuchsia-600 text-white shadow-lg'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <User className="w-3.5 h-3.5" />
                  Female Voice
                </button>
                <button
                  onClick={() => handleGenderChange('Male')}
                  className={`py-2 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                    voiceSettings.gender === 'Male'
                      ? 'bg-indigo-600 text-white shadow-lg'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <User className="w-3.5 h-3.5" />
                  Male Voice
                </button>
              </div>

              {/* Voice Models List */}
              <div className="space-y-2 mb-4">
                {currentVoices.map((v) => {
                  const isActive = voiceSettings.voice === v.id;

                  return (
                    <button
                      key={v.id}
                      onClick={() => onChangeVoiceSettings({ voice: v.id })}
                      className={`w-full p-3 rounded-2xl border text-left flex items-center justify-between transition-all ${
                        isActive
                          ? 'border-indigo-400 bg-indigo-500/20 text-white'
                          : 'border-white/10 bg-white/5 text-slate-300 hover:bg-white/10'
                      }`}
                    >
                      <div>
                        <span className="text-sm font-semibold block">{v.name}</span>
                        <span className="text-xs text-slate-400">{v.desc}</span>
                      </div>
                      {isActive && <Sparkles className="w-4 h-4 text-indigo-400" />}
                    </button>
                  );
                })}
              </div>

              {/* Detailed Voice Customization Grid */}
              <div className="space-y-3 p-4 rounded-2xl bg-white/5 border border-white/10">
                {/* Speaking Style */}
                <div>
                  <label className="flex items-center gap-1.5 text-[11px] font-mono text-slate-400 mb-2">
                    <Volume2 className="w-3.5 h-3.5 text-indigo-400" />
                    Speaking Style
                  </label>
                  <div className="flex flex-wrap gap-1.5">
                    {STYLES.map((st) => (
                      <button
                        key={st}
                        onClick={() => onChangeVoiceSettings({ style: st })}
                        className={`px-2.5 py-1 rounded-xl text-xs font-medium border transition-all ${
                          voiceSettings.style === st
                            ? 'bg-indigo-600 text-white border-indigo-400'
                            : 'bg-white/5 text-slate-300 border-white/10 hover:bg-white/10'
                        }`}
                      >
                        {st}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Speaking Speed */}
                <div>
                  <label className="flex items-center gap-1.5 text-[11px] font-mono text-slate-400 mb-2">
                    <Gauge className="w-3.5 h-3.5 text-indigo-400" />
                    Speaking Speed
                  </label>
                  <div className="grid grid-cols-3 gap-1.5">
                    {SPEEDS.map((sp) => (
                      <button
                        key={sp}
                        onClick={() => onChangeVoiceSettings({ speed: sp })}
                        className={`py-1.5 rounded-xl text-xs font-medium border text-center transition-all ${
                          voiceSettings.speed === sp
                            ? 'bg-indigo-600 text-white border-indigo-400'
                            : 'bg-white/5 text-slate-300 border-white/10 hover:bg-white/10'
                        }`}
                      >
                        {sp}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Voice Warmth */}
                <div>
                  <label className="flex items-center gap-1.5 text-[11px] font-mono text-slate-400 mb-2">
                    <Flame className="w-3.5 h-3.5 text-indigo-400" />
                    Voice Warmth / Depth
                  </label>
                  <div className="grid grid-cols-3 gap-1.5">
                    {WARMTHS.map((wm) => (
                      <button
                        key={wm}
                        onClick={() => onChangeVoiceSettings({ warmth: wm })}
                        className={`py-1.5 rounded-xl text-xs font-medium border text-center transition-all ${
                          voiceSettings.warmth === wm
                            ? 'bg-indigo-600 text-white border-indigo-400'
                            : 'bg-white/5 text-slate-300 border-white/10 hover:bg-white/10'
                        }`}
                      >
                        {wm}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Theme Selector */}
            <div>
              <label className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-slate-400 mb-3">
                <Palette className="w-4 h-4 text-cyan-400" />
                HUD Color Palette
              </label>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {(Object.keys(THEMES) as ThemeMode[]).map((tKey) => {
                  const cfg = THEMES[tKey];
                  const isActive = theme === tKey;

                  return (
                    <button
                      key={tKey}
                      onClick={() => onChangeTheme(tKey)}
                      className={`p-3 rounded-2xl border text-left transition-all ${
                        isActive
                          ? 'border-cyan-400 bg-cyan-500/15 text-white shadow-lg'
                          : 'border-white/10 bg-white/5 text-slate-300 hover:bg-white/10'
                      }`}
                    >
                      <div className="flex items-center gap-1.5 mb-1">
                        <span
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: cfg.primary }}
                        />
                        <span
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: cfg.secondary }}
                        />
                      </div>
                      <span className="text-xs font-semibold block">{cfg.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Tools Capabilities Info */}
            <div className="p-4 rounded-2xl bg-white/5 border border-white/10">
              <label className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-slate-400 mb-2">
                <Wrench className="w-4 h-4 text-indigo-400" />
                Active Function Tools
              </label>
              <div className="flex flex-wrap gap-1.5">
                {[
                  'openWebsite',
                  'searchWeb',
                  'setTimer',
                  'calculateMath',
                  'getCurrentTime',
                  'changeThemeMode',
                  'changeVoiceSettings',
                  'saveMemory',
                  'searchMemories',
                ].map((tool) => (
                  <span
                    key={tool}
                    className="px-2.5 py-1 rounded-lg bg-indigo-950/60 border border-indigo-500/30 text-[11px] font-mono text-indigo-300"
                  >
                    {tool}()
                  </span>
                ))}
              </div>
            </div>

            {/* API Key Status */}
            <div className="flex items-center justify-between p-3 rounded-2xl bg-white/5 border border-white/10 text-xs">
              <span className="flex items-center gap-2 text-slate-300">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                Gemini Live API Key Status
              </span>
              <span className={`font-mono font-bold ${hasApiKey ? 'text-emerald-400' : 'text-amber-400'}`}>
                {hasApiKey ? 'Configured' : 'Missing in Secrets'}
              </span>
            </div>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
