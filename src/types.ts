export type AssistantState =
  | 'disconnected'
  | 'connecting'
  | 'listening'
  | 'speaking'
  | 'processing'
  | 'screensharing'
  | 'analyzing'
  | 'paused'
  | 'stopped';

export type ScreenShareType = 'screen' | 'window' | 'tab' | 'unknown';

export interface ScreenVisionState {
  isSharing: boolean;
  isPaused: boolean;
  shareType: ScreenShareType;
  fps: number;
  lastCapturedTime: number | null;
  lastFramePreview: string | null;
  activeApp?: string;
  detectedElementsCount?: number;
  resolution?: string;
  frameCount?: number;
  blobSizeBytes?: number;
  captureDurationMs?: number;
}

export interface DesktopActionRequest {
  id: string;
  actionName: string;
  description: string;
  args: Record<string, any>;
  timestamp: number;
}

export type ThemeMode = 'neon' | 'cosmic' | 'cyber' | 'aurora' | 'sunset';

export type PrebuiltVoice = 'Aoede' | 'Kore' | 'Zephyr' | 'Fenrir' | 'Puck';

export type VoiceGender = 'Female' | 'Male';
export type SpeakingStyle = 'Calm' | 'Friendly' | 'Professional' | 'Energetic' | 'Cheerful';
export type SpeakingSpeed = 'Slow' | 'Normal' | 'Fast';
export type VoiceWarmth = 'Soft' | 'Neutral' | 'Deep';

export interface VoiceSettings {
  gender: VoiceGender;
  voice: PrebuiltVoice;
  style: SpeakingStyle;
  speed: SpeakingSpeed;
  warmth: VoiceWarmth;
}

export interface ActiveTimer {
  id: string;
  label: string;
  totalSeconds: number;
  remainingSeconds: number;
  isPaused: boolean;
  createdAt: number;
}

export interface OpenedWebsite {
  id: string;
  url: string;
  title: string;
  timestamp: number;
}

export interface SearchQuery {
  id: string;
  query: string;
  timestamp: number;
}

export interface FunctionCallItem {
  id: string;
  name: string;
  args: Record<string, any>;
}

export interface ToolCallMessage {
  functionCalls: FunctionCallItem[];
}

export interface FunctionResponseItem {
  id: string;
  name: string;
  response: {
    output: Record<string, any>;
  };
}

export interface LiveMessage {
  audio?: string;
  interrupted?: boolean;
  toolCall?: ToolCallMessage;
  state?: AssistantState;
  error?: string;
}

export type MemoryCategory =
  | 'identity'
  | 'preference'
  | 'relationship'
  | 'project'
  | 'goal'
  | 'routine'
  | 'device'
  | 'conversation'
  | 'emotional';

export type ImportanceLevel = 'Critical' | 'High' | 'Medium' | 'Low';

export interface MemoryItem {
  id: string;
  title: string;
  category: MemoryCategory;
  value: string;
  importance: ImportanceLevel;
  confidence: number;
  source: string;
  dateCreated: number;
  lastUpdated: number;
  timesReferenced: number;
  tags: string[];
  summary: string;
}

