"use client";

import { useEffect, useState } from "react";
import { api } from "../lib/api";

interface Application {
  id: string;
  job_title: string;
  company: string;
  job_url: string;
  cover_letter: string;
  cover_letter_edited?: string;
  status: string;
  fit_score?: number;
  screenshot_url?: string;
  created_at: string;
}

export default function ApplicationReview() {
  const [apps, setApps] = useState<Application[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [editText, setEditText] = useState("");
  const [loading, setLoading] = useState<string | null>(null);

  const refresh = () => {
    api.getPending().then(setApps).catch(console.error);
  };

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (appId: string) => {
    setLoading(appId);
    try {
      const letter = editing === appId ? editText : undefined;
      await api.approveApplication(appId, letter);
      setApps((prev) => prev.filter((a) => a.id !== appId));
      setEditing(null);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(null);
    }
  };

  const handleReject = async (appId: string) => {
    setLoading(appId);
    try {
      await api.rejectApplication(appId, "Not interested");
      setApps((prev) => prev.filter((a) => a.id !== appId));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-200">
        Pending Approval ({apps.length})
      </h2>

      {apps.map((app) => (
        <div
          key={app.id}
          className="bg-gray-900 border border-gray-800 rounded-lg p-5 space-y-4"
        >
          {/* Header */}
          <div className="flex justify-between items-start">
            <div>
              <h3 className="text-lg font-semibold">{app.job_title}</h3>
              <p className="text-gray-400">{app.company}</p>
              <a
                href={app.job_url}
                target="_blank"
                rel="noopener"
                className="text-blue-400 text-sm hover:underline"
              >
                View posting
              </a>
            </div>
            <span className="text-xs text-gray-500">
              {new Date(app.created_at).toLocaleDateString()}
            </span>
          </div>

          {/* Cover Letter */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-400">Cover Letter</h4>
              <button
                onClick={() => {
                  if (editing === app.id) {
                    setEditing(null);
                  } else {
                    setEditing(app.id);
                    setEditText(app.cover_letter);
                  }
                }}
                className="text-xs text-blue-400 hover:text-blue-300"
              >
                {editing === app.id ? "Cancel Edit" : "Edit"}
              </button>
            </div>
            {editing === app.id ? (
              <textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="w-full h-48 bg-gray-800 text-gray-200 border border-gray-700 rounded p-3 text-sm font-mono resize-y"
              />
            ) : (
              <pre className="bg-gray-800 border border-gray-700 rounded p-3 text-sm text-gray-300 whitespace-pre-wrap max-h-48 overflow-y-auto">
                {app.cover_letter}
              </pre>
            )}
          </div>

          {/* Screenshot preview */}
          {app.screenshot_url && (
            <a
              href={app.screenshot_url}
              target="_blank"
              className="text-purple-400 text-sm hover:underline"
            >
              View form screenshot
            </a>
          )}

          {/* Actions */}
          <div className="flex gap-3">
            <button
              onClick={() => handleApprove(app.id)}
              disabled={loading === app.id}
              className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white px-5 py-2 rounded font-medium text-sm"
            >
              {loading === app.id ? "..." : "Approve & Submit"}
            </button>
            <button
              onClick={() => handleReject(app.id)}
              disabled={loading === app.id}
              className="bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-gray-200 px-5 py-2 rounded font-medium text-sm"
            >
              Skip
            </button>
          </div>
        </div>
      ))}

      {apps.length === 0 && (
        <p className="text-gray-500 text-center py-8">
          No applications pending review. The agent will find more jobs soon.
        </p>
      )}
    </div>
  );
}
