import { ScreenShareType, ScreenVisionState } from '../types';

export interface ScreenStreamerCallbacks {
  onFrameCaptured: (base64Data: string, previewUrl: string) => void;
  onStateChange: (state: ScreenVisionState) => void;
  onError: (error: string) => void;
}

export class ScreenStreamer {
  private mediaStream: MediaStream | null = null;
  private videoElement: HTMLVideoElement | null = null;
  private canvasElement: HTMLCanvasElement | null = null;
  private captureTimer: number | null = null;
  private callbacks: ScreenStreamerCallbacks;
  private isPaused: boolean = false;
  private captureIntervalMs: number = 1000; // Capture frame every 1s
  private lastCapturedPreview: string | null = null;
  private shareType: ScreenShareType = 'unknown';

  // Quality & Debug Metrics
  private frameCount: number = 0;
  private lastResolution: string = '0x0';
  private lastBlobSizeBytes: number = 0;
  private lastCaptureDurationMs: number = 0;
  private lastFrameTimestamp: number | null = null;
  private isCapturing: boolean = false;
  private lastSamplePixels: Uint8ClampedArray | null = null;

  constructor(callbacks: ScreenStreamerCallbacks) {
    this.callbacks = callbacks;
  }

  public async startShare(): Promise<boolean> {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        throw new Error('Screen capture API is not supported in this browser.');
      }

      // 1. Native Screen Capture with full 1080p/4K ideal constraints
      this.mediaStream = await navigator.mediaDevices.getDisplayMedia({
        video: {
          displaySurface: 'monitor',
          width: { ideal: 1920, max: 3840 },
          height: { ideal: 1080, max: 2160 },
          frameRate: { ideal: 10, max: 15 },
        } as any,
        audio: false,
      });

      const videoTrack = this.mediaStream.getVideoTracks()[0];
      if (!videoTrack) {
        throw new Error('No video track available from screen capture.');
      }

      // Determine display share type
      const settings = videoTrack.getSettings() as any;
      if (settings.displaySurface) {
        if (settings.displaySurface === 'monitor') this.shareType = 'screen';
        else if (settings.displaySurface === 'window') this.shareType = 'window';
        else if (settings.displaySurface === 'browser') this.shareType = 'tab';
      } else {
        this.shareType = 'screen';
      }

      // Track end listener (triggered by browser UI bar or revoked permission)
      videoTrack.onended = () => {
        console.log('[ScreenStreamer] Screen sharing track ended by user');
        this.stopShare();
      };

      // Create video element for screen stream
      this.videoElement = document.createElement('video');
      this.videoElement.autoplay = true;
      this.videoElement.muted = true;
      this.videoElement.playsInline = true;
      this.videoElement.srcObject = this.mediaStream;

      this.canvasElement = document.createElement('canvas');

      // 3. Wait until video is ready: loadedmetadata AND readyState >= HAVE_CURRENT_DATA (2)
      await new Promise<void>((resolve) => {
        if (!this.videoElement) return resolve();

        const checkReady = () => {
          if (
            this.videoElement &&
            this.videoElement.readyState >= 2 &&
            this.videoElement.videoWidth > 0 &&
            this.videoElement.videoHeight > 0
          ) {
            resolve();
          } else {
            requestAnimationFrame(checkReady);
          }
        };

        this.videoElement.onloadedmetadata = () => {
          this.videoElement?.play().then(() => checkReady()).catch(console.error);
        };

        if (this.videoElement.readyState >= 1) {
          this.videoElement.play().then(() => checkReady()).catch(console.error);
        }
      });

      this.isPaused = false;
      this.frameCount = 0;
      this.startFrameCaptureLoop();
      this.notifyState();

      return true;
    } catch (err: any) {
      console.error('[ScreenStreamer] Failed to start screen share:', err);
      const isIframe = typeof window !== 'undefined' && window.self !== window.top;
      let userMsg = err.message || 'Screen capture permission denied or failed.';

      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        if (isIframe) {
          userMsg =
            'Screen capture was denied or blocked by the preview iframe. Please open the app in a new tab (using the pop-out icon top-right) to allow screen sharing!';
        } else {
          userMsg = 'Screen sharing prompt was cancelled or permission was denied.';
        }
      } else if (isIframe && (err.name === 'SecurityError' || err.name === 'InvalidStateError')) {
        userMsg = 'Browser restricted screen sharing in embedded iframe. Please open in a new tab to share your desktop.';
      }

      this.callbacks.onError(userMsg);
      this.stopShare();
      return false;
    }
  }

  public stopShare(): void {
    if (this.captureTimer !== null) {
      window.clearInterval(this.captureTimer);
      this.captureTimer = null;
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }

    if (this.videoElement) {
      this.videoElement.srcObject = null;
      this.videoElement = null;
    }

    this.canvasElement = null;
    this.isPaused = false;
    this.shareType = 'unknown';
    this.lastCapturedPreview = null;
    this.lastSamplePixels = null;

    this.notifyState();
  }

  public pause(): void {
    this.isPaused = true;
    this.notifyState();
  }

  public pauseVision(): void {
    this.pause();
  }

  public resume(): void {
    this.isPaused = false;
    this.captureFrameNow();
    this.notifyState();
  }

  public resumeVision(): void {
    this.resume();
  }

  /**
   * Captures a frame directly from the current active screen stream.
   * Ensures canvas dimensions match the source video dimensions exactly without intermediate scaling or resizing,
   * and encodes using canvas.toBlob with image/jpeg at 0.95 quality.
   */
  public async captureFrameNow(): Promise<string | null> {
    if (!this.videoElement || !this.canvasElement || !this.mediaStream || this.isCapturing) {
      return null;
    }

    const video = this.videoElement;
    if (video.readyState < 2 || video.videoWidth === 0 || video.videoHeight === 0) {
      return null;
    }

    this.isCapturing = true;
    const startTime = performance.now();

    try {
      const canvas = this.canvasElement;
      const ctx = canvas.getContext('2d', { alpha: false });
      if (!ctx) return null;

      // Ensure canvas dimensions match source video dimensions exactly without intermediate scaling
      const sourceWidth = video.videoWidth;
      const sourceHeight = video.videoHeight;

      if (canvas.width !== sourceWidth) {
        canvas.width = sourceWidth;
      }
      if (canvas.height !== sourceHeight) {
        canvas.height = sourceHeight;
      }

      // Draw source video onto canvas at exact 1:1 pixel dimensions
      ctx.drawImage(video, 0, 0, sourceWidth, sourceHeight);

      // Screen Change Detection sampling
      this.detectScreenChange(ctx, sourceWidth, sourceHeight);

      // High Quality Encoding using canvas.toBlob() with image/jpeg at 0.95 quality
      const blob = await new Promise<Blob | null>((resolve) => {
        canvas.toBlob((b) => resolve(b), 'image/jpeg', 0.95);
      });

      if (!blob) {
        throw new Error('Failed to create JPEG image blob from canvas.');
      }

      // Convert Blob to Base64 data URL
      const dataUrl = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      });

      const base64Data = dataUrl.replace(/^data:image\/jpeg;base64,/, '');
      const durationMs = Math.round(performance.now() - startTime);

      // Update metrics
      this.frameCount++;
      this.lastResolution = `${sourceWidth}x${sourceHeight}`;
      this.lastBlobSizeBytes = blob.size;
      this.lastCaptureDurationMs = durationMs;
      this.lastFrameTimestamp = Date.now();
      this.lastCapturedPreview = dataUrl;

      console.log('[ScreenStreamer] High-Res Frame Captured:', {
        videoWidth: sourceWidth,
        videoHeight: sourceHeight,
        canvasWidth: canvas.width,
        canvasHeight: canvas.height,
        captureDurationMs: durationMs,
        blobSizeBytes: blob.size,
        frameTimestamp: this.lastFrameTimestamp,
        frameCount: this.frameCount,
      });

      this.callbacks.onFrameCaptured(base64Data, dataUrl);
      this.notifyState();

      return base64Data;
    } catch (err) {
      console.error('[ScreenStreamer] Error during frame capture:', err);
      return null;
    } finally {
      this.isCapturing = false;
    }
  }

  public isSharing(): boolean {
    return !!this.mediaStream && this.mediaStream.active;
  }

  public isVisionPaused(): boolean {
    return this.isPaused;
  }

  public getLastPreview(): string | null {
    return this.lastCapturedPreview;
  }

  private startFrameCaptureLoop(): void {
    if (this.captureTimer !== null) {
      window.clearInterval(this.captureTimer);
    }

    // Capture first fresh frame immediately once ready
    setTimeout(() => {
      this.captureFrameNow();
    }, 200);

    // Periodic capture loop
    this.captureTimer = window.setInterval(() => {
      if (!this.isPaused && this.isSharing()) {
        this.captureFrameNow();
      }
    }, this.captureIntervalMs);
  }

  /**
   * 7. Detect significant screen changes between frames
   */
  private detectScreenChange(ctx: CanvasRenderingContext2D, width: number, height: number): void {
    try {
      // Sample 10x10 grid of pixels to test for screen content change
      const sampleCanvas = document.createElement('canvas');
      sampleCanvas.width = 16;
      sampleCanvas.height = 16;
      const sampleCtx = sampleCanvas.getContext('2d');
      if (!sampleCtx) return;

      sampleCtx.drawImage(ctx.canvas, 0, 0, 16, 16);
      const imgData = sampleCtx.getImageData(0, 0, 16, 16).data;

      if (this.lastSamplePixels) {
        let diff = 0;
        for (let i = 0; i < imgData.length; i += 4) {
          diff += Math.abs(imgData[i] - this.lastSamplePixels[i]);
          diff += Math.abs(imgData[i + 1] - this.lastSamplePixels[i + 1]);
          diff += Math.abs(imgData[i + 2] - this.lastSamplePixels[i + 2]);
        }
        if (diff > 1500) {
          console.log('[ScreenStreamer] Significant screen change detected! Pixel diff:', diff);
        }
      }
      this.lastSamplePixels = imgData;
    } catch (e) {
      // Ignore cross-origin context warnings if any
    }
  }

  private notifyState(): void {
    const isSharing = this.isSharing();
    this.callbacks.onStateChange({
      isSharing,
      isPaused: this.isPaused,
      shareType: this.shareType,
      fps: isSharing && !this.isPaused ? Math.round((1000 / this.captureIntervalMs) * 10) / 10 : 0,
      lastCapturedTime: this.lastFrameTimestamp,
      lastFramePreview: this.lastCapturedPreview,
      resolution: this.lastResolution,
      frameCount: this.frameCount,
      blobSizeBytes: this.lastBlobSizeBytes,
      captureDurationMs: this.lastCaptureDurationMs,
    });
  }
}

