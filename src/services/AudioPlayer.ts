export class AudioPlayer {
  private audioContext: AudioContext | null = null;
  private analyserNode: AnalyserNode | null = null;
  private nextStartTime: number = 0;
  private activeSources: Set<AudioBufferSourceNode> = new Set();
  private sampleRate: number = 24000;
  private isPlaying: boolean = false;
  private onStateChange?: (isPlaying: boolean) => void;

  constructor(onStateChange?: (isPlaying: boolean) => void) {
    this.onStateChange = onStateChange;
  }

  private initAudioContext(): AudioContext {
    if (!this.audioContext || this.audioContext.state === 'closed') {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: this.sampleRate,
      });

      this.analyserNode = this.audioContext.createAnalyser();
      this.analyserNode.fftSize = 64;
      this.analyserNode.smoothingTimeConstant = 0.8;
      this.analyserNode.connect(this.audioContext.destination);
    }

    if (this.audioContext.state === 'suspended') {
      this.audioContext.resume();
    }

    return this.audioContext;
  }

  public playChunk(base64Pcm: string): void {
    const ctx = this.initAudioContext();
    const pcmData = this.base64ToFloat32(base64Pcm);

    if (pcmData.length === 0) return;

    const buffer = ctx.createBuffer(1, pcmData.length, this.sampleRate);
    buffer.getChannelData(0).set(pcmData);

    const source = ctx.createBufferSource();
    source.buffer = buffer;

    if (this.analyserNode) {
      source.connect(this.analyserNode);
    } else {
      source.connect(ctx.destination);
    }

    const now = ctx.currentTime;
    const startTime = Math.max(now, this.nextStartTime);
    source.start(startTime);
    this.nextStartTime = startTime + buffer.duration;

    this.activeSources.add(source);
    this.updatePlayingState(true);

    source.onended = () => {
      this.activeSources.delete(source);
      if (this.activeSources.size === 0 && ctx.currentTime >= this.nextStartTime) {
        this.updatePlayingState(false);
      }
    };
  }

  public interrupt(): void {
    for (const source of this.activeSources) {
      try {
        source.stop();
        source.disconnect();
      } catch (e) {
        // Source might already have ended
      }
    }
    this.activeSources.clear();
    if (this.audioContext) {
      this.nextStartTime = this.audioContext.currentTime;
    } else {
      this.nextStartTime = 0;
    }
    this.updatePlayingState(false);
  }

  public stop(): void {
    this.interrupt();
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
      this.audioContext = null;
    }
  }

  public getFrequencyData(): Uint8Array {
    if (!this.analyserNode) return new Uint8Array(0);
    const dataArray = new Uint8Array(this.analyserNode.frequencyBinCount);
    this.analyserNode.getByteFrequencyData(dataArray);
    return dataArray;
  }

  public getVolume(): number {
    const freq = this.getFrequencyData();
    if (freq.length === 0) return 0;
    let sum = 0;
    for (let i = 0; i < freq.length; i++) {
      sum += freq[i];
    }
    return sum / (freq.length * 255);
  }

  public getIsPlaying(): boolean {
    return this.isPlaying;
  }

  private updatePlayingState(playing: boolean): void {
    if (this.isPlaying !== playing) {
      this.isPlaying = playing;
      if (this.onStateChange) {
        this.onStateChange(playing);
      }
    }
  }

  private base64ToFloat32(base64: string): Float32Array {
    try {
      const binary = atob(base64);
      const bytes = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
      }

      const int16Array = new Int16Array(bytes.buffer);
      const float32Array = new Float32Array(int16Array.length);

      for (let i = 0; i < int16Array.length; i++) {
        float32Array[i] = int16Array[i] / 32768.0;
      }

      return float32Array;
    } catch (e) {
      console.error('Error decoding audio chunk base64:', e);
      return new Float32Array(0);
    }
  }
}
