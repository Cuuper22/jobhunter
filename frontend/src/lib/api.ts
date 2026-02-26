const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8081";

function getPassword(): string {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("jh_password") || "";
}

export function setPassword(pw: string) {
  localStorage.setItem("jh_password", pw);
}

export function clearPassword() {
  localStorage.removeItem("jh_password");
}

async function fetchApi(path: string, options: RequestInit = {}) {
  const password = getPassword();
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(password ? { Authorization: `Bearer ${password}` } : {}),
      ...options.headers,
    },
  });
  if (res.status === 401) {
    clearPassword();
    window.location.reload();
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${await res.text()}`);
  }
  return res.json();
}

export const api = {
  // Jobs
  getJobs: (params?: { minScore?: number; source?: string }) => {
    const qs = new URLSearchParams();
    if (params?.minScore) qs.set("min_score", String(params.minScore));
    if (params?.source) qs.set("source", params.source);
    return fetchApi(`/api/jobs/?${qs}`);
  },

  // Applications
  getApplications: (status?: string) => {
    const qs = status ? `?status=${status}` : "";
    return fetchApi(`/api/applications/${qs}`);
  },
  getPending: () => fetchApi("/api/applications/pending"),
  approveApplication: (appId: string, editedLetter?: string) =>
    fetchApi(`/api/applications/${appId}/approve`, {
      method: "POST",
      body: JSON.stringify({ edited_cover_letter: editedLetter || null }),
    }),
  rejectApplication: (appId: string, reason?: string) =>
    fetchApi(`/api/applications/${appId}/reject`, {
      method: "POST",
      body: JSON.stringify({ reason: reason || "" }),
    }),

  // Controls
  pauseQueue: () => fetchApi("/api/controls/pause", { method: "POST" }),
  resumeQueue: () => fetchApi("/api/controls/resume", { method: "POST" }),
  emergencyStop: () => fetchApi("/api/controls/emergency-stop", { method: "POST" }),

  // Scheduler
  triggerScrape: () => fetchApi("/api/scheduler/trigger", { method: "POST" }),

  // Stats
  getStats: () => fetchApi("/api/stats"),
  getLogs: (limit = 50) => fetchApi(`/api/logs?limit=${limit}`),
};
