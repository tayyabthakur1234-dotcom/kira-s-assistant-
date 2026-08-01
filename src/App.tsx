import { useEffect, useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { AlertCircle, X, Sparkles, Volume2, ShieldAlert, Monitor, Eye } from 'lucide-react';
import {
  ActiveTimer,
  AssistantState,
  DesktopActionRequest,
  OpenedWebsite,
  ScreenVisionState,
  ThemeMode,
  VoiceSettings,
} from './types';
import { THEMES } from './lib/theme';
import { ToolManager } from './services/ToolManager';
import { LiveSession } from './services/LiveSession';
import { ScreenStreamer } from './services/ScreenStreamer';
import { HeaderHUD } from './components/HeaderHUD';
import { FuturisticOrb } from './components/FuturisticOrb';
import { WaveformVisualizer } from './components/WaveformVisualizer';
import { TimerOverlay } from './components/TimerOverlay';
import { WebsiteOverlay } from './components/WebsiteOverlay';
import { SettingsModal } from './components/SettingsModal';
import { BrainModal } from './components/BrainModal';
import { OSDashboardModal } from './components/OSDashboardModal';
import { ScreenVisionOverlay } from './components/ScreenVisionOverlay';
import { BatteryStatus, fetchBatteryStatus } from './utils/battery';

const DEFAULT_VOICE_SETTINGS: VoiceSettings = {
  gender: 'Female',
  voice: 'Aoede',
  style: 'Friendly',
  speed: 'Normal',
  warmth: 'Soft',
};

export default function App() {
  const [assistantState, setAssistantState] = useState<AssistantState>('disconnected');
  const [theme, setTheme] = useState<ThemeMode>('neon');
  const [voiceSettings, setVoiceSettings] = useState<VoiceSettings>(() => {
    try {
      const saved = localStorage.getItem('kira_voice_settings');
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.error('Failed to parse voice settings from localStorage:', e);
    }
    return DEFAULT_VOICE_SETTINGS;
  });

  const [micVolume, setMicVolume] = useState<number>(0);
  const [outputVolume, setOutputVolume] = useState<number>(0);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [hasApiKey, setHasApiKey] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Overlays & Screen Vision state
  const [timers, setTimers] = useState<ActiveTimer[]>([]);
  const [openedSites, setOpenedSites] = useState<OpenedWebsite[]>([]);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [isBrainOpen, setIsBrainOpen] = useState<boolean>(false);
  const [isOSDashboardOpen, setIsOSDashboardOpen] = useState<boolean>(false);

  // Screen Vision State
  const [visionState, setVisionState] = useState<ScreenVisionState>({
    isSharing: false,
    isPaused: false,
    shareType: 'unknown',
    fps: 0,
    lastCapturedTime: null,
    lastFramePreview: null,
  });
  const [highlightRegion, setHighlightRegion] = useState<{
    label: string;
    description: string;
    xPercent: number;
    yPercent: number;
  } | null>(null);
  const [pendingDesktopAction, setPendingDesktopAction] = useState<DesktopActionRequest | null>(null);
  const [batteryStatus, setBatteryStatus] = useState<BatteryStatus>({
    supported: false,
    level: null,
    charging: null,
    statusText: 'Checking...',
  });

  const liveSessionRef = useRef<LiveSession | null>(null);
  const screenStreamerRef = useRef<ScreenStreamer | null>(null);
  const prevVoiceSettingsRef = useRef<VoiceSettings>(voiceSettings);

  // Fetch and monitor user system battery status
  useEffect(() => {
    let batteryObj: any = null;
    let isMounted = true;

    const loadBattery = async () => {
      const initial = await fetchBatteryStatus();
      if (!isMounted) return;
      setBatteryStatus(initial);

      if ('getBattery' in navigator && typeof (navigator as any).getBattery === 'function') {
        try {
          batteryObj = await (navigator as any).getBattery();
          const handleUpdate = () => {
            if (!isMounted || !batteryObj) return;
            const level = Math.round((batteryObj.level ?? 1) * 100);
            const charging = Boolean(batteryObj.charging);
            setBatteryStatus({
              supported: true,
              level,
              charging,
              statusText: `${level}%${charging ? ' (Charging)' : ''}`,
            });
          };

          batteryObj.addEventListener('levelchange', handleUpdate);
          batteryObj.addEventListener('chargingchange', handleUpdate);
        } catch (err) {
          console.warn('[App] Battery listener attachment failed:', err);
        }
      }
    };

    loadBattery();

    return () => {
      isMounted = false;
      if (batteryObj) {
        batteryObj.removeEventListener('levelchange', () => {});
        batteryObj.removeEventListener('chargingchange', () => {});
      }
    };
  }, []);

  // Auto dismiss highlight region after 8 seconds
  useEffect(() => {
    if (highlightRegion) {
      const timer = setTimeout(() => setHighlightRegion(null), 8000);
      return () => clearTimeout(timer);
    }
  }, [highlightRegion]);

  // Persist voice settings to localStorage whenever changed
  useEffect(() => {
    try {
      localStorage.setItem('kira_voice_settings', JSON.stringify(voiceSettings));
    } catch (e) {
      console.error('Failed to save voice settings:', e);
    }
  }, [voiceSettings]);

  // ScreenStreamer Service Initialization
  useEffect(() => {
    const streamer = new ScreenStreamer({
      onFrameCaptured: (base64Data) => {
        if (liveSessionRef.current) {
          liveSessionRef.current.sendScreenFrame(base64Data);
        }
      },
      onStateChange: (vState) => setVisionState(vState),
      onError: (err) => setErrorMessage(err),
    });

    screenStreamerRef.current = streamer;

    return () => {
      streamer.stopShare();
    };
  }, []);

  // Check server health and API Key status
  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => {
        if (data && typeof data.hasApiKey === 'boolean') {
          setHasApiKey(data.hasApiKey);
        }
      })
      .catch((err) => {
        console.warn('Health check failed:', err);
      });
  }, []);

  const handleUpdateVoiceSettings = useCallback((newSettings: Partial<VoiceSettings>) => {
    setVoiceSettings((prev) => {
      const updated = { ...prev, ...newSettings };
      // Handle gender fallbacks
      if (newSettings.gender === 'Male' && !['Fenrir', 'Puck'].includes(updated.voice)) {
        updated.voice = 'Fenrir';
      } else if (newSettings.gender === 'Female' && !['Aoede', 'Kore', 'Zephyr'].includes(updated.voice)) {
        updated.voice = 'Aoede';
      }
      return updated;
    });
  }, []);

  // Tool Manager callbacks
  const handleOpenWebsite = useCallback((site: OpenedWebsite) => {
    setOpenedSites((prev) => [site, ...prev]);
  }, []);

  const handleSetTimer = useCallback((newTimer: ActiveTimer) => {
    setTimers((prev) => [...prev, newTimer]);
  }, []);

  const handleChangeTheme = useCallback((newTheme: ThemeMode) => {
    setTheme(newTheme);
  }, []);

  const handleDesktopActionRequested = useCallback((action: DesktopActionRequest) => {
    setPendingDesktopAction(action);
  }, []);

  const handleHighlightRegion = useCallback(
    (label: string, description: string, xPercent?: number, yPercent?: number) => {
      setHighlightRegion({
        label,
        description,
        xPercent: xPercent !== undefined ? xPercent : 50,
        yPercent: yPercent !== undefined ? yPercent : 50,
      });
    },
    []
  );

  const handleScreenAnalyzeRequested = useCallback(() => {
    if (screenStreamerRef.current) {
      screenStreamerRef.current.captureFrameNow();
    }
  }, []);

  // Initialize LiveSession instance
  useEffect(() => {
    const toolManager = new ToolManager({
      onOpenWebsite: handleOpenWebsite,
      onSetTimer: handleSetTimer,
      onChangeTheme: handleChangeTheme,
      onChangeVoiceSettings: handleUpdateVoiceSettings,
      onDesktopActionRequested: handleDesktopActionRequested,
      onHighlightRegion: handleHighlightRegion,
      onScreenAnalyzeRequested: handleScreenAnalyzeRequested,
    });

    const liveSession = new LiveSession(toolManager, {
      onStateChange: (state) => setAssistantState(state),
      onError: (err) => setErrorMessage(err),
      onMicVolumeChange: (vol) => setMicVolume(vol),
      onAudioOutputVolumeChange: (vol) => setOutputVolume(vol),
    });

    liveSessionRef.current = liveSession;

    return () => {
      liveSession.disconnect();
    };
  }, [handleOpenWebsite, handleSetTimer, handleChangeTheme, handleUpdateVoiceSettings]);

  // Live session reconnection when voice settings change during active conversation
  useEffect(() => {
    if (
      liveSessionRef.current &&
      assistantState !== 'disconnected' &&
      JSON.stringify(prevVoiceSettingsRef.current) !== JSON.stringify(voiceSettings)
    ) {
      console.log('[App] Voice settings changed during active call. Reconnecting with new voice...');
      liveSessionRef.current.disconnect();
      setTimeout(() => {
        liveSessionRef.current?.connect(voiceSettings);
      }, 300);
    }
    prevVoiceSettingsRef.current = voiceSettings;
  }, [voiceSettings, assistantState]);

  const toggleConnect = () => {
    setErrorMessage(null);
    if (!liveSessionRef.current) return;

    if (assistantState === 'disconnected') {
      liveSessionRef.current.connect(voiceSettings);
    } else {
      liveSessionRef.current.disconnect();
    }
  };

  const toggleMute = () => {
    if (liveSessionRef.current) {
      const muted = liveSessionRef.current.toggleMute();
      setIsMuted(muted);
    }
  };

  const handleToggleScreenShare = async () => {
    if (!screenStreamerRef.current) return;
    if (visionState.isSharing) {
      screenStreamerRef.current.stopShare();
    } else {
      setErrorMessage(null);
      const success = await screenStreamerRef.current.startShare();
      if (success && assistantState === 'disconnected') {
        liveSessionRef.current?.connect(voiceSettings);
      }
    }
  };

  const handleApproveDesktopAction = (actionId: string) => {
    console.log('[App] Desktop action approved:', actionId);
    setPendingDesktopAction(null);
  };

  const handleRejectDesktopAction = (actionId: string) => {
    console.log('[App] Desktop action rejected:', actionId);
    setPendingDesktopAction(null);
  };

  const closeSiteOverlay = (id: string) => {
    setOpenedSites((prev) => prev.filter((s) => s.id !== id));
  };

  const themeConfig = THEMES[theme];

  return (
    <div
      className={`relative min-h-screen w-full flex flex-col justify-between overflow-hidden bg-[#050508] text-slate-100 transition-colors duration-700 bg-gradient-to-b ${themeConfig.bgGradient}`}
    >
      {/* Background Ambient Glows from Frosted Glass Theme */}
      <div className="absolute inset-0 pointer-events-none z-0">
        <div className="absolute top-[-10%] left-[-10%] w-[600px] h-[600px] bg-indigo-900/30 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[700px] h-[700px] bg-fuchsia-900/20 rounded-full blur-[150px]" />
        <div className="absolute top-[20%] right-[10%] w-[400px] h-[400px] bg-blue-900/20 rounded-full blur-[100px]" />
        <div className="absolute inset-0 bg-grid-dots opacity-5" />
      </div>

      {/* Header HUD */}
      <HeaderHUD
        state={assistantState}
        theme={theme}
        voiceSettings={voiceSettings}
        isSharingScreen={visionState.isSharing}
        onOpenSettings={() => setIsSettingsOpen(true)}
        onOpenBrain={() => setIsBrainOpen(true)}
        onOpenOSDashboard={() => setIsOSDashboardOpen(true)}
        onToggleScreenShare={handleToggleScreenShare}
      />

      {/* Main Container */}
      <main className="relative z-10 flex-1 flex flex-col items-center justify-center p-4 w-full max-w-5xl mx-auto my-auto">
        {/* Error Notification Banner */}
        <AnimatePresence>
          {errorMessage && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="mb-4 w-full max-w-md p-3.5 rounded-2xl bg-rose-950/40 border border-rose-500/40 text-rose-200 text-xs flex items-center justify-between gap-3 shadow-xl backdrop-blur-xl"
            >
              <div className="flex items-center gap-2.5">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
                <span>{errorMessage}</span>
              </div>
              <button
                onClick={() => setErrorMessage(null)}
                className="p-1 text-rose-300 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          )}

          {!hasApiKey && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 w-full max-w-md p-3.5 rounded-2xl bg-amber-950/40 border border-amber-500/40 text-amber-200 text-xs flex items-center gap-2.5 shadow-xl backdrop-blur-xl"
            >
              <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
              <span>
                GEMINI_API_KEY is required for voice API calls. Set it in AI Studio Settings &gt; Secrets.
              </span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Central Futuristic Orb & Microphone Button */}
        <FuturisticOrb
          state={assistantState}
          theme={theme}
          micVolume={micVolume}
          outputVolume={outputVolume}
          isMuted={isMuted}
          onToggleConnect={toggleConnect}
          onToggleMute={toggleMute}
        />
      </main>

      {/* Floating Active Overlays */}
      <TimerOverlay
        timers={timers}
        theme={theme}
        onUpdateTimers={(updated) => setTimers(updated)}
      />

      <WebsiteOverlay
        sites={openedSites}
        theme={theme}
        onCloseSite={closeSiteOverlay}
      />

      {/* Screen Vision Floating HUD & Target Overlay */}
      <ScreenVisionOverlay
        visionState={visionState}
        onStopShare={() => screenStreamerRef.current?.stopShare()}
        onPauseVision={() => screenStreamerRef.current?.pauseVision()}
        onResumeVision={() => screenStreamerRef.current?.resumeVision()}
        onAnalyzeNow={() => screenStreamerRef.current?.captureFrameNow()}
        highlightRegion={highlightRegion}
        pendingDesktopAction={pendingDesktopAction}
        onApproveAction={handleApproveDesktopAction}
        onRejectAction={handleRejectDesktopAction}
        onDismissHighlight={() => setHighlightRegion(null)}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        theme={theme}
        voiceSettings={voiceSettings}
        hasApiKey={hasApiKey}
        onClose={() => setIsSettingsOpen(false)}
        onChangeTheme={(t) => setTheme(t)}
        onChangeVoiceSettings={handleUpdateVoiceSettings}
      />

      {/* Kira Memory Brain Modal */}
      <BrainModal
        isOpen={isBrainOpen}
        onClose={() => setIsBrainOpen(false)}
      />

      {/* Kira Phase 7 JARVIS OS Dashboard Modal */}
      <OSDashboardModal
        isOpen={isOSDashboardOpen}
        onClose={() => setIsOSDashboardOpen(false)}
        assistantState={assistantState}
        outputVolume={outputVolume}
        micVolume={micVolume}
      />

      {/* Frosted Glass Bottom Interface Panels */}
      <footer className="relative z-10 w-full max-w-5xl mx-auto px-6 pb-6 pt-2">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Active Tools Panel */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-xl">
            <div className="text-[10px] text-white/40 uppercase tracking-widest font-mono mb-2">
              Active Capabilities
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-white/80">Kira's Brain Memory</span>
                <span className="text-indigo-400 font-semibold">Persistent</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-white/80">Desktop Control Engine</span>
                <span className="text-cyan-400 font-semibold">Python 3.12 / REST</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-white/80">Desktop Screen Vision</span>
                <span className={visionState.isSharing ? 'text-red-400 font-semibold animate-pulse' : 'text-slate-400'}>
                  {visionState.isSharing ? (visionState.isPaused ? 'Paused' : 'Active') : 'Standby'}
                </span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-white/80">Gemini Live Voice</span>
                <span className="text-fuchsia-400 font-semibold">24kHz PCM</span>
              </div>
              <div className="flex items-center justify-between text-xs font-mono">
                <span className="text-white/80">System Battery</span>
                <span
                  className={`font-semibold ${
                    batteryStatus.level !== null
                      ? batteryStatus.level <= 20 && !batteryStatus.charging
                        ? 'text-rose-400 animate-pulse'
                        : batteryStatus.charging
                        ? 'text-emerald-400'
                        : 'text-emerald-300'
                      : 'text-slate-400'
                  }`}
                  id="battery-level-status"
                >
                  {batteryStatus.statusText}
                </span>
              </div>
            </div>
          </div>

          {/* Waveform Output Detail Panel */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-4 flex flex-col items-center justify-center shadow-xl min-h-[90px]">
            <WaveformVisualizer
              state={assistantState}
              theme={theme}
              micVolume={micVolume}
              audioPlayer={liveSessionRef.current?.getAudioPlayer() || null}
            />
            <div className="text-[9px] text-white/30 uppercase tracking-[0.2em] font-mono mt-2">
              Real-time Audio Amplitude
            </div>
          </div>

          {/* Control Panel */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-4 flex flex-col justify-between shadow-xl">
            <div className="text-[10px] text-white/40 uppercase tracking-widest font-mono mb-2">
              Quick Control
            </div>
            <div className="flex space-x-2">
              <button
                onClick={toggleConnect}
                className={`flex-1 ${
                  assistantState === 'disconnected'
                    ? 'bg-indigo-600/40 hover:bg-indigo-600/60 border-indigo-400/30'
                    : 'bg-rose-600/40 hover:bg-rose-600/60 border-rose-400/30'
                } border h-10 rounded-xl flex items-center justify-center text-xs font-mono text-white transition-all`}
              >
                {assistantState === 'disconnected' ? 'Connect' : 'Disconnect'}
              </button>
              <button
                onClick={toggleMute}
                disabled={assistantState === 'disconnected'}
                className="flex-1 bg-white/10 hover:bg-white/20 border border-white/10 h-10 rounded-xl flex items-center justify-center text-xs font-mono text-white transition-all disabled:opacity-40"
              >
                {isMuted ? 'Unmute' : 'Mute'}
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
