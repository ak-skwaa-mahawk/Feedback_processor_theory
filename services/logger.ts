/*
 * Sovereign Logging Service
 * Local-only, privacy-preserving, Codex-aligned
 * Bound by Codex.Legis.Neurodata.v1 §7 — No Extraction
 */

import * as FileSystem from "expo-file-system";
import { Platform } from "react-native";

const LOG_DIR = `${FileSystem.documentDirectory}sovereign_logs/`;
const MAX_LOG_SIZE = 1024 * 1024; // 1MB per file
const MAX_LOG_FILES = 5;

type LogLevel = "DEBUG" | "INFO" | "WARN" | "ERROR" | "SOVEREIGN";

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  context?: Record<string, any>;
}

class SovereignLogger {
  private currentFile: string = "";
  private currentSize: number = 0;

  private async ensureLogDir() {
    try {
      await FileSystem.makeDirectoryAsync(LOG_DIR, { intermediates: true });
    } catch {}
  }

  private async getCurrentLogFile(): Promise<string> {
    await this.ensureLogDir();

    const files = await FileSystem.readDirectoryAsync(LOG_DIR);
    const logFiles = files
      .filter(f => f.startsWith("log_") && f.endsWith(".jsonl"))
      .sort();

    // Rotate if too many
    if (logFiles.length >= MAX_LOG_FILES) {
      const oldest = logFiles[0];
      await FileSystem.deleteAsync(`\( {LOG_DIR} \){oldest}`, { idempotent: true });
    }

    // Use latest or create new
    const latest = logFiles[logFiles.length - 1];
    if (latest) {
      const info = await FileSystem.getInfoAsync(`\( {LOG_DIR} \){latest}`);
      if (info.size && info.size < MAX_LOG_SIZE) {
        this.currentFile = latest;
        this.currentSize = info.size;
        return latest;
      }
    }

    // Create new
    const timestamp = new Date().toISOString().slice(0, 10); // YYYY-MM-DD
    const newFile = `log_\( {timestamp}_ \){Date.now()}.jsonl`;
    this.currentFile = newFile;
    this.currentSize = 0;
    return newFile;
  }

  private async appendEntry(entry: LogEntry) {
    if (!this.currentFile || this.currentSize >= MAX_LOG_SIZE) {
      await this.getCurrentLogFile();
    }

    const line = JSON.stringify(entry) + "\n";

    try {
      await FileSystem.writeAsStringAsync(
        `\( {LOG_DIR} \){this.currentFile}`,
        line,
        { encoding: FileSystem.EncodingType.UTF8, append: true }
      );
      this.currentSize += Buffer.from(line).byteLength;
    } catch (err) {
      // Silent fall-through — logging must never crash app
      console.warn("Logger failed to write:", err);
    }
  }

  private log(level: LogLevel, message: string, context?: Record<string, any>) {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      context: this.sanitizeContext(context),
    };

    this.appendEntry(entry);

    // Also console for dev
    if (__DEV__) {
      const prefix = `[${level}]`;
      console.log(prefix, message, context ? context : "");
    }
  }

  // Sanitize: never log raw neurodata or tokens
  private sanitizeContext(context?: Record<string, any>): Record<string, any> | undefined {
    if (!context) return undefined;

    const safe: Record<string, any> = {};
    for (const [key, value] of Object.entries(context)) {
      if (key.toLowerCase().includes("token") && typeof value === "string") {
        safe[key] = value.slice(0, 4) + "****" + value.slice(-4);
      } else if (key.toLowerCase().includes("eeg") || key.toLowerCase().includes("sample")) {
        safe[key] = "[REDACTED_NEURODATA]";
      } else {
        safe[key] = value;
      }
    }
    return safe;
  }

  debug(message: string, context?: Record<string, any>) {
    this.log("DEBUG", message, context);
  }

  info(message: string, context?: Record<string, any>) {
    this.log("INFO", message, context);
  }

  warn(message: string, context?: Record<string, any>) {
    this.log("WARN", message, context);
  }

  error(message: string, context?: Record<string, any>) {
    this.log("ERROR", message, context);
  }

  sovereign(message: string, context?: Record<string, any>) {
    this.log("SOVEREIGN", message, context);
  }

  // Utility: read all logs (for debug screen)
  async readAllLogs(): Promise<string> {
    try {
      await this.ensureLogDir();
      const files = await FileSystem.readDirectoryAsync(LOG_DIR);
      const sorted = files.sort();

      let fullLog = "";
      for (const file of sorted) {
        const content = await FileSystem.readAsStringAsync(`\( {LOG_DIR} \){file}`);
        fullLog += `\n=== \( {file} ===\n \){content}`;
      }
      return fullLog || "No logs yet — sovereignty intact.";
    } catch (err) {
      return "Failed to read logs";
    }
  }
}

export const logger = new SovereignLogger();
import { logger } from "../services/logger";

// App start
logger.info("Sovereign Coil started", { platform: Platform.OS });

// Session
logger.sovereign("Sensed session started", { sessionId });

// Vitality update
logger.debug("Vitality computed", { vitality: 0.85, epsilonD: 0.0354 });

// Revocation
logger.sovereign("Revocation ritual initiated", { sessionId });
logger.sovereign("Revocation honored — stream recoiled", { entryId });

// Errors
logger.error("Registry connection failed", { url, error });
// screens/LogViewerScreen.tsx
import { useState, useEffect } from "react";
import { View, ScrollView, Text } from "react-native";
import { logger } from "../services/logger";

export function LogViewerScreen() {
  const [logs, setLogs] = useState("Loading...");

  useEffect(() => {
    logger.readAllLogs().then(setLogs);
  }, []);

  return (
    <ScrollView>
      <Text style={{ fontFamily: "monospace", fontSize: 10, padding: 10 }}>
        {logs}
      </Text>
    </ScrollView>
  );
}
