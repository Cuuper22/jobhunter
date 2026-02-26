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
    <div className="flex items-center gap-2">
      <span
        className={`w-2 h-2 rounded-full ${
          status === "running" ? "bg-green-400" : "bg-yellow-400"
        }`}
      />
      <span className="text-sm text-gray-400 mr-2">
        {status === "running" ? "Active" : "Paused"}
      </span>
      <button
        onClick={handleTriggerScrape}
        disabled={scraping}
        className={`px-3 py-1.5 rounded text-sm font-medium ${
          scraping
            ? "bg-blue-900 text-blue-300 cursor-wait"
            : "bg-blue-600 hover:bg-blue-500 text-white"
        }`}
      >
        {scraping ? "Scraping..." : "Scrape Now"}
      </button>
      <button
        onClick={handlePause}
        className={`px-3 py-1.5 rounded text-sm font-medium ${
          status === "running"
            ? "bg-yellow-600 hover:bg-yellow-700 text-white"
            : "bg-green-600 hover:bg-green-700 text-white"
        }`}
      >
        {status === "running" ? "Pause" : "Resume"}
      </button>
      <button
        onClick={handleEmergencyStop}
        className={`px-3 py-1.5 rounded text-sm font-medium ${
          confirming
            ? "bg-red-500 text-white animate-pulse"
            : "bg-red-800 hover:bg-red-700 text-red-200"
        }`}
      >
        {confirming ? "Click again to confirm" : "Emergency Stop"}
      </button>
    </div>
  );
}
