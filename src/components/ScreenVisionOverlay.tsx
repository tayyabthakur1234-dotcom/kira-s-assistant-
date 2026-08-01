import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Monitor,
  Eye,
  Pause,
  Play,
  Square,
  Sparkles,
  MousePointer,
  CheckCircle2,
  XCircle,
  Maximize2,
  Minimize2,
  ShieldAlert,
  Target,
  Zap,
} from 'lucide-react';
import { DesktopActionRequest, ScreenVisionState } from '../types';

interface ScreenVisionOverlayProps {
  visionState: ScreenVisionState;
  onStopShare: () => void;
  onPauseVision: () => void;
  onResumeVision: () => void;
  onAnalyzeNow: () => void;
  highlightRegion?: { label: string; description: string; xPercent: number; yPercent: number } | null;
  pendingDesktopAction?: DesktopActionRequest | null;
  onApproveAction?: (actionId: string) => void;
  onRejectAction?: (actionId: string) => void;
  onDismissHighlight?: () => void;
}

export const ScreenVisionOverlay: React.FC<ScreenVisionOverlayProps> = ({
  visionState,
  onStopShare,
  onPauseVision,
  onResumeVision,
  onAnalyzeNow,
  highlightRegion,
  pendingDesktopAction,
  onApproveAction,
  onRejectAction,
  onDismissHighlight, }) => {
  const [isMinimized, setIsMinimized] = useState(false);
  const [autoApproveActions, setAutoApproveActions] = useState(false);

  // Automatically approve actions if setting is enabled
  useEffect(() => {
    if (pendingDesktopAction && autoApproveActions && onApproveAction) {
      onApproveAction(pendingDesktopAction.id);
    }
  }, [pendingDesktopAction, autoApproveActions, onApproveAction]);

  if (!visionState.isSharing) return null;

  return (
    <>
      {/* 1. Floating Screen Vision HUD Widget */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="fixed bottom-6 right-6 z-40 max-w-sm w-full bg-slate-950/85 backdrop-blur-xl border border-red-500/30 shadow-2xl rounded-2xl overflow-hidden"
      >
        {/* HUD Top Bar */}
        <div className="flex items-center justify-between px-4 py-3 bg-red-950/40 border-b border-red-500/20">
          <div className="flex items-center space-x-2.5">
            <span className="relative flex h-2.5 w-2.5">
              {!visionState.isPaused && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              )}
              <span
                className={`relative inline-flex rounded-full h-2.5 w-2.5 ${
                  visionState.isPaused ? 'bg-amber-400' : 'bg-red-500'
                }`}
              ></span>
            </span>

            <div className="flex items-center space-x-1.5">
              <Monitor className="w-4 h-4 text-red-400" />
              <span className="text-xs font-bold tracking-wide uppercase text-white">
                Kira Vision {visionState.isPaused ? '(Paused)' : 'Active'}
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              title={isMinimized ? 'Expand HUD' : 'Minimize HUD'}
            >
              {isMinimized ? <Maximize2 className="w-3.5 h-3.5" /> : <Minimize2 className="w-3.5 h-3.5" />}
            </button>
            <button
              onClick={onStopShare}
              className="p-1.5 rounded-lg bg-red-600/80 hover:bg-red-500 text-white transition-colors"
              title="Stop Sharing Screen"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
            </button>
          </div>
        </div>

        {/* HUD Body */}
        {!isMinimized && (
          <div className="p-4 space-y-3">
            {/* Realtime Live Screen Preview Thumbnail */}
            <div className="relative rounded-xl overflow-hidden border border-white/10 bg-black aspect-video flex items-center justify-center group">
              {visionState.lastFramePreview ? (
                <img
                  src={visionState.lastFramePreview}
                  alt="Live Screen Capture"
                  className={`w-full h-full object-contain transition-opacity duration-300 ${
                    visionState.isPaused ? 'opacity-40 grayscale' : 'opacity-100'
                  }`}
                />
              ) : (
                <div className="text-center p-4">
                  <Eye className="w-8 h-8 text-red-400 animate-pulse mx-auto mb-2" />
                  <span className="text-xs text-slate-400 block font-mono">Initializing Screen Stream...</span>
                </div>
              )}

              {/* Status Badge Overlay */}
              <div className="absolute top-2 left-2 px-2 py-1 rounded-md bg-slate-950/85 border border-white/10 backdrop-blur-md flex items-center space-x-1.5 text-[10px] font-mono text-slate-300">
                <span className="capitalize text-red-300 font-semibold">{visionState.shareType} share</span>
                {visionState.resolution && <span>• {visionState.resolution}</span>}
                <span>• ~{visionState.fps} FPS</span>
              </div>

              {/* Debug Metrics Badge Overlay (Requirement 8) */}
              {visionState.frameCount !== undefined && (
                <div className="absolute bottom-2 left-2 right-2 px-2 py-1 rounded-md bg-slate-950/85 border border-white/10 backdrop-blur-md flex items-center justify-between text-[9px] font-mono text-slate-300">
                  <span>Frame #{visionState.frameCount}</span>
                  {visionState.blobSizeBytes !== undefined && (
                    <span>{Math.round(visionState.blobSizeBytes / 1024)} KB</span>
                  )}
                  {visionState.captureDurationMs !== undefined && (
                    <span>{visionState.captureDurationMs}ms</span>
                  )}
                  {visionState.lastCapturedTime && (
                    <span>{new Date(visionState.lastCapturedTime).toLocaleTimeString([], { hour12: false, minute: '2-digit', second: '2-digit' })}</span>
                  )}
                </div>
              )}

              {visionState.isPaused && (
                <div className="absolute inset-0 flex items-center justify-center bg-slate-950/60 backdrop-blur-xs">
                  <span className="px-3 py-1.5 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-xs font-semibold flex items-center space-x-1.5">
                    <Pause className="w-3.5 h-3.5" />
                    <span>Vision Processing Paused</span>
                  </span>
                </div>
              )}
            </div>

            {/* Quick Action Controls */}
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={onAnalyzeNow}
                disabled={visionState.isPaused}
                className="py-2 px-3 rounded-xl bg-indigo-600/90 hover:bg-indigo-500 disabled:opacity-50 text-white text-xs font-semibold flex items-center justify-center space-x-1.5 transition-all shadow-md"
              >
                <Sparkles className="w-3.5 h-3.5 text-indigo-200" />
                <span>Analyze Screen</span>
              </button>

              <button
                onClick={visionState.isPaused ? onResumeVision : onPauseVision}
                className="py-2 px-3 rounded-xl bg-white/10 hover:bg-white/20 text-white text-xs font-semibold flex items-center justify-center space-x-1.5 transition-all"
              >
                {visionState.isPaused ? (
                  <>
                    <Play className="w-3.5 h-3.5 text-green-400" />
                    <span>Resume Stream</span>
                  </>
                ) : (
                  <>
                    <Pause className="w-3.5 h-3.5 text-amber-400" />
                    <span>Pause Stream</span>
                  </>
                )}
              </button>
            </div>

            {/* Safety & Auto Approve Option */}
            <div className="flex items-center justify-between pt-2 border-t border-white/10 text-[11px] text-slate-400 font-mono">
              <span className="flex items-center space-x-1">
                <ShieldAlert className="w-3.5 h-3.5 text-indigo-400" />
                <span>Action Approval</span>
              </span>
              <label className="flex items-center space-x-1.5 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoApproveActions}
                  onChange={(e) => setAutoApproveActions(e.target.checked)}
                  className="rounded border-white/20 bg-white/5 text-indigo-600 focus:ring-0"
                />
                <span className={autoApproveActions ? 'text-indigo-300 font-semibold' : 'text-slate-400'}>
                  Auto-allow
                </span>
              </label>
            </div>
          </div>
        )}
      </motion.div>

      {/* 2. On-Screen Target Pointer / Highlight Box */}
      <AnimatePresence>
        {highlightRegion && (
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.5, opacity: 0 }}
            style={{
              left: `${highlightRegion.xPercent}%`,
              top: `${highlightRegion.yPercent}%`,
            }}
            className="fixed z-50 -translate-x-1/2 -translate-y-1/2 pointer-events-none"
          >
            <div className="relative flex items-center justify-center">
              {/* Pulsing Target Ring */}
              <div className="w-20 h-20 rounded-full border-2 border-indigo-400 animate-ping absolute inset-0 opacity-75"></div>
              <div className="w-16 h-16 rounded-2xl border-2 border-cyan-400 bg-cyan-500/20 backdrop-blur-xs flex items-center justify-center shadow-2xl">
                <Target className="w-8 h-8 text-cyan-300 animate-bounce" />
              </div>

              {/* Tooltip Label */}
              <div className="absolute top-20 left-1/2 -translate-x-1/2 bg-slate-900/95 border border-cyan-400/50 px-3 py-1.5 rounded-xl shadow-2xl text-center whitespace-nowrap pointer-events-auto">
                <span className="text-xs font-bold text-cyan-300 block">{highlightRegion.label}</span>
                <span className="text-[11px] text-slate-300 block">{highlightRegion.description}</span>
                <button
                  onClick={onDismissHighlight}
                  className="text-[10px] text-slate-400 hover:text-white underline mt-1 block mx-auto"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 3. Pending Desktop Action Approval Modal */}
      <AnimatePresence>
        {pendingDesktopAction && !autoApproveActions && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 10 }}
              className="max-w-md w-full bg-slate-900 border border-indigo-500/40 rounded-3xl p-6 shadow-2xl space-y-4"
            >
              <div className="flex items-center space-x-3 text-indigo-400">
                <div className="p-3 rounded-2xl bg-indigo-500/20 border border-indigo-500/30">
                  <Zap className="w-6 h-6 text-indigo-300" />
                </div>
                <div>
                  <h4 className="text-base font-bold text-white">Desktop Action Requested</h4>
                  <span className="text-xs text-slate-400 font-mono">Kira AI Screen Control</span>
                </div>
              </div>

              <div className="p-4 rounded-2xl bg-white/5 border border-white/10 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono text-indigo-300">
                  <span className="uppercase font-bold">{pendingDesktopAction.actionName}</span>
                  <span>{new Date(pendingDesktopAction.timestamp).toLocaleTimeString()}</span>
                </div>
                <p className="text-sm font-medium text-slate-200">{pendingDesktopAction.description}</p>
                {Object.keys(pendingDesktopAction.args).length > 0 && (
                  <pre className="text-[11px] font-mono text-slate-400 bg-black/40 p-2 rounded-xl overflow-x-auto">
                    {JSON.stringify(pendingDesktopAction.args, null, 2)}
                  </pre>
                )}
              </div>

              <p className="text-xs text-slate-400">
                Kira requires your explicit confirmation before interacting with your desktop. Do you approve this action?
              </p>

              <div className="flex space-x-3 pt-2">
                <button
                  onClick={() => onRejectAction && onRejectAction(pendingDesktopAction.id)}
                  className="flex-1 py-2.5 px-4 rounded-xl border border-white/10 bg-white/5 hover:bg-white/10 text-slate-300 text-xs font-semibold flex items-center justify-center space-x-2 transition-all"
                >
                  <XCircle className="w-4 h-4 text-red-400" />
                  <span>Reject</span>
                </button>
                <button
                  onClick={() => onApproveAction && onApproveAction(pendingDesktopAction.id)}
                  className="flex-1 py-2.5 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center justify-center space-x-2 transition-all shadow-lg shadow-indigo-600/30"
                >
                  <CheckCircle2 className="w-4 h-4 text-green-300" />
                  <span>Approve & Execute</span>
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
};
