"use client";

/**
 * `retry()`, not `reset()`. The Next 16 docs are explicit: reset() clears the error state
 * and re-renders the children *without re-fetching*, so an error thrown while the server
 * rendered the page comes straight back. retry() re-fetches, which is what "Try again"
 * has to mean when the cause was an unreachable backend.
 */
export default function Error({ retry }: { error: Error; retry: () => void }) {
  return (
    <div className="flex min-h-screen w-full items-center justify-center bg-neutral-mist px-4">
      <div className="w-full max-w-[440px] rounded-2xl border border-neutral-border bg-white p-8 text-center">
        <h1 className="text-xl font-bold text-primary-navy">Something went wrong</h1>
        <p className="mt-2 text-sm text-neutral-slate">
          We couldn&rsquo;t reach Opzy just then. It&rsquo;s usually temporary.
        </p>
        <button
          onClick={() => retry()}
          className="mt-6 inline-flex items-center justify-center rounded-lg bg-primary-navy px-5 py-3 text-sm font-bold text-white transition-all hover:bg-primary-blue active:scale-95 cursor-pointer"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
