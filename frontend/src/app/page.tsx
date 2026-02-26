"use client";

import { useState, useEffect } from "react";
import Dashboard from "../components/Dashboard";
import { setPassword, clearPassword } from "../lib/api";

export default function Home() {
  const [authed, setAuthed] = useState(false);
  const [pw, setPw] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    // Check if password already stored
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
      // Health endpoint may not require auth — try stats instead
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
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <form
        onSubmit={handleLogin}
        className="bg-gray-900 border border-gray-800 rounded-xl p-8 w-full max-w-sm"
      >
        <h1 className="text-2xl font-bold text-white mb-6 text-center">
          JobHunter AI
        </h1>
        <input
          type="password"
          value={pw}
          onChange={(e) => setPw(e.target.value)}
          placeholder="Enter password"
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 mb-4"
          autoFocus
        />
        {error && (
          <p className="text-red-400 text-sm mb-4">{error}</p>
        )}
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-lg transition"
        >
          Sign In
        </button>
      </form>
    </div>
  );
}
