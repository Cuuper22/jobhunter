"use client";

import { useState, useEffect } from "react";
import Dashboard from "../components/Dashboard";
import { setPassword, clearPassword } from "../lib/api";

export default function Home() {
  const [authed, setAuthed] = useState(false);
  const [pw, setPw] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const saved = localStorage.getItem("jh_password");
    if (saved) setAuthed(true);
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setPassword(pw);
    try {
      const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8081";
      const res = await fetch(`${API_BASE}/health`, {
        headers: { Authorization: `Bearer ${pw}` },
      });
      if (res.ok) {
        setAuthed(true);
      } else {
        clearPassword();
        setError("Invalid password");
      }
    } catch {
      try {
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8081";
        const res = await fetch(`${API_BASE}/api/stats`, {
          headers: { Authorization: `Bearer ${pw}` },
        });
        if (res.ok) {
          setAuthed(true);
        } else {
          clearPassword();
          setError("Invalid password or API unreachable");
        }
      } catch {
        clearPassword();
        setError("Cannot reach API server");
      }
    }
  };

  if (authed) return <Dashboard />;

  return (
    <div className="min-h-screen bg-surface-primary flex items-center justify-center">
      <form
        onSubmit={handleLogin}
        className="bg-surface-secondary border border-edge rounded-lg p-8 w-full max-w-sm shadow-md"
      >
        <h1 className="text-xl font-semibold text-ink-heading tracking-heading mb-6 text-center">
          jobhunter
        </h1>
        <input
          type="password"
          value={pw}
          onChange={(e) => setPw(e.target.value)}
          placeholder="Enter password"
          className="w-full bg-surface-primary border border-edge rounded-md px-4 py-3 text-ink-body placeholder:text-ink-faint focus:outline-none focus:border-edge-strong mb-4 text-[14px] transition-colors duration-150"
          autoFocus
        />
        {error && (
          <p className="text-signal-error text-[13px] mb-4">{error}</p>
        )}
        <button
          type="submit"
          className="w-full bg-accent-primary/15 hover:bg-accent-primary/25 border border-accent-primary/30 text-accent-primary font-medium py-3 rounded-md text-[14px] transition-colors duration-150"
        >
          Sign In
        </button>
      </form>
    </div>
  );
}
