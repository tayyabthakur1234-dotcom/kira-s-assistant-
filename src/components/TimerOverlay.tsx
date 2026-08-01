import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Timer, X, Pause, Play, BellRing } from 'lucide-react';
import { ActiveTimer, ThemeMode } from '../types';
import { THEMES } from '../lib/theme';

interface TimerOverlayProps {
  timers: ActiveTimer[];
  theme: ThemeMode;
  onUpdateTimers: (timers: ActiveTimer[]) => void;
}

export const TimerOverlay: React.FC<TimerOverlayProps> = ({
  timers,
  theme,
  onUpdateTimers,
}) => {
  const themeConfig = THEMES[theme];

  // Tick timers every second
  useEffect(() => {
    if (timers.length === 0) return;

    const interval = setInterval(() => {
      const updated = timers.map((timer) => {
        if (timer.isPaused || timer.remainingSeconds <= 0) return timer;
        return {
          ...timer,
          remainingSeconds: Math.max(0, timer.remainingSeconds - 1),
        };
      });

      onUpdateTimers(updated);
    }, 1000);

    return () => clearInterval(interval);
  }, [timers, onUpdateTimers]);

  const togglePause = (id: string) => {
    onUpdateTimers(
      timers.map((t) => (t.id === id ? { ...t, isPaused: !t.isPaused } : t))
    );
  };

  const removeTimer = (id: string) => {
    onUpdateTimers(timers.filter((t) => t.id !== id));
  };

  const formatSeconds = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = sec % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  if (timers.length === 0) return null;

  return (
    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-30 w-full max-w-sm px-4 flex flex-col gap-2">
      <AnimatePresence>
        {timers.map((timer) => {
          const isFinished = timer.remainingSeconds === 0;
          const progress = ((timer.totalSeconds - timer.remainingSeconds) / timer.totalSeconds) * 100;

          return (
            <motion.div
              key={timer.id}
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9, y: 10 }}
              className={`relative overflow-hidden rounded-2xl glassmorphism border p-3 shadow-2xl backdrop-blur-xl ${
                isFinished
                  ? 'border-rose-500/50 bg-rose-950/40 animate-pulse'
                  : 'border-white/15 bg-slate-900/80'
              }`}
            >
              {/* Progress bar background */}
              <div
                className="absolute left-0 top-0 bottom-0 bg-white/5 transition-all duration-1000 pointer-events-none"
                style={{ width: `${progress}%` }}
              />

              <div className="relative z-10 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-xl bg-white/10 ${isFinished ? 'text-rose-400 animate-bounce' : themeConfig.accentText}`}>
                    {isFinished ? <BellRing className="w-5 h-5" /> : <Timer className="w-5 h-5" />}
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white tracking-tight">
                      {timer.label}
                    </h4>
                    <p className={`text-lg font-mono font-bold ${isFinished ? 'text-rose-400' : 'text-slate-200'}`}>
                      {isFinished ? 'TIMER COMPLETED!' : formatSeconds(timer.remainingSeconds)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-1">
                  {!isFinished && (
                    <button
                      onClick={() => togglePause(timer.id)}
                      className="p-1.5 rounded-lg bg-white/10 text-slate-300 hover:text-white transition-colors"
                    >
                      {timer.isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                    </button>
                  )}
                  <button
                    onClick={() => removeTimer(timer.id)}
                    className="p-1.5 rounded-lg bg-white/10 text-slate-400 hover:text-rose-400 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
};
