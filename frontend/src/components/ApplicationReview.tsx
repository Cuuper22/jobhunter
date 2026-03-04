"use client";

import { useEffect, useState, useCallback, memo } from "react";
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
        <div className="w-12 h-12 rounded-full bg-surface-elevated flex items-center justify-center text-ink-faint text-sm font-bold">
          --
        </div>
      </div>
    );
  }

  const colorClass =
    score >= 70
      ? "bg-signal-success/15 text-signal-success border-signal-success/40"
      : score >= 40
      ? "bg-signal-warning/15 text-signal-warning border-signal-warning/40"
      : "bg-signal-error/15 text-signal-error border-signal-error/40";

  return (
    <div className="flex flex-col items-center gap-1 min-w-[3.5rem]">
      <div
        className={`w-12 h-12 rounded-full border flex items-center justify-center text-sm font-bold tabular-nums ${colorClass}`}
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
    <div className="border border-edge rounded-lg overflow-hidden">
      <button
        type="button"
        onClick={onToggle}
        className="w-full flex items-center justify-between px-4 py-3 bg-surface-secondary hover:bg-surface-elevated transition-colors duration-150 text-left"
      >
        <span className="text-[13px] font-semibold text-ink-muted">{title}</span>
        <span className="text-ink-faint text-xs">{open ? "▲" : "▼"}</span>
      </button>
      {open && <div className="px-4 pb-4 pt-3 bg-surface-primary">{children}</div>}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Single application card
// ---------------------------------------------------------------------------

// ⚡ Bolt: Wrapped AppCard in React.memo to prevent unnecessary re-renders
// when the parent ApplicationReview component auto-refreshes every 15s.
// Expected Impact: Reduces re-renders of expensive form components significantly.
const AppCard = memo(function AppCard({
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

  return (
    <div className="bg-surface-secondary border border-edge rounded-lg p-5 space-y-5 hover:border-edge-strong transition-colors duration-150">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-[15px] font-semibold text-ink-heading truncate tracking-heading">
            {app.job_title}
          </h3>
          <p className="text-ink-muted text-[13px] mt-0.5">{app.company}</p>
          <div className="flex items-center gap-3 mt-1.5">
            <a
              href={app.job_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-accent-primary text-[12px] hover:underline"
            >
              View posting
            </a>
            {app.screenshot_url && (
              <a
                href={app.screenshot_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-accent-secondary text-[12px] hover:underline"
              >
                Form screenshot
              </a>
            )}
            <span className="text-ink-faint text-[11px]">
              {new Date(app.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
        <div className="flex flex-col items-center gap-1 shrink-0">
          <ScoreBadge score={app.fit_score} />
          {app.fit_reasoning && (
            <p className="text-[11px] text-ink-faint text-center max-w-[10rem] leading-tight">
              {app.fit_reasoning}
            </p>
          )}
        </div>
      </div>

      {/* Role & Company Summaries */}
      {(app.role_summary || app.company_summary) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {app.role_summary && (
            <div className="bg-surface-elevated/50 rounded-md p-3">
              <p className="text-[10px] font-medium text-ink-faint uppercase tracking-widest mb-1">
                Role
              </p>
              <p className="text-[13px] text-ink-body leading-relaxed">
                {app.role_summary}
              </p>
            </div>
          )}
          {app.company_summary && (
            <div className="bg-surface-elevated/50 rounded-md p-3">
              <p className="text-[10px] font-medium text-ink-faint uppercase tracking-widest mb-1">
                Company
              </p>
              <p className="text-[13px] text-ink-body leading-relaxed">
                {app.company_summary}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Fit Analysis */}
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
                <p className="text-[10px] font-medium text-signal-success uppercase tracking-widest mb-2">
                  Strengths
                </p>
                <ul className="space-y-1">
                  {app.strengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-[13px] text-ink-body">
                      <span className="text-signal-success mt-0.5 shrink-0">✓</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {app.gaps && app.gaps.length > 0 && (
              <div>
                <p className="text-[10px] font-medium text-signal-warning uppercase tracking-widest mb-2">
                  Gaps
                </p>
                <ul className="space-y-1">
                  {app.gaps.map((g, i) => (
                    <li key={i} className="flex items-start gap-2 text-[13px] text-ink-body">
                      <span className="text-signal-warning mt-0.5 shrink-0">⚠</span>
                      <span>{g}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            {app.suggestions && app.suggestions.length > 0 && (
              <div>
                <p className="text-[10px] font-medium text-accent-primary uppercase tracking-widest mb-2">
                  Suggestions
                </p>
                <ul className="space-y-1">
                  {app.suggestions.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-[13px] text-ink-body">
                      <span className="text-accent-primary mt-0.5 shrink-0">→</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </CollapsibleSection>
      )}

      {/* Cover Letter */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-[13px] font-semibold text-ink-muted">Cover Letter</h4>
          <span className="text-[11px] text-ink-faint tabular-nums">
            {wordCount(state.coverLetter)} words
          </span>
        </div>
        <textarea
          value={state.coverLetter}
          onChange={(e) => set({ coverLetter: e.target.value })}
          rows={10}
          className="w-full bg-surface-primary text-ink-body border border-edge rounded-md p-3 text-[13px] font-mono resize-y focus:outline-none focus:border-edge-strong leading-relaxed transition-colors duration-150"
        />
      </div>

      {/* Form Data */}
      {Object.keys(state.formData).length > 0 && (
        <CollapsibleSection
          title={`Form Fields (${Object.keys(state.formData).length})`}
          open={state.formOpen}
          onToggle={() => set({ formOpen: !state.formOpen })}
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {Object.entries(state.formData).map(([key, value]) => (
              <div key={key}>
                <label className="block text-[11px] text-ink-faint mb-1 font-mono">
                  {key}
                </label>
                <input
                  type="text"
                  value={value}
                  onChange={(e) => updateFormField(key, e.target.value)}
                  className="w-full bg-surface-primary text-ink-body border border-edge rounded-md px-3 py-1.5 text-[13px] focus:outline-none focus:border-edge-strong transition-colors duration-150"
                />
              </div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {/* Outreach Email */}
      <div className="border border-edge rounded-lg overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 bg-surface-secondary">
          <span className="text-[13px] font-semibold text-ink-muted">
            Outreach Email
          </span>
          <button
            type="button"
            onClick={handleGenerateOutreach}
            disabled={state.outreachLoading}
            className="text-[12px] bg-accent-primary/15 hover:bg-accent-primary/25 disabled:opacity-50 text-accent-primary px-3 py-1 rounded-md font-medium transition-colors duration-150"
          >
            {state.outreachLoading ? "Generating..." : "Draft Outreach"}
          </button>
        </div>
        {state.outreachVisible && (
          <div className="px-4 pb-4 pt-3 bg-surface-primary space-y-3">
            <div>
              <label className="block text-[11px] text-ink-faint mb-1">Subject</label>
              <input
                type="text"
                value={state.outreachSubject}
                onChange={(e) => set({ outreachSubject: e.target.value })}
                placeholder="Email subject line..."
                className="w-full bg-surface-secondary text-ink-body border border-edge rounded-md px-3 py-2 text-[13px] focus:outline-none focus:border-edge-strong placeholder:text-ink-faint transition-colors duration-150"
              />
            </div>
            <div>
              <label className="block text-[11px] text-ink-faint mb-1">Body</label>
              <textarea
                value={state.outreachEmail}
                onChange={(e) => set({ outreachEmail: e.target.value })}
                rows={8}
                placeholder={
                  state.outreachLoading
                    ? "Generating outreach email..."
                    : "Email body will appear here..."
                }
                className="w-full bg-surface-secondary text-ink-body border border-edge rounded-md px-3 py-2 text-[13px] font-mono resize-y focus:outline-none focus:border-edge-strong placeholder:text-ink-faint transition-colors duration-150"
              />
            </div>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center gap-3 pt-1">
        <button
          type="button"
          onClick={handleApprove}
          disabled={state.actionLoading}
          className="bg-signal-success/15 hover:bg-signal-success/25 border border-signal-success/30 disabled:opacity-50 text-signal-success px-5 py-2 rounded-md font-medium text-[13px] transition-colors duration-150"
        >
          {state.actionLoading ? "Submitting..." : "Approve & Submit"}
        </button>
        <button
          type="button"
          onClick={handleSave}
          disabled={state.saving || state.actionLoading}
          className="bg-surface-elevated hover:bg-surface-elevated/80 border border-edge disabled:opacity-50 text-ink-body px-5 py-2 rounded-md font-medium text-[13px] transition-colors duration-150"
        >
          {state.saving ? "Saving..." : "Save Changes"}
        </button>
        <button
          type="button"
          onClick={handleSkip}
          disabled={state.actionLoading}
          className="bg-surface-primary hover:bg-surface-secondary border border-edge disabled:opacity-50 text-ink-muted px-5 py-2 rounded-md font-medium text-[13px] transition-colors duration-150"
        >
          Skip
        </button>
        <button
          type="button"
          onClick={handleRescore}
          disabled={state.actionLoading}
          className="border border-signal-warning/30 hover:bg-signal-warning/10 text-signal-warning px-5 py-2 rounded-md font-medium text-[13px] transition-colors duration-150"
        >
          Re-score
        </button>
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  // ⚡ Bolt: Custom equality check to prevent re-renders when API polling returns new object references
  // Only re-render if the core data we display/edit has actually changed.
  return (
    prevProps.app.id === nextProps.app.id &&
    prevProps.app.status === nextProps.app.status &&
    prevProps.app.cover_letter === nextProps.app.cover_letter &&
    prevProps.app.cover_letter_edited === nextProps.app.cover_letter_edited
  );
});

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

  // ⚡ Bolt: Wrapped dismiss in useCallback to preserve its function reference.
  // This prevents breaking the React.memo optimization on AppCard during re-renders.
  const dismiss = useCallback((id: string) => {
    setApps((prev) => prev.filter((a) => a.id !== id));
  }, []);

  if (initialLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <p className="text-ink-muted text-sm">Loading applications...</p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-[15px] font-semibold text-ink-heading tracking-heading">
          Pending Approval
          <span className="ml-2 text-[13px] font-normal text-ink-faint tabular-nums">
            ({apps.length})
          </span>
        </h2>
        <button
          type="button"
          onClick={refresh}
          className="text-[12px] text-ink-faint hover:text-ink-muted transition-colors duration-150"
        >
          Refresh
        </button>
      </div>

      {apps.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <p className="text-ink-muted text-[14px]">No applications pending review.</p>
          <p className="text-ink-faint text-[13px] mt-1">
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
