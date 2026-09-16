"use client";
import { useState } from "react";
import AppNav from "@/components/AppNav";

const cadences = [
  { label: "Instantly", desc: "The moment a strong match appears" },
  { label: "Daily", desc: "One summary each day" },
  { label: "Weekly", desc: "One summary each week" },
];

export default function Settings() {
  const [cadence, setCadence] = useState("Daily");

  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="" />
      <div className="mx-auto max-w-[640px] px-6 py-12">
        <h1 className="text-[28px] font-bold text-primary-navy">Settings</h1>
        <div className="mt-6 rounded-2xl border border-neutral-border bg-white p-8">
          <h2 className="text-base font-bold text-primary-navy">Notifications</h2>
          <p className="mt-4 mb-3 text-[13px] font-bold text-neutral-ink">
            How often do you want to hear from us?
          </p>
          <div className="flex flex-col gap-2">
            {cadences.map((c) => (
              <button
                key={c.label}
                onClick={() => setCadence(c.label)}
                className={`flex items-center gap-3 rounded-lg px-4 py-3 text-left ${
                  cadence === c.label ? "bg-neutral-mist" : "border border-neutral-border"
                }`}
              >
                <span
                  className={`h-3.5 w-3.5 rounded-full border ${
                    cadence === c.label ? "border-primary-navy bg-primary-navy" : "border-neutral-border"
                  }`}
                />
                <span>
                  <span className="block text-[13px] font-bold text-neutral-ink">{c.label}</span>
                  <span className="block text-xs text-neutral-slate">{c.desc}</span>
                </span>
              </button>
            ))}
          </div>

          <div className="my-6 h-px w-full bg-neutral-border" />

          <h2 className="text-base font-bold text-primary-navy">Account</h2>
          <p className="mt-3 text-[13px] text-neutral-slate">you@example.com</p>
          <div className="mt-4 flex items-center gap-4">
            <button className="rounded-lg border border-neutral-border px-5 py-2.5 text-[13px] font-bold text-neutral-ink hover:border-primary-navy transition-colors">
              Log out
            </button>
          </div>
          
          <div className="my-6 h-px w-full bg-neutral-border" />
          
          <h2 className="text-base font-bold text-danger-red">Danger Zone</h2>
          <p className="mt-2 text-sm text-neutral-slate">Once you delete your account, there is no going back. Please be certain.</p>
          <button className="mt-4 rounded-lg border border-danger-red text-danger-red px-5 py-2.5 text-[13px] font-bold hover:bg-danger-red hover:text-white transition-colors cursor-pointer">
            Delete Account
          </button>
        </div>
      </div>
    </div>
  );
}
