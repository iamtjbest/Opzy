"use client";

import { useState } from "react";
import AppNav from "@/components/AppNav";
import Link from "next/link";
import { opportunities } from "@/lib/opportunities";
import DismissModal from "@/components/DismissModal";

const filters = ["All", "Jobs", "Internships", "Scholarships", "Fellowships", "Grants", "Hackathons"];

export default function Feed() {
  const [activeFilter, setActiveFilter] = useState("All");
  const [savedItems, setSavedItems] = useState<Set<string>>(new Set());
  const [dismissedItems, setDismissedItems] = useState<Set<string>>(new Set());
  
  const [dismissModalOpen, setDismissModalOpen] = useState(false);
  const [itemToDismiss, setItemToDismiss] = useState<string | null>(null);

  const toggleSave = (id: string) => {
    setSavedItems(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const initiateDismiss = (id: string) => {
    setItemToDismiss(id);
    setDismissModalOpen(true);
  };

  const handleDismiss = (reason: string) => {
    if (itemToDismiss) {
      setDismissedItems(prev => {
        const next = new Set(prev);
        next.add(itemToDismiss);
        return next;
      });
      console.log(`Dismissed ${itemToDismiss} because: ${reason}`);
    }
    setDismissModalOpen(false);
    setItemToDismiss(null);
  };

  const visibleOpportunities = opportunities
    .filter(o => !dismissedItems.has(o.id))
    .filter(o => {
      if (activeFilter === "All") return true;
      // Mock filtering based on title
      return o.title.toLowerCase().includes(activeFilter.toLowerCase().slice(0, -1));
    });
  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Feed" />
      <DismissModal 
        isOpen={dismissModalOpen} 
        onClose={() => setDismissModalOpen(false)} 
        onDismiss={handleDismiss} 
      />
      <div className="mx-auto max-w-[1140px] px-6 py-12">
        <h1 className="text-[28px] font-bold text-primary-navy">Your matches</h1>
        <p className="mt-1 text-sm text-neutral-slate">
          {visibleOpportunities.length} opportunities found for you, updated today.
        </p>

        <div className="mt-6 flex flex-wrap gap-2.5">
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setActiveFilter(f)}
              className={`rounded-full px-4 py-2 text-[13px] transition-colors cursor-pointer ${
                activeFilter === f ? "bg-primary-navy text-white border border-primary-navy" : "border border-neutral-border bg-white text-neutral-ink hover:border-primary-navy"
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        <div className="mt-6 flex flex-col gap-4">
          {visibleOpportunities.map((o) => (
            <div key={o.id} className="rounded-2xl border border-neutral-border bg-white p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="rounded-lg bg-success-emerald px-3 py-1.5 text-xs font-bold text-white">
                    {o.score}% match
                  </span>
                  <h2 className="text-lg font-bold text-primary-navy">{o.title}</h2>
                </div>
                <button 
                  onClick={() => toggleSave(o.id)}
                  className={`rounded-lg border px-4 py-2 text-xs font-bold transition-colors cursor-pointer ${
                    savedItems.has(o.id) 
                      ? "border-primary-navy bg-primary-navy text-white" 
                      : "border-neutral-border text-neutral-ink hover:border-primary-navy"
                  }`}
                >
                  {savedItems.has(o.id) ? "Saved" : "Save"}
                </button>
              </div>
              <p className="mt-2 text-[13px] text-neutral-slate">
                {o.org} &middot; Deadline: {o.deadline}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {o.reasons.map((r) => (
                  <span key={r} className="rounded-full bg-neutral-mist px-3 py-1.5 text-xs text-neutral-ink">
                    {r}
                  </span>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-between">
                <button 
                  onClick={() => initiateDismiss(o.id)}
                  className="text-[13px] text-neutral-slate hover:text-primary-navy transition-colors cursor-pointer"
                >
                  Dismiss
                </button>
                <Link href={`/opportunities/${o.id}`} className="text-[13px] font-bold text-primary-blue">
                  View details →
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
