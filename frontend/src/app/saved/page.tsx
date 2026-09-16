import AppNav from "@/components/AppNav";
import { opportunities } from "@/lib/opportunities";

export default function Saved() {
  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Saved" />
      <div className="mx-auto max-w-[1140px] px-6 py-12">
        <h1 className="text-[28px] font-bold text-primary-navy">Saved & applications</h1>
        <div className="mt-6 flex gap-8 border-b border-neutral-border">
          <span className="border-b-2 border-primary-navy pb-3 text-sm font-bold text-primary-navy">
            Saved ({opportunities.length})
          </span>
          <span className="pb-3 text-sm text-neutral-slate">Applications (2)</span>
        </div>

        <div className="mt-6 flex flex-col gap-4">
          {opportunities.map((o) => (
            <div key={o.id} className="flex items-center justify-between rounded-xl border border-neutral-border bg-white p-5">
              <div className="flex items-center gap-4">
                <span className="rounded-lg bg-success-emerald px-3 py-1.5 text-xs font-bold text-white">
                  {o.score}% match
                </span>
                <div>
                  <p className="font-bold text-primary-navy">{o.title}</p>
                  <p className="text-[13px] text-neutral-slate">
                    {o.org} &middot; Deadline in {o.deadline}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-6">
                <button className="text-[13px] text-neutral-slate hover:text-primary-navy">Remove</button>
                <button className="rounded-lg bg-primary-navy px-5 py-2.5 text-[13px] font-bold text-white hover:bg-[#1c2b52]">
                  Apply
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
