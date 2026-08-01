import { AssistantState, FunctionCallItem, VoiceSettings } from '../types';
import { AudioPlayer } from './AudioPlayer';
import { AudioStreamer } from './AudioStreamer';
import { ToolManager } from './ToolManager';

export interface LiveSessionCallbacks {
  onStateChange: (state: AssistantState) => void;
  onError: (error: string) => void;
  onMicVolumeChange?: (volume: number) => void;
  onAudioOutputVolumeChange?: (volume: number) => void;
}

export class LiveSession {
  private ws: WebSocket | null = null;
  private audioStreamer: AudioStreamer | null = null;
  private audioPlayer: AudioPlayer | null = null;
  private toolManager: ToolManager;
  private currentState: AssistantState = 'disconnected';
  private callbacks: LiveSessionCallbacks;
  private isMuted: boolean = false;
  private animFrameId: number | null = null;

  constructor(toolManager: ToolManager, callbacks: LiveSessionCallbacks) {
    this.toolManager = toolManager;
    this.callbacks = callbacks;

    this.audioPlayer = new AudioPlayer((isPlaying) => {
      if (this.currentState === 'listening' || this.currentState === 'speaking') {
        this.setState(isPlaying ? 'speaking' : 'listening');
      }
    });
  }

  public async connect(voiceInput: VoiceSettings | string = 'Aoede'): Promise<void> {
    if (this.currentState !== 'disconnected') return;

    this.setState('connecting');

    try {
      // 1. Initialize Audio Streamer for mic input
      this.audioStreamer = new AudioStreamer((base64Pcm) => {
        if (this.ws && this.ws.readyState === WebSocket.OPEN && !this.isMuted) {
          this.ws.send(JSON.stringify({ audio: base64Pcm }));
        }
      });

      await this.audioStreamer.start();

      // 2. Build WebSocket URL with voice parameters
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      let queryParams = '';

      if (typeof voiceInput === 'string') {
        queryParams = `voice=${encodeURIComponent(voiceInput)}`;
      } else {
        queryParams = `voice=${encodeURIComponent(voiceInput.voice)}&gender=${encodeURIComponent(voiceInput.gender)}&style=${encodeURIComponent(voiceInput.style)}&speed=${encodeURIComponent(voiceInput.speed)}&warmth=${encodeURIComponent(voiceInput.warmth)}`;
      }

      const wsUrl = `${protocol}//${window.location.host}/live?${queryParams}`;

      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('[LiveSession] WS connected');
        this.setState('listening');
        this.startVolumeMonitoring();
      };

      this.ws.onmessage = async (event) => {
        try {
          const msg = JSON.parse(event.data);

          if (msg.error) {
            console.error('[LiveSession] Error from server:', msg.error);
            this.callbacks.onError(msg.error);
            this.disconnect();
            return;
          }

          if (msg.state) {
            if (msg.state === 'connected') {
              this.setState('listening');
            } else if (msg.state === 'disconnected') {
              this.disconnect();
            }
          }

          // Handle incoming audio chunk from model
          if (msg.audio) {
            if (this.audioPlayer) {
              this.audioPlayer.playChunk(msg.audio);
            }
          }

          // Handle barge-in / interruption signal
          if (msg.interrupted) {
            console.log('[LiveSession] Model turn interrupted by user');
            if (this.audioPlayer) {
              this.audioPlayer.interrupt();
            }
            this.setState('listening');
          }

          // Handle tool call execution
          if (msg.toolCall && msg.toolCall.functionCalls) {
            this.setState('processing');
            for (const call of msg.toolCall.functionCalls as FunctionCallItem[]) {
              const toolResponse = await this.toolManager.executeToolCall(call);
              if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                console.log('[LiveSession] Sending toolResponse back to server:', toolResponse);
                this.ws.send(JSON.stringify({ toolResponse }));
              }
            }
            if (!this.audioPlayer?.getIsPlaying()) {
              this.setState('listening');
            }
          }
        } catch (e) {
          console.error('[LiveSession] Error handling WS message:', e);
        }
      };

      this.ws.onerror = (err) => {
        console.error('[LiveSession] WS error:', err);
        this.callbacks.onError('WebSocket connection error');
        this.disconnect();
      };

      this.ws.onclose = () => {
        console.log('[LiveSession] WS closed');
        this.disconnect();
      };
    } catch (err: any) {
      console.error('[LiveSession] Failed to connect:', err);
      this.callbacks.onError(err.message || 'Microphone or connection access denied');
      this.disconnect();
    }
  }

  public disconnect(): void {
    this.stopVolumeMonitoring();

    if (this.audioStreamer) {
      this.audioStreamer.stop();
      this.audioStreamer = null;
    }

    if (this.audioPlayer) {
      this.audioPlayer.stop();
    }

    if (this.ws) {
      this.ws.onopen = null;
      this.ws.onmessage = null;
      this.ws.onerror = null;
      this.ws.onclose = null;
      if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
        this.ws.close();
      }
      this.ws = null;
    }

    this.setState('disconnected');
  }

  public sendScreenFrame(base64JpegData: string): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ image: base64JpegData }));
      return true;
    }
    return false;
  }

  public toggleMute(): boolean {
    this.isMuted = !this.isMuted;
    if (this.audioStreamer) {
      this.audioStreamer.setMute(this.isMuted);
    }
    return this.isMuted;
  }

  public getIsMuted(): boolean {
    return this.isMuted;
  }

  public getState(): AssistantState {
    return this.currentState;
  }

  public getAudioPlayer(): AudioPlayer | null {
    return this.audioPlayer;
  }

  private setState(state: AssistantState): void {
    if (this.currentState !== state) {
      this.currentState = state;
      this.callbacks.onStateChange(state);
    }
  }

  private startVolumeMonitoring(): void {
    const monitor = () => {
      if (this.audioStreamer && this.callbacks.onMicVolumeChange) {
        this.callbacks.onMicVolumeChange(this.audioStreamer.getVolume());
      }

      if (this.audioPlayer && this.callbacks.onAudioOutputVolumeChange) {
        this.callbacks.onAudioOutputVolumeChange(this.audioPlayer.getVolume());
      }

      if (this.currentState !== 'disconnected') {
        this.animFrameId = requestAnimationFrame(monitor);
      }
    };

    monitor();
  }

  private stopVolumeMonitoring(): void {
    if (this.animFrameId !== null) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
  }
}
