import AppNav from "@/components/AppNav";
import Link from "next/link";
import { opportunities } from "@/lib/opportunities";

export default function Applications() {
  // In a real app, you would fetch applied opportunities. 
  // Here we just mock an empty state or take a slice.
  const applied = opportunities.slice(0, 1); // Mock 1 applied

  return (
    <div className="min-h-screen w-full bg-neutral-mist">
      <AppNav active="Applications" />
      <div className="mx-auto max-w-[1140px] px-6 py-12">
        <h1 className="text-[28px] font-bold text-primary-navy">Saved & applications</h1>
        <div className="mt-6 flex gap-8 border-b border-neutral-border">
          <Link href="/saved" className="pb-3 text-sm font-bold text-neutral-slate hover:text-primary-navy">
            Saved
          </Link>
          <Link href="/applications" className="border-b-2 border-primary-navy pb-3 text-sm font-bold text-primary-navy">
            Applications ({applied.length})
          </Link>
        </div>

        <div className="mt-6 flex flex-col gap-4">
          {applied.length === 0 ? (
            <div className="rounded-xl border border-neutral-border bg-white p-8 text-center">
              <p className="text-neutral-slate">You haven&rsquo;t applied to any opportunities yet.</p>
              <Link href="/feed" className="mt-4 inline-block text-sm font-bold text-primary-blue hover:underline">
                Find opportunities
              </Link>
            </div>
          ) : (
            applied.map((o) => (
              <div key={o.id} className="flex flex-col sm:flex-row sm:items-center justify-between rounded-xl border border-neutral-border bg-white p-5 gap-4">
                <div className="flex items-center gap-4">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-neutral-mist font-bold text-primary-navy">
                    {o.org[0]}
                  </div>
                  <div>
                    <p className="font-bold text-primary-navy">{o.title}</p>
                    <p className="text-[13px] text-neutral-slate">
                      {o.org} &middot; Applied recently
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <span className="rounded-full bg-success-emerald/10 px-3 py-1 text-xs font-bold text-success-emerald">
                    Application Sent
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
