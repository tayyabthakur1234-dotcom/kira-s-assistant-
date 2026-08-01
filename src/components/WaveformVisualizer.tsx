import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { AssistantState, ThemeMode } from '../types';
import { THEMES } from '../lib/theme';
import { AudioPlayer } from '../services/AudioPlayer';

interface WaveformVisualizerProps {
  state: AssistantState;
  theme: ThemeMode;
  micVolume: number;
  audioPlayer: AudioPlayer | null;
}

export const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  state,
  theme,
  micVolume,
  audioPlayer,
}) => {
  const [frequencies, setFrequencies] = useState<number[]>(Array(16).fill(10));
  const themeConfig = THEMES[theme];

  useEffect(() => {
    let animId: number;

    const update = () => {
      if (state === 'speaking' && audioPlayer) {
        const freqData = audioPlayer.getFrequencyData();
        if (freqData && freqData.length > 0) {
          // Sample 16 frequency bins
          const sampled: number[] = [];
          const step = Math.floor(freqData.length / 16) || 1;
          for (let i = 0; i < 16; i++) {
            const val = freqData[i * step] || 0;
            sampled.push(Math.max(12, Math.min(100, (val / 255) * 100)));
          }
          setFrequencies(sampled);
        }
      } else if (state === 'listening') {
        // Generate pseudo audio bars driven by mic volume
        const sampled = Array(16)
          .fill(0)
          .map((_, i) => {
            const wave = Math.sin((i / 16) * Math.PI) * (micVolume * 100);
            return Math.max(8, Math.min(95, wave + Math.random() * 10));
          });
        setFrequencies(sampled);
      } else {
        // Idle gentle breathing bars
        const now = Date.now() / 300;
        const sampled = Array(16)
          .fill(0)
          .map((_, i) => Math.max(6, 12 + Math.sin(now + i * 0.4) * 8));
        setFrequencies(sampled);
      }

      animId = requestAnimationFrame(update);
    };

    update();

    return () => {
      cancelAnimationFrame(animId);
    };
  }, [state, micVolume, audioPlayer]);

  return (
    <div className="w-full max-w-lg mx-auto flex items-center justify-center gap-1.5 h-16 px-4">
      {frequencies.map((height, i) => (
        <motion.div
          key={i}
          animate={{ height: `${height}%` }}
          transition={{ duration: 0.08, ease: 'easeOut' }}
          className="flex-1 rounded-full opacity-80 backdrop-blur-sm"
          style={{
            background:
              i % 2 === 0
                ? `linear-gradient(to top, ${themeConfig.primary}, ${themeConfig.secondary})`
                : `linear-gradient(to top, ${themeConfig.secondary}, ${themeConfig.primary})`,
            boxShadow: height > 30 ? `0 0 12px ${themeConfig.glow}` : 'none',
          }}
        />
      ))}
    </div>
  );
};
