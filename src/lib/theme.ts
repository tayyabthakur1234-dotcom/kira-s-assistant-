import { ThemeMode } from '../types';

export interface ThemeConfig {
  name: string;
  primary: string; // Tailwind color class or hex
  secondary: string;
  glow: string;
  ringColor: string;
  bgGradient: string;
  accentText: string;
  borderGlow: string;
}

export const THEMES: Record<ThemeMode, ThemeConfig> = {
  neon: {
    name: 'Frosted Indigo',
    primary: '#6366f1', // Indigo 500
    secondary: '#d946ef', // Fuchsia 500
    glow: 'rgba(99, 102, 241, 0.45)',
    ringColor: 'from-indigo-500 via-fuchsia-500 to-purple-500',
    bgGradient: 'from-[#050508] via-indigo-950/20 to-[#050508]',
    accentText: 'text-indigo-400',
    borderGlow: 'border-indigo-500/30 shadow-[0_0_35px_rgba(99,102,241,0.3)]',
  },
  cosmic: {
    name: 'Cosmic Fuchsia',
    primary: '#d946ef', // Fuchsia 500
    secondary: '#818cf8', // Indigo 400
    glow: 'rgba(217, 70, 239, 0.45)',
    ringColor: 'from-fuchsia-500 via-pink-500 to-indigo-500',
    bgGradient: 'from-[#050508] via-fuchsia-950/20 to-[#050508]',
    accentText: 'text-fuchsia-400',
    borderGlow: 'border-fuchsia-500/30 shadow-[0_0_35px_rgba(217,70,239,0.3)]',
  },
  cyber: {
    name: 'Emerald Glass',
    primary: '#10b981', // Emerald 500
    secondary: '#6366f1', // Indigo 500
    glow: 'rgba(16, 185, 129, 0.45)',
    ringColor: 'from-emerald-400 via-teal-500 to-indigo-500',
    bgGradient: 'from-[#050508] via-emerald-950/20 to-[#050508]',
    accentText: 'text-emerald-400',
    borderGlow: 'border-emerald-500/30 shadow-[0_0_35px_rgba(16,185,129,0.3)]',
  },
  aurora: {
    name: 'Aurora Cyan',
    primary: '#06b6d4', // Cyan 500
    secondary: '#3b82f6', // Blue 500
    glow: 'rgba(6, 182, 212, 0.45)',
    ringColor: 'from-cyan-400 via-teal-400 to-blue-500',
    bgGradient: 'from-[#050508] via-cyan-950/20 to-[#050508]',
    accentText: 'text-cyan-400',
    borderGlow: 'border-cyan-500/30 shadow-[0_0_35px_rgba(6,182,212,0.3)]',
  },
  sunset: {
    name: 'Solar Sunset',
    primary: '#f97316', // Orange 500
    secondary: '#e11d48', // Rose 600
    glow: 'rgba(249, 115, 22, 0.45)',
    ringColor: 'from-amber-500 via-orange-500 to-rose-500',
    bgGradient: 'from-[#050508] via-orange-950/20 to-[#050508]',
    accentText: 'text-orange-400',
    borderGlow: 'border-orange-500/30 shadow-[0_0_35px_rgba(249,115,22,0.3)]',
  },
};
