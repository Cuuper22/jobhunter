"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "../lib/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface Application {
  id: string;
  job_id: string;
  job_title: string;
  company: string;
  job_url: string;
  cover_letter: string;
  cover_letter_edited?: string;
  status: string;
  fit_score?: number;
  fit_reasoning?: string;
  role_summary?: string;
  company_summary?: string;
  strengths?: string[];
  gaps?: string[];
  suggestions?: string[];
  form_data?: Record<string, string>;
  screenshot_url?: string;
  outreach_subject?: string;
  outreach_email?: string;
  created_at: string;
}

interface AppCardState {
  coverLetter: string;
  formData: Record<string, string>;
  outreachSubject: string;
  outreachEmail: string;
  outreachLoading: boolean;
  outreachVisible: boolean;
  fitOpen: boolean;
  formOpen: boolean;
  saving: boolean;
  actionLoading: boolean;
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function wordCount(text: string): number {
  return text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
}

function ScoreBadge({ score }: { score?: number }) {
  if (score === undefined || score === null) {
    return (
      <div className="flex flex-col items-center gap-1">
        <div className="w-12 h-12 rounded-full bg-gray-700 flex items-center justify-center text-gray-400 text-sm font-bold">
          --
        </div>
      </div>
    );
  }

  const colorClass =
    score >= 70
      ? "bg-green-700 text-green-100 border-green-500"
      : score >= 40
      ? "bg-yellow-700 text-yellow-100 border-yellow-500"
      : "bg-red-800 text-red-100 border-red-600";

  return (
    <div className="flex flex-col items-center gap-1 min-w-[3.5rem]">
      <div
        className={`w-12 h-12 rounded-full border-2 flex items-center justify-center text-sm font-bold ${colorClass}`}
      >
        {score}
      </div>
    </div>
  );
}

function CollapsibleSection({
  title,
  open,
  onToggle,
  children,
}: {
  title: string;
  open: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="border border-gray-800 rounded-lg overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 bg-gray-850 hover:bg-gray-800 transition-colors text-left"
      >
        <span className="text-sm font-semibold text-gray-300">{title}</span>
        <span className="text-gray-500 text-xs">{open ? "▲" : "▼"}</span>
      </button>
      {open && <div className="px-4 pb-4 pt-3 bg-gray-900">{children}</div>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Single application card
// ---------------------------------------------------------------------------

function AppCard({
  app,
  onDismiss,
}: {
  app: Application;
  onDismiss: (id: string) => void;
}) {
  const [state, setState] = useState<AppCardState>({
    coverLetter: app.cover_letter_edited ?? app.cover_letter,
    formData: app.form_data ? { ...app.form_data } : {},
    outreachSubject: app.outreach_subject ?? "",
    outreachEmail: app.outreach_email ?? "",
    outreachLoading: false,
    outreachVisible: !!(app.outreach_subject || app.outreach_email),
    fitOpen: true,
    formOpen: false,
    saving: false,
    actionLoading: false,
  });

  const set = (patch: Partial<AppCardState>) =>
    setState((prev) => ({ ...prev, ...patch }));

  // -- helpers ---------------------------------------------------------------

  const buildPayload = () => ({
    cover_letter_edited: state.coverLetter,
    form_data: state.formData,
    outreach_subject: state.outreachSubject || null,
    outreach_email: state.outreachEmail || null,
  });

  const handleSave = async () => {
    set({ saving: true });
    try {
      await api.updateApplication(app.id, buildPayload());
    } catch (e) {
      console.error("Save failed:", e);
    } finally {
      set({ saving: false });
    }
  };

  const handleApprove = async () => {
    set({ actionLoading: true });
    try {
      await api.updateApplication(app.id, buildPayload());
      await api.approveApplication(app.id, state.coverLetter);
      onDismiss(app.id);
    } catch (e) {
      console.error("Approve failed:", e);
    } finally {
      set({ actionLoading: false });
    }
  };

  const handleSkip = async () => {
    set({ actionLoading: true });
    try {
      await api.rejectApplication(app.id, "Skipped by reviewer");
      onDismiss(app.id);
    } catch (e) {
      console.error("Skip failed:", e);
    } finally {
      set({ actionLoading: false });
    }
  };

  const handleGenerateOutreach = async () => {
    set({ outreachLoading: true, outreachVisible: true });
    try {
      const result = await api.generateOutreach(app.job_id);
      set({
        outreachSubject: result.subject ?? "",
        outreachEmail: result.email ?? result.body ?? "",
      });
    } catch (e) {
      console.error("Outreach generation failed:", e);
    } finally {
      set({ outreachLoading: false });
    }
  };

  const handleRescore = () => {
    console.log("[Re-score] app_id:", app.id, "job_id:", app.job_id);
  };

  const updateFormField = (key: string, value: string) => {
    set({ formData: { ...state.formData, [key]: value } });
  };

  // -- render ----------------------------------------------------------------

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-5">
      {/* ---- Header ---- */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-100 truncate">
            {app.job_title}
          </h3>
          <p className="text-gray-400 text-sm">{app.company}</p>
          <div className="flex items-center gap-3 mt-1">
            <a
              href={app.job_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 text-xs hover:underline"
            >
              View posting
            </a>
            {app.screenshot_url && (
              <a
                href={app.screenshot_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-purple-400 text-xs hover:underline"
              >
                Form screenshot
              </a>
            )}
            <span className="text-gray-600 text-xs">
              {new Date(app.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
        <div className="flex flex-col items-center gap-1 shrink-0">
          <ScoreBadge score={app.fit_score} />
          {app.fit_reasoning && (
            <p className="text-xs text-gray-500 text-center max-w-[10rem] leading-tight">
              {app.fit_reasoning}
            </p>
          )}
        </div>
      </div>

      {/* ---- Role & Company Summaries ---- */}
      {(app.role_summary || app.company_summary) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {app.role_summary && (
            <div className="bg-gray-800 rounded-lg p-3">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
                Role
              </p>
              <p className="text-sm text-gray-300 leading-relaxed">
                {app.role_summary}
              </p>
            </div>
          )}
          {app.company_summary && (
            <div className="bg-gray-800 rounded-lg p-3">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">
                Company
              </p>
              <p className="text-sm text-gray-300 leading-relaxed">
                {app.company_summary}
              </p>
            </div>
          )}
        </div>
      )}

      {/* ---- Fit Analysis (collapsible) ---- */}
      {(app.strengths?.length ||
        app.gaps?.length ||
        app.suggestions?.length) && (
        <CollapsibleSection
          title="Fit Analysis"
          open={state.fitOpen}
          onToggle={() => set({ fitOpen: !state.fitOpen })}
        >
          <div className="space-y-4">
            {app.strengths && app.strengths.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-green-400 uppercase tracking-wide mb-2">
                  Strengths
                </p>
                <ul className="space-y-1">
                  {app.strengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                      <span className="text-green-400 mt-0.5 shrink-0">✓</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {app.gaps && app.gaps.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-yellow-400 uppercase tracking-wide mb-2">
                  Gaps
                </p>
                <ul className="space-y-1">
                  {app.gaps.map((g, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                      <span className="text-yellow-400 mt-0.5 shrink-0">⚠</span>
                      <span>{g}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {app.suggestions && app.suggestions.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-blue-400 uppercase tracking-wide mb-2">
                  Suggestions
                </p>
                <ul className="space-y-1">
                  {app.suggestions.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                      <span className="text-blue-400 mt-0.5 shrink-0">💡</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}

      {/* ---- Cover Letter ---- */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-sm font-semibold text-gray-300">Cover Letter</h4>
          <span className="text-xs text-gray-500">
            {wordCount(state.coverLetter)} words
          </span>
        </div>
        <textarea
          value={state.coverLetter}
          onChange={(e) => set({ coverLetter: e.target.value })}
          rows={10}
          className="w-full bg-gray-800 text-gray-200 border border-gray-700 rounded-lg p-3 text-sm font-mono resize-y focus:outline-none focus:border-gray-500 leading-relaxed"
        />
      </div>

      {/* ---- Form Data (collapsible) ---- */}
      {Object.keys(state.formData).length > 0 && (
        <CollapsibleSection
          title={`Form Fields (${Object.keys(state.formData).length})`}
          open={state.formOpen}
          onToggle={() => set({ formOpen: !state.formOpen })}
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {Object.entries(state.formData).map(([key, value]) => (
              <div key={key}>
                <label className="block text-xs text-gray-500 mb-1 font-mono">
                  {key}
                </label>
                <input
                  type="text"
                  value={value}
                  onChange={(e) => updateFormField(key, e.target.value)}
                  className="w-full bg-gray-800 text-gray-200 border border-gray-700 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-gray-500"
                />
              </div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {/* ---- Outreach Email ---- */}
      <div className="border border-gray-800 rounded-lg overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 bg-gray-900">
          <span className="text-sm font-semibold text-gray-300">
            Outreach Email
          </span>
          <button
            type="button"
            onClick={handleGenerateOutreach}
            disabled={state.outreachLoading}
            className="text-xs bg-indigo-700 hover:bg-indigo-600 disabled:opacity-50 text-white px-3 py-1 rounded font-medium transition-colors"
          >
            {state.outreachLoading ? "Generating..." : "Draft Outreach"}
          </button>
        </div>
        {state.outreachVisible && (
          <div className="px-4 pb-4 pt-3 bg-gray-900 space-y-3">
            <div>
              <label className="block text-xs text-gray-500 mb-1">Subject</label>
              <input
                type="text"
                value={state.outreachSubject}
                onChange={(e) => set({ outreachSubject: e.target.value })}
                placeholder="Email subject line..."
                className="w-full bg-gray-800 text-gray-200 border border-gray-700 rounded px-3 py-2 text-sm focus:outline-none focus:border-gray-500"
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 mb-1">Body</label>
              <textarea
                value={state.outreachEmail}
                onChange={(e) => set({ outreachEmail: e.target.value })}
                rows={8}
                placeholder={
                  state.outreachLoading
                    ? "Generating outreach email..."
                    : "Email body will appear here..."
                }
                className="w-full bg-gray-800 text-gray-200 border border-gray-700 rounded px-3 py-2 text-sm font-mono resize-y focus:outline-none focus:border-gray-500"
              />
            </div>
          </div>
        )}
      </div>

      {/* ---- Action Buttons ---- */}
      <div className="flex flex-wrap items-center gap-3 pt-1">
        <button
          type="button"
          onClick={handleApprove}
          disabled={state.actionLoading}
          className="bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white px-5 py-2 rounded-lg font-medium text-sm transition-colors"
        >
          {state.actionLoading ? "Submitting..." : "Approve & Submit"}
        </button>
        <button
          type="button"
          onClick={handleSave}
          disabled={state.saving || state.actionLoading}
          className="bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-gray-200 px-5 py-2 rounded-lg font-medium text-sm transition-colors"
        >
          {state.saving ? "Saving..." : "Save Changes"}
        </button>
        <button
          type="button"
          onClick={handleSkip}
          disabled={state.actionLoading}
          className="bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-gray-400 px-5 py-2 rounded-lg font-medium text-sm transition-colors"
        >
          Skip
        </button>
        <button
          type="button"
          onClick={handleRescore}
          disabled={state.actionLoading}
          className="border border-orange-600 hover:bg-orange-600/10 text-orange-400 px-5 py-2 rounded-lg font-medium text-sm transition-colors"
        >
          Re-score
        </button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export default function ApplicationReview() {
  const [apps, setApps] = useState<Application[]>([]);
  const [initialLoading, setInitialLoading] = useState(true);

  const refresh = useCallback(() => {
    api
      .getPending()
      .then((data) => {
        setApps(data);
        setInitialLoading(false);
      })
      .catch((e) => {
        console.error("Failed to load pending applications:", e);
        setInitialLoading(false);
      });
  }, []);

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 15000);
    return () => clearInterval(interval);
  }, [refresh]);

  const dismiss = (id: string) => {
    setApps((prev) => prev.filter((a) => a.id !== id));
  };

  if (initialLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <p className="text-gray-500 text-sm">Loading applications...</p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-200">
          Pending Approval
          <span className="ml-2 text-sm font-normal text-gray-500">
            ({apps.length})
          </span>
        </h2>
        <button
          type="button"
          onClick={refresh}
          className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
        >
          Refresh
        </button>
      </div>

      {apps.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <p className="text-gray-500">No applications pending review.</p>
          <p className="text-gray-600 text-sm mt-1">
            The agent will surface new ones as jobs are found.
          </p>
        </div>
      ) : (
        apps.map((app) => (
          <AppCard key={app.id} app={app} onDismiss={dismiss} />
        ))
      )}
    </div>
  );
}
