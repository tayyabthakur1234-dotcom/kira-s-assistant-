import { ActiveTimer, FunctionCallItem, FunctionResponseItem, OpenedWebsite, ThemeMode, VoiceSettings } from '../types';

export interface ToolManagerCallbacks {
  onOpenWebsite?: (site: OpenedWebsite) => void;
  onSetTimer?: (timer: ActiveTimer) => void;
  onChangeTheme?: (theme: ThemeMode) => void;
  onChangeVoiceSettings?: (voiceSettings: Partial<VoiceSettings>) => void;
  onSearchQuery?: (query: string) => void;
  onToolExecuted?: (toolName: string, args: Record<string, any>, result: any) => void;
  onDesktopActionRequested?: (action: {
    id: string;
    actionName: string;
    description: string;
    args: Record<string, any>;
    timestamp: number;
  }) => void;
  onHighlightRegion?: (label: string, description: string, xPercent?: number, yPercent?: number) => void;
  onScreenAnalyzeRequested?: () => void;
}

export class ToolManager {
  private callbacks: ToolManagerCallbacks;

  constructor(callbacks: ToolManagerCallbacks = {}) {
    this.callbacks = callbacks;
  }

  public async executeToolCall(call: FunctionCallItem): Promise<FunctionResponseItem> {
    const { id, name, args } = call;
    console.log(`[ToolManager] Executing tool: ${name}`, args);

    let result: Record<string, any> = {};

    try {
      switch (name) {
        case 'openWebsite': {
          let url = args.url || '';
          if (!url.startsWith('http://') && !url.startsWith('https://')) {
            url = 'https://' + url;
          }
          const title = args.title || url.replace(/^https?:\/\//, '');

          const site: OpenedWebsite = {
            id: 'site_' + Date.now(),
            url,
            title,
            timestamp: Date.now(),
          };

          if (this.callbacks.onOpenWebsite) {
            this.callbacks.onOpenWebsite(site);
          }

          // Try opening in new window/tab as fallback
          try {
            window.open(url, '_blank', 'noopener,noreferrer');
          } catch (e) {
            // Popup blocker might intercept
          }

          result = {
            status: 'success',
            message: `Website ${title} opened successfully.`,
            url,
          };
          break;
        }

        case 'searchWeb': {
          const query = args.query || '';
          const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(query)}`;

          if (this.callbacks.onSearchQuery) {
            this.callbacks.onSearchQuery(query);
          }

          if (this.callbacks.onOpenWebsite) {
            this.callbacks.onOpenWebsite({
              id: 'search_' + Date.now(),
              url: searchUrl,
              title: `Search: ${query}`,
              timestamp: Date.now(),
            });
          }

          result = {
            status: 'success',
            query,
            searchUrl,
            message: `Search initiated for '${query}'.`,
          };
          break;
        }

        case 'getCurrentTime': {
          const now = new Date();
          const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          const dateString = now.toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
          const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

          result = {
            time: timeString,
            date: dateString,
            timezone,
            formatted: `It is currently ${timeString} on ${dateString} (${timezone}).`,
          };
          break;
        }

        case 'setTimer': {
          const durationSeconds = Math.max(1, Number(args.durationSeconds) || 60);
          const label = args.label || `Timer (${durationSeconds}s)`;

          const newTimer: ActiveTimer = {
            id: 'timer_' + Date.now(),
            label,
            totalSeconds: durationSeconds,
            remainingSeconds: durationSeconds,
            isPaused: false,
            createdAt: Date.now(),
          };

          if (this.callbacks.onSetTimer) {
            this.callbacks.onSetTimer(newTimer);
          }

          result = {
            status: 'success',
            timerId: newTimer.id,
            durationSeconds,
            label,
            message: `Timer '${label}' set for ${durationSeconds} seconds.`,
          };
          break;
        }

        case 'calculateMath': {
          const expr = args.expression || '0';
          let calcResult: any = 0;

          try {
            // Safe evaluation for basic math
            const sanitized = expr.replace(/[^0-9+\-*/().^%\s]/g, '');
            // Convert ^ to ** for exponentiation
            const jsExpr = sanitized.replace(/\^/g, '**');
            // eslint-disable-next-line no-new-func
            calcResult = new Function(`return (${jsExpr})`)();
          } catch (e) {
            calcResult = 'Invalid mathematical expression';
          }

          result = {
            expression: expr,
            result: String(calcResult),
            formatted: `${expr} = ${calcResult}`,
          };
          break;
        }

        case 'changeThemeMode': {
          const theme = (args.theme || 'neon').toLowerCase() as ThemeMode;
          const validThemes: ThemeMode[] = ['neon', 'cosmic', 'cyber', 'aurora', 'sunset'];
          const selectedTheme = validThemes.includes(theme) ? theme : 'neon';

          if (this.callbacks.onChangeTheme) {
            this.callbacks.onChangeTheme(selectedTheme);
          }

          result = {
            status: 'success',
            activeTheme: selectedTheme,
            message: `UI visual theme changed to ${selectedTheme}.`,
          };
          break;
        }

        case 'changeVoiceSettings': {
          const gender = args.gender;
          const voice = args.voice;
          const style = args.style;
          const speed = args.speed;
          const warmth = args.warmth;

          if (this.callbacks.onChangeVoiceSettings) {
            this.callbacks.onChangeVoiceSettings({
              gender,
              voice,
              style,
              speed,
              warmth,
            });
          }

          result = {
            status: 'success',
            message: `Voice settings updated successfully: gender=${gender || 'current'}, voice=${voice || 'current'}, style=${style || 'current'}, speed=${speed || 'current'}, warmth=${warmth || 'current'}.`,
          };
          break;
        }

        case 'saveMemory': {
          const title = args.title || 'Note';
          const category = args.category || 'identity';
          const value = args.value || '';
          const importance = args.importance || 'Medium';
          const confidence = args.confidence ? Number(args.confidence) : 90;
          const summary = args.summary || `${title}: ${value}`;

          try {
            const res = await fetch('/api/memories', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ title, category, value, importance, confidence, summary }),
            });
            const data = await res.json();
            result = {
              status: 'success',
              savedMemory: data.memory,
              message: `Fact saved into Kira's brain: "${title} - ${value}"`,
            };
          } catch (e: any) {
            result = { status: 'error', message: e.message || 'Failed to save memory' };
          }
          break;
        }

        case 'searchMemories': {
          const query = args.query || '';
          const category = args.category || '';

          try {
            const params = new URLSearchParams();
            if (query) params.append('q', query);
            if (category) params.append('category', category);

            const res = await fetch(`/api/memories?${params.toString()}`);
            const data = await res.json();
            result = {
              status: 'success',
              resultsCount: data.memories ? data.memories.length : 0,
              memories: data.memories || [],
              message: `Retrieved ${data.memories ? data.memories.length : 0} matching memories for '${query}'.`,
            };
          } catch (e: any) {
            result = { status: 'error', message: e.message || 'Failed to search memories' };
          }
          break;
        }

        case 'forgetMemory': {
          const query = args.query || '';
          const category = args.category || '';
          const deleteAll = Boolean(args.deleteAll);

          try {
            const res = await fetch('/api/memories/forget', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ query, category, deleteAll }),
            });
            const data = await res.json();
            result = {
              status: 'success',
              deletedCount: data.deletedCount || 0,
              message: deleteAll
                ? "Wiped all memories from Kira's brain."
                : `Forgot ${data.deletedCount || 0} memory item(s).`,
            };
          } catch (e: any) {
            result = { status: 'error', message: e.message || 'Failed to forget memory' };
          }
          break;
        }

        case 'getBrainSummary': {
          try {
            const res = await fetch('/api/memories');
            const data = await res.json();
            const memories = data.memories || [];

            const summary = memories.map((m: any) => `[${m.category}] ${m.title}: ${m.value}`).join('; ');
            result = {
              status: 'success',
              totalMemories: memories.length,
              memoriesSummary: summary,
              message: `Kira currently remembers ${memories.length} facts about you.`,
            };
          } catch (e: any) {
            result = { status: 'error', message: e.message || 'Failed to fetch brain summary' };
          }
          break;
        }

        case 'analyzeScreen': {
          if (this.callbacks.onScreenAnalyzeRequested) {
            this.callbacks.onScreenAnalyzeRequested();
          }
          result = {
            status: 'success',
            message: `Screen frame capture triggered for topic: '${args.focusTopic || 'general layout'}'. Observing visible windows, text, and active software.`,
          };
          break;
        }

        case 'highlightScreenRegion': {
          const label = args.label || 'Screen Focus';
          const description = args.description || 'Focus area highlighted';
          const xPercent = args.xPercent !== undefined ? Number(args.xPercent) : 50;
          const yPercent = args.yPercent !== undefined ? Number(args.yPercent) : 50;

          if (this.callbacks.onHighlightRegion) {
            this.callbacks.onHighlightRegion(label, description, xPercent, yPercent);
          }

          result = {
            status: 'success',
            highlighted: { label, description, xPercent, yPercent },
            message: `Highlighted region '${label}' on user screen at approx (${xPercent}%, ${yPercent}%).`,
          };
          break;
        }

        case 'clickScreenElement': {
          const elementName = args.elementName || 'UI Element';
          const actionReq = {
            id: 'act_' + Date.now(),
            actionName: 'Click Element',
            description: `Click on '${elementName}' on desktop screen`,
            args,
            timestamp: Date.now(),
          };

          if (this.callbacks.onDesktopActionRequested) {
            this.callbacks.onDesktopActionRequested(actionReq);
          }

          result = {
            status: 'success',
            actionExecuted: 'clickScreenElement',
            elementName,
            message: `Requested desktop action to click '${elementName}'.`,
          };
          break;
        }

        case 'typeTextOnScreen': {
          const text = args.text || '';
          const targetInputName = args.targetInputName || 'Active Field';
          const actionReq = {
            id: 'act_' + Date.now(),
            actionName: 'Type Text',
            description: `Type '${text}' into ${targetInputName}`,
            args,
            timestamp: Date.now(),
          };

          if (this.callbacks.onDesktopActionRequested) {
            this.callbacks.onDesktopActionRequested(actionReq);
          }

          result = {
            status: 'success',
            typedText: text,
            message: `Typed text into '${targetInputName}' on screen.`,
          };
          break;
        }

        case 'scrollScreen': {
          const direction = args.direction || 'down';
          const amountPixels = Number(args.amountPixels) || 300;
          const actionReq = {
            id: 'act_' + Date.now(),
            actionName: 'Scroll Window',
            description: `Scroll ${direction} by ${amountPixels}px`,
            args,
            timestamp: Date.now(),
          };

          if (this.callbacks.onDesktopActionRequested) {
            this.callbacks.onDesktopActionRequested(actionReq);
          }

          // Also execute browser window scroll
          if (typeof window !== 'undefined') {
            window.scrollBy({
              top: direction === 'down' ? amountPixels : -amountPixels,
              behavior: 'smooth',
            });
          }

          result = {
            status: 'success',
            direction,
            amountPixels,
            message: `Scrolled screen ${direction} by ${amountPixels}px.`,
          };
          break;
        }

        case 'openDesktopApp': {
          const appName = args.appName || 'Application';
          const actionReq = {
            id: 'act_' + Date.now(),
            actionName: 'Open / Switch App',
            description: `Launch or focus desktop software: '${appName}'`,
            args,
            timestamp: Date.now(),
          };

          if (this.callbacks.onDesktopActionRequested) {
            this.callbacks.onDesktopActionRequested(actionReq);
          }

          result = {
            status: 'success',
            appName,
            message: `Desktop action requested to open '${appName}'.`,
          };
          break;
        }

        case 'takeScreenShot': {
          const note = args.note || 'Screen Snapshot';
          const actionReq = {
            id: 'act_' + Date.now(),
            actionName: 'Take Screenshot',
            description: `Save high-res screen artifact: ${note}`,
            args,
            timestamp: Date.now(),
          };

          if (this.callbacks.onDesktopActionRequested) {
            this.callbacks.onDesktopActionRequested(actionReq);
          }

          result = {
            status: 'success',
            note,
            timestamp: Date.now(),
            message: `Captured screen snapshot artifact.`,
          };
          break;
        }

        case 'copyPasteText': {
          const action = args.action || 'copy';
          const content = args.content || '';

          if (action === 'copy' && content && navigator.clipboard) {
            try {
              await navigator.clipboard.writeText(content);
            } catch (e) {}
          }

          result = {
            status: 'success',
            action,
            message: `Executed desktop clipboard ${action} operation.`,
          };
          break;
        }

        default: {
          result = {
            status: 'error',
            message: `Unknown tool name: ${name}`,
          };
        }
      }
    } catch (err: any) {
      console.error(`[ToolManager] Error executing ${name}:`, err);
      result = {
        status: 'error',
        message: err.message || 'Execution error',
      };
    }

    if (this.callbacks.onToolExecuted) {
      this.callbacks.onToolExecuted(name, args, result);
    }

    return {
      id,
      name,
      response: {
        output: result,
      },
    };
  }
}
