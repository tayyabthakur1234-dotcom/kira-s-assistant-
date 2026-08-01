import fs from "fs";
import path from "path";

export type MemoryCategory =
  | "identity"
  | "preference"
  | "relationship"
  | "project"
  | "goal"
  | "routine"
  | "device"
  | "conversation"
  | "emotional";

export type ImportanceLevel = "Critical" | "High" | "Medium" | "Low";

export interface MemoryItem {
  id: string;
  title: string;
  category: MemoryCategory;
  value: string;
  importance: ImportanceLevel;
  confidence: number; // 0 to 100
  source: string;
  dateCreated: number;
  lastUpdated: number;
  timesReferenced: number;
  tags: string[];
  summary: string;
}

export interface BrainData {
  version: string;
  lastSync: number;
  memories: MemoryItem[];
}

const DATA_DIR = path.join(process.cwd(), "data");
const BRAIN_FILE = path.join(DATA_DIR, "kira_brain.json");

// Default seed memories to establish initial acquaintance
const DEFAULT_MEMORIES: Omit<MemoryItem, "id" | "dateCreated" | "lastUpdated" | "timesReferenced">[] = [
  {
    title: "User Name",
    category: "identity",
    value: "Tayyab",
    importance: "Critical",
    confidence: 100,
    source: "initial_setup",
    tags: ["name", "identity"],
    summary: "The user's primary name is Tayyab.",
  },
  {
    title: "Occupation",
    category: "identity",
    value: "AI Engineering Student & Developer",
    importance: "High",
    confidence: 95,
    source: "initial_setup",
    tags: ["job", "education", "ai"],
    summary: "Tayyab is studying AI engineering and building advanced web and voice AI applications.",
  },
  {
    title: "Primary Voice Assistant Project",
    category: "project",
    value: "Kira's Real-time Voice AI Assistant",
    importance: "Critical",
    confidence: 100,
    source: "conversation",
    tags: ["kira", "gemini-live", "react"],
    summary: "Tayyab is actively engineering Kira using React, Express, and Gemini 3.1 Flash Live API.",
  },
];

export class MemoryEngine {
  private brain: BrainData;

  constructor() {
    this.brain = {
      version: "1.0.0",
      lastSync: Date.now(),
      memories: [],
    };
    this.init();
  }

  private init() {
    try {
      if (!fs.existsSync(DATA_DIR)) {
        fs.mkdirSync(DATA_DIR, { recursive: true });
      }

      if (fs.existsSync(BRAIN_FILE)) {
        const fileData = fs.readFileSync(BRAIN_FILE, "utf-8");
        this.brain = JSON.parse(fileData);
      } else {
        // Seed initial memories
        const now = Date.now();
        this.brain.memories = DEFAULT_MEMORIES.map((m, index) => ({
          ...m,
          id: `mem_${now}_${index}`,
          dateCreated: now,
          lastUpdated: now,
          timesReferenced: 1,
        }));
        this.saveToFile();
      }
    } catch (err) {
      console.error("[MemoryEngine] Error initializing memory brain file:", err);
    }
  }

  private saveToFile() {
    try {
      this.brain.lastSync = Date.now();
      fs.writeFileSync(BRAIN_FILE, JSON.stringify(this.brain, null, 2), "utf-8");
    } catch (err) {
      console.error("[MemoryEngine] Error saving memory file:", err);
    }
  }

  public getAllMemories(): MemoryItem[] {
    return this.brain.memories;
  }

  public searchMemories(query?: string, category?: string): MemoryItem[] {
    let results = this.brain.memories;

    if (category) {
      const catLower = category.toLowerCase();
      results = results.filter((m) => m.category.toLowerCase() === catLower);
    }

    if (query && query.trim()) {
      const q = query.toLowerCase().trim();
      results = results.filter(
        (m) =>
          m.title.toLowerCase().includes(q) ||
          m.value.toLowerCase().includes(q) ||
          m.summary.toLowerCase().includes(q) ||
          m.tags.some((t) => t.toLowerCase().includes(q))
      );
    }

    return results;
  }

  public upsertMemory(data: {
    title: string;
    category: MemoryCategory;
    value: string;
    importance?: ImportanceLevel;
    confidence?: number;
    tags?: string[];
    summary?: string;
    source?: string;
  }): MemoryItem {
    const now = Date.now();
    const titleLower = data.title.toLowerCase().trim();

    // Check if an existing memory matches by title or category/value similarity
    const existingIndex = this.brain.memories.findIndex(
      (m) =>
        m.title.toLowerCase().trim() === titleLower ||
        (m.category === data.category && m.title.toLowerCase().includes(titleLower))
    );

    let item: MemoryItem;

    if (existingIndex >= 0) {
      // Update existing memory
      const existing = this.brain.memories[existingIndex];
      item = {
        ...existing,
        title: data.title || existing.title,
        category: data.category || existing.category,
        value: data.value,
        importance: data.importance || existing.importance,
        confidence: data.confidence ?? existing.confidence,
        lastUpdated: now,
        timesReferenced: existing.timesReferenced + 1,
        tags: Array.from(new Set([...existing.tags, ...(data.tags || [])])),
        summary: data.summary || `${data.title}: ${data.value}`,
      };
      this.brain.memories[existingIndex] = item;
    } else {
      // Create new memory item
      item = {
        id: `mem_${now}_${Math.random().toString(36).substring(2, 7)}`,
        title: data.title,
        category: data.category || "identity",
        value: data.value,
        importance: data.importance || "Medium",
        confidence: data.confidence ?? 85,
        source: data.source || "voice_interaction",
        dateCreated: now,
        lastUpdated: now,
        timesReferenced: 1,
        tags: data.tags || [data.category],
        summary: data.summary || `${data.title}: ${data.value}`,
      };
      this.brain.memories.push(item);
    }

    this.saveToFile();
    return item;
  }

  public forgetMemory(queryOrId?: string, category?: string, deleteAll: boolean = false): { deletedCount: number } {
    if (deleteAll) {
      const count = this.brain.memories.length;
      this.brain.memories = [];
      this.saveToFile();
      return { deletedCount: count };
    }

    if (!queryOrId && !category) {
      return { deletedCount: 0 };
    }

    const initialCount = this.brain.memories.length;

    this.brain.memories = this.brain.memories.filter((m) => {
      if (queryOrId) {
        if (m.id === queryOrId) return false;
        const q = queryOrId.toLowerCase();
        if (m.title.toLowerCase().includes(q) || m.value.toLowerCase().includes(q)) {
          return false;
        }
      }
      if (category && m.category.toLowerCase() === category.toLowerCase()) {
        return false;
      }
      return true;
    });

    const deletedCount = initialCount - this.brain.memories.length;
    this.saveToFile();
    return { deletedCount };
  }

  public getFormattedContextForSystemPrompt(): string {
    if (this.brain.memories.length === 0) {
      return "No prior user memories recorded yet. Ask naturally and learn about the user as you converse.";
    }

    const categoriesMap: Record<string, MemoryItem[]> = {};

    for (const mem of this.brain.memories) {
      if (!categoriesMap[mem.category]) {
        categoriesMap[mem.category] = [];
      }
      categoriesMap[mem.category].push(mem);
    }

    let output = "=== KIRA'S MEMORY BRAIN (PERSISTENT FACTS ABOUT THE USER) ===\n";
    output += "You MUST naturally incorporate these known facts about the user during conversation without repeating yourself:\n\n";

    for (const [cat, items] of Object.entries(categoriesMap)) {
      output += `[Category: ${cat.toUpperCase()}]\n`;
      for (const item of items) {
        output += `- ${item.title}: ${item.value} (Importance: ${item.importance}, Confidence: ${item.confidence}%)\n`;
      }
      output += "\n";
    }

    return output.trim();
  }
}

export const memoryEngine = new MemoryEngine();
