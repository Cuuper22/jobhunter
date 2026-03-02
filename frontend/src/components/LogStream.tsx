"use client";

import { useEffect, useState } from "react";
import { api } from "../lib/api";

interface LogEntry {
  id: string;
  timestamp: string;
  level: string;
  message: string;
  job_id?: string;
  application_id?: string;
  screenshot_url?: string;
}

export default function LogStream() {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    const fetchLogs = () => {
      api.getLogs(100).then(setLogs).catch(console.error);
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const levelColor = (level: string) => {
    switch (level) {
      case "error":
        return "text-signal-error";
      case "success":
        return "text-signal-success";
      case "warning":
        return "text-signal-warning";
      default:
        return "text-signal-info";
    }
  };

  return (
    <div className="bg-surface-secondary border border-edge rounded-lg p-4 font-mono text-sm h-[32rem] overflow-y-auto">
      <h2 className="text-ink-faint text-[10px] uppercase tracking-widest font-medium mb-3">
        Live Activity Log
      </h2>
      {logs.map((log) => (
        <div key={log.id} className="mb-1 flex gap-2">
          <span className="text-ink-faint text-[11px] min-w-[5rem] tabular-nums">
            {new Date(log.timestamp).toLocaleTimeString()}
          </span>
          <span className={`text-[11px] font-bold uppercase min-w-[3.5rem] ${levelColor(log.level)}`}>
            [{log.level}]
          </span>
          <span className={`text-[12px] ${levelColor(log.level)}`}>{log.message}</span>
          {log.screenshot_url && (
            <a
              href={log.screenshot_url}
              target="_blank"
              className="text-accent-secondary text-[11px] hover:underline"
            >
              [screenshot]
            </a>
          )}
        </div>
      ))}
      {logs.length === 0 && (
        <p className="text-ink-faint text-[13px]">Waiting for agent activity...</p>
      )}
    </div>
  );
}
