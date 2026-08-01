import React, { useEffect, useRef } from 'react';
import { motion } from 'motion/react';
import { Mic, MicOff, Power, Loader2, Sparkles, Volume2 } from 'lucide-react';
import { AssistantState, ThemeMode } from '../types';
import { THEMES } from '../lib/theme';

interface FuturisticOrbProps {
  state: AssistantState;
  theme: ThemeMode;
  micVolume: number;
  outputVolume: number;
  isMuted: boolean;
  onToggleConnect: () => void;
  onToggleMute: () => void;
}

export const FuturisticOrb: React.FC<FuturisticOrbProps> = ({
  state,
  theme,
  micVolume,
  outputVolume,
  isMuted,
  onToggleConnect,
  onToggleMute,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const themeConfig = THEMES[theme];

  // Render reactive canvas particle wave orb
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let phase = 0;

    const resize = () => {
      const rect = canvas.parentElement?.getBoundingClientRect();
      if (rect) {
        canvas.width = rect.width * window.devicePixelRatio;
        canvas.height = rect.height * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
      }
    };

    resize();
    window.addEventListener('resize', resize);

    const render = () => {
      const width = canvas.width / window.devicePixelRatio;
      const height = canvas.height / window.devicePixelRatio;
      const centerX = width / 2;
      const centerY = height / 2;

      ctx.clearRect(0, 0, width, height);

      const activeVolume = state === 'speaking' ? outputVolume : state === 'listening' ? micVolume : 0.05;
      const baseRadius = Math.min(width, height) * 0.22 + activeVolume * 35;

      phase += 0.03 + activeVolume * 0.08;

      // Draw multi-layered glowing organic wave rings
      const ringCount = 3;
      for (let ring = 0; ring < ringCount; ring++) {
        ctx.beginPath();
        const numPoints = 120;
        const currentRadius = baseRadius + ring * 12 * (1 + activeVolume);

        for (let i = 0; i <= numPoints; i++) {
          const angle = (i / numPoints) * Math.PI * 2;
          // Organic sine deformation
          const distortion =
            Math.sin(angle * 6 + phase + ring * 1.5) * (8 + activeVolume * 25) +
            Math.cos(angle * 4 - phase * 0.8) * (5 + activeVolume * 15);

          const r = currentRadius + distortion;
          const x = centerX + Math.cos(angle) * r;
          const y = centerY + Math.sin(angle) * r;

          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }

        ctx.closePath();

        const opacity = Math.max(0.15, 0.6 - ring * 0.15 + activeVolume * 0.4);
        ctx.strokeStyle = ring === 0 ? themeConfig.primary : themeConfig.secondary;
        ctx.globalAlpha = opacity;
        ctx.lineWidth = 2 + ring + activeVolume * 4;
        ctx.shadowColor = themeConfig.primary;
        ctx.shadowBlur = 15 + activeVolume * 25;
        ctx.stroke();
      }

      ctx.globalAlpha = 1;
      animId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animId);
    };
  }, [state, theme, micVolume, outputVolume, themeConfig]);

  const getStateText = () => {
    switch (state) {
      case 'disconnected':
        return 'Tap to Connect Kira';
      case 'connecting':
        return 'Connecting to Kira...';
      case 'listening':
        return isMuted ? 'Muted — Tap Mic to Unmute' : 'Listening... Speak freely';
      case 'speaking':
        return 'Kira is speaking...';
      case 'processing':
        return 'Executing browser tool...';
    }
  };

  return (
    <div className="relative flex flex-col items-center justify-center w-full max-w-md mx-auto aspect-square my-auto">
      {/* Background Canvas Visualizer */}
      <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
        <canvas ref={canvasRef} className="w-full h-full" />
      </div>

      {/* Ambient Pulsing Glow Backdrop */}
      <motion.div
        animate={{
          scale: state === 'speaking' ? [1, 1.25, 1] : state === 'listening' ? [1, 1.15, 1] : [1, 1.05, 1],
          opacity: state === 'disconnected' ? 0.3 : 0.85,
        }}
        transition={{
          duration: state === 'speaking' ? 1.2 : state === 'listening' ? 2 : 4,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className={`absolute rounded-full blur-3xl pointer-events-none w-64 h-64`}
        style={{
          background: `radial-gradient(circle, ${themeConfig.primary} 0%, ${themeConfig.secondary} 70%, transparent 100%)`,
        }}
      />

      {/* Outer Glow Rings from Frosted Glass Theme */}
      <div className="absolute w-72 h-72 sm:w-80 sm:h-80 rounded-full border border-indigo-500/10 animate-pulse pointer-events-none" />
      <div className="absolute w-60 h-60 sm:w-68 sm:h-68 rounded-full border border-fuchsia-500/20 pointer-events-none" />
      <div className="absolute w-48 h-48 sm:w-56 sm:h-56 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm pointer-events-none" />

      {/* Central Interactive Core Button */}
      <div className="relative z-10 flex flex-col items-center justify-center">
        <motion.button
          onClick={onToggleConnect}
          whileHover={{ scale: 1.06 }}
          whileTap={{ scale: 0.95 }}
          className={`relative flex items-center justify-center w-40 h-40 rounded-full transition-all duration-300 shadow-[0_0_80px_rgba(99,102,241,0.4)] backdrop-blur-2xl border ${
            state === 'disconnected'
              ? 'border-white/20 bg-gradient-to-br from-indigo-950/80 via-slate-900 to-fuchsia-950/80 hover:border-indigo-400/50'
              : 'border-fuchsia-400/40 bg-gradient-to-br from-indigo-600 via-fuchsia-500 to-indigo-800'
          }`}
          aria-label={state === 'disconnected' ? 'Start Kira Session' : 'Disconnect Kira Session'}
        >
          {/* Radial depth overlay */}
          <div className="absolute inset-0 rounded-full bg-[radial-gradient(circle_at_center,_transparent_0%,_#000_100%)] opacity-30 pointer-events-none" />
          <div className="absolute inset-2 rounded-full border border-white/15 pointer-events-none" />

          {/* State Icon */}
          {state === 'disconnected' && (
            <Power className="w-12 h-12 text-slate-300 group-hover:text-indigo-400 transition-colors relative z-10" />
          )}

          {state === 'connecting' && (
            <Loader2 className="w-12 h-12 animate-spin text-white relative z-10" />
          )}

          {state === 'listening' && (
            <div className="flex flex-col items-center justify-center gap-1 relative z-10">
              {isMuted ? (
                <MicOff className="w-11 h-11 text-rose-300" />
              ) : (
                <Mic className="w-11 h-11 text-white animate-pulse" />
              )}
            </div>
          )}

          {state === 'speaking' && (
            <Volume2 className="w-12 h-12 text-white animate-bounce relative z-10" />
          )}

          {state === 'processing' && (
            <Sparkles className="w-12 h-12 text-amber-300 animate-spin relative z-10" />
          )}
        </motion.button>

        {/* Mute Toggle floating badge if active */}
        {state !== 'disconnected' && state !== 'connecting' && (
          <motion.button
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            onClick={onToggleMute}
            className={`mt-6 px-4 py-2 rounded-full glassmorphism border flex items-center gap-2 text-xs font-medium tracking-wide transition-all ${
              isMuted
                ? 'border-rose-500/40 bg-rose-500/20 text-rose-300 shadow-rose-900/30'
                : 'border-white/15 bg-white/10 text-slate-200 hover:bg-white/15'
            }`}
          >
            {isMuted ? <MicOff className="w-3.5 h-3.5 text-rose-400" /> : <Mic className="w-3.5 h-3.5 text-emerald-400" />}
            {isMuted ? 'Unmute Mic' : 'Mute Mic'}
          </motion.button>
        )}

        {/* Live Status Text Indicator */}
        <motion.div
          key={state}
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 text-center"
        >
          <span className={`text-sm font-medium tracking-wider uppercase text-slate-300 font-mono flex items-center justify-center gap-2`}>
            {state !== 'disconnected' && (
              <span className="relative flex h-2 w-2">
                <span
                  className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                    state === 'speaking' ? 'bg-cyan-400' : 'bg-emerald-400'
                  }`}
                />
                <span
                  className={`relative inline-flex rounded-full h-2 w-2 ${
                    state === 'speaking' ? 'bg-cyan-500' : 'bg-emerald-500'
                  }`}
                />
              </span>
            )}
            {getStateText()}
          </span>
        </motion.div>
      </div>
    </div>
  );
};
