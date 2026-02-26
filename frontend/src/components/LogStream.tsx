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
        return "text-red-400";
      case "success":
        return "text-green-400";
      case "warning":
        return "text-yellow-400";
      default:
        return "text-blue-400";
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-4 font-mono text-sm h-[32rem] overflow-y-auto">
      <h2 className="text-gray-400 text-xs uppercase tracking-wide mb-3">
        Live Activity Log
      </h2>
      {logs.map((log) => (
        <div key={log.id} className="mb-1 flex gap-2">
          <span className="text-gray-600 text-xs min-w-[5rem]">
            {new Date(log.timestamp).toLocaleTimeString()}
          </span>
          <span className={`text-xs font-bold uppercase min-w-[3.5rem] ${levelColor(log.level)}`}>
            [{log.level}]
          </span>
          <span className={levelColor(log.level)}>{log.message}</span>
          {log.screenshot_url && (
            <a
              href={log.screenshot_url}
              target="_blank"
              className="text-purple-400 hover:underline"
            >
              [screenshot]
            </a>
          )}
        </div>
      ))}
      {logs.length === 0 && (
        <p className="text-gray-600">Waiting for agent activity...</p>
      )}
    </div>
  );
}
