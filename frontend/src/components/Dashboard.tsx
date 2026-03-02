"use client";

import { useEffect, useState } from "react";
import { api, clearPassword } from "../lib/api";
import LogStream from "./LogStream";
import Controls from "./Controls";
import ApplicationReview from "./ApplicationReview";

interface Stats {
  total_jobs_scraped: number;
  total_applications: number;
  pending_approval: number;
  submitted: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [activeTab, setActiveTab] = useState<"review" | "jobs" | "logs">("review");

  useEffect(() => {
    api.getStats().then(setStats).catch(console.error);
    const interval = setInterval(() => {
      api.getStats().then(setStats).catch(console.error);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { key: "review" as const, label: "Review" },
    { key: "jobs" as const, label: "Jobs" },
    { key: "logs" as const, label: "Logs" },
  ];

  return (
    <div className="min-h-screen bg-surface-primary text-ink-body">
      {/* Header */}
      <header className="bg-surface-secondary border-b border-edge px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-semibold text-ink-heading tracking-heading">
              jobhunter
            </h1>
            <button
              onClick={() => { clearPassword(); window.location.reload(); }}
              className="text-[11px] text-ink-faint hover:text-ink-muted transition-colors duration-200"
            >
              logout
            </button>
          </div>
          <Controls />
        </div>
      </header>

      {/* Stats Bar */}
      {stats && (
        <div className="bg-surface-secondary/60 border-b border-edge">
          <div className="max-w-7xl mx-auto px-6 py-3 flex gap-10">
            <Stat label="Scraped" value={stats.total_jobs_scraped} />
            <Stat label="Applications" value={stats.total_applications} />
            <Stat
              label="Pending"
              value={stats.pending_approval}
              highlight={stats.pending_approval > 0}
            />
            <Stat label="Submitted" value={stats.submitted} accent />
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-6 pt-4">
        <div className="flex gap-0 border-b border-edge">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`px-4 py-2.5 text-[13px] font-medium transition-colors duration-200 ${
                activeTab === tab.key
                  ? "text-accent-primary border-b-2 border-accent-primary"
                  : "text-ink-muted hover:text-ink-body"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-6">
        {activeTab === "review" && <ApplicationReview />}
        {activeTab === "jobs" && <JobList />}
        {activeTab === "logs" && <LogStream />}
      </main>
    </div>
  );
}

function Stat({
  label,
  value,
  highlight = false,
  accent = false,
}: {
  label: string;
  value: number;
  highlight?: boolean;
  accent?: boolean;
}) {
  return (
    <div>
      <div className="text-[10px] text-ink-faint uppercase tracking-widest font-medium">
        {label}
      </div>
      <div
        className={`text-lg font-semibold tracking-heading tabular-nums ${
          accent
            ? "text-accent-secondary"
            : highlight
            ? "text-signal-warning"
            : "text-ink-heading"
        }`}
      >
        {value.toLocaleString()}
      </div>
    </div>
  );
}

function JobList() {
  const [jobs, setJobs] = useState<any[]>([]);

  useEffect(() => {
    api.getJobs({ minScore: 0 }).then(setJobs).catch(console.error);
  }, []);

  return (
    <div className="space-y-2">
      {jobs.map((job) => (
        <div
          key={job.id}
          className="bg-surface-secondary border border-edge rounded-lg p-4 flex justify-between items-start hover:border-edge-strong transition-colors duration-200"
        >
          <div>
            <h3 className="font-medium text-ink-heading text-[15px]">{job.title}</h3>
            <p className="text-ink-muted text-[13px] mt-0.5">
              {job.company} &middot; {job.location}
            </p>
            {job.salary_min && (
              <p className="text-accent-secondary text-[13px] mt-1 font-medium tabular-nums">
                ${job.salary_min.toLocaleString()} – ${job.salary_max?.toLocaleString()}
              </p>
            )}
          </div>
          <div className="text-right flex flex-col items-end gap-1">
            {job.fit_score != null && (
              <ScoreInline score={job.fit_score} />
            )}
            <div className="text-[11px] text-ink-faint">{job.source}</div>
          </div>
        </div>
      ))}
      {jobs.length === 0 && (
        <p className="text-ink-muted text-center py-12 text-sm">No jobs scraped yet</p>
      )}
    </div>
  );
}

function ScoreInline({ score }: { score: number }) {
  const color =
    score >= 70
      ? "text-signal-success"
      : score >= 40
      ? "text-signal-warning"
      : "text-signal-error";

  return (
    <span className={`text-lg font-semibold tabular-nums ${color}`}>
      {score}
    </span>
  );
}
