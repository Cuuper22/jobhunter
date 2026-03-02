"use client";

import { useState } from "react";
import { api } from "../lib/api";

export default function Controls() {
  const [status, setStatus] = useState<"running" | "paused">("running");
  const [confirming, setConfirming] = useState(false);
  const [scraping, setScraping] = useState(false);

  const handlePause = async () => {
    if (status === "running") {
      await api.pauseQueue();
      setStatus("paused");
    } else {
      await api.resumeQueue();
      setStatus("running");
    }
  };

  const handleEmergencyStop = async () => {
    if (!confirming) {
      setConfirming(true);
      setTimeout(() => setConfirming(false), 3000);
      return;
    }
    await api.emergencyStop();
    setStatus("paused");
    setConfirming(false);
  };

  const handleTriggerScrape = async () => {
    setScraping(true);
    try {
      await api.triggerScrape();
    } catch (e) {
      console.error("Scrape trigger failed:", e);
    } finally {
      setScraping(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <div className="flex items-center gap-1.5 mr-1">
        <span
          className={`w-1.5 h-1.5 rounded-full ${
            status === "running" ? "bg-signal-success" : "bg-signal-warning"
          }`}
        />
        <span className="text-[11px] text-ink-muted font-medium">
          {status === "running" ? "Active" : "Paused"}
        </span>
      </div>
      <button
        onClick={handleTriggerScrape}
        disabled={scraping}
        className={`px-3 py-1.5 rounded-md text-[12px] font-medium border transition-colors duration-200 ${
          scraping
            ? "border-edge text-ink-faint cursor-wait"
            : "border-accent-primary/30 text-accent-primary hover:bg-accent-primary/10"
        }`}
      >
        {scraping ? "Scraping..." : "Scrape Now"}
      </button>
      <button
        onClick={handlePause}
        className={`px-3 py-1.5 rounded-md text-[12px] font-medium border transition-colors duration-200 ${
          status === "running"
            ? "border-signal-warning/30 text-signal-warning hover:bg-signal-warning/10"
            : "border-signal-success/30 text-signal-success hover:bg-signal-success/10"
        }`}
      >
        {status === "running" ? "Pause" : "Resume"}
      </button>
      <button
        onClick={handleEmergencyStop}
        className={`px-3 py-1.5 rounded-md text-[12px] font-medium border transition-colors duration-200 ${
          confirming
            ? "border-signal-error bg-signal-error/20 text-signal-error animate-pulse"
            : "border-signal-error/20 text-signal-error/70 hover:bg-signal-error/10 hover:text-signal-error"
        }`}
      >
        {confirming ? "Confirm Stop" : "Emergency Stop"}
      </button>
    </div>
  );
}
