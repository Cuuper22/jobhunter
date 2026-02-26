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

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl font-bold">JobHunter AI</h1>
            <button
              onClick={() => { clearPassword(); window.location.reload(); }}
              className="text-xs text-gray-500 hover:text-gray-300"
            >
              Logout
            </button>
          </div>
          <Controls />
        </div>
      </header>

      {/* Stats Bar */}
      {stats && (
        <div className="bg-gray-900/50 border-b border-gray-800">
          <div className="max-w-7xl mx-auto px-6 py-3 flex gap-8">
            <Stat label="Jobs Scraped" value={stats.total_jobs_scraped} />
            <Stat label="Applications" value={stats.total_applications} />
            <Stat
              label="Pending Review"
              value={stats.pending_approval}
              highlight={stats.pending_approval > 0}
            />
            <Stat label="Submitted" value={stats.submitted} color="text-green-400" />
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-6 pt-4">
        <div className="flex gap-1 border-b border-gray-800">
          {(["review", "jobs", "logs"] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-4 py-2 text-sm font-medium capitalize ${
                activeTab === tab
                  ? "text-blue-400 border-b-2 border-blue-400"
                  : "text-gray-400 hover:text-gray-200"
              }`}
            >
              {tab === "review" ? "Review Applications" : tab}
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
  color = "",
}: {
  label: string;
  value: number;
  highlight?: boolean;
  color?: string;
}) {
  return (
    <div>
      <div className="text-xs text-gray-500 uppercase tracking-wide">{label}</div>
      <div
        className={`text-xl font-bold ${
          color || (highlight ? "text-yellow-400" : "text-white")
        }`}
      >
        {value}
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
    <div className="space-y-3">
      {jobs.map((job) => (
        <div
          key={job.id}
          className="bg-gray-900 border border-gray-800 rounded-lg p-4 flex justify-between items-start"
        >
          <div>
            <h3 className="font-semibold">{job.title}</h3>
            <p className="text-gray-400 text-sm">
              {job.company} &middot; {job.location}
            </p>
            {job.salary_min && (
              <p className="text-green-400 text-sm">
                ${job.salary_min.toLocaleString()} - ${job.salary_max?.toLocaleString()}
              </p>
            )}
          </div>
          <div className="text-right">
            {job.fit_score != null && (
              <span
                className={`text-lg font-bold ${
                  job.fit_score >= 70
                    ? "text-green-400"
                    : job.fit_score >= 40
                    ? "text-yellow-400"
                    : "text-red-400"
                }`}
              >
                {job.fit_score}%
              </span>
            )}
            <div className="text-xs text-gray-500 mt-1">{job.source}</div>
          </div>
        </div>
      ))}
      {jobs.length === 0 && (
        <p className="text-gray-500 text-center py-8">No jobs scraped yet</p>
      )}
    </div>
  );
}
