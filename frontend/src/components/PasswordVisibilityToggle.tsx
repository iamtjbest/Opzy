"use client";

/** The small eye / eye-slash button that sits inside a password field's right edge. */
export default function PasswordVisibilityToggle({
  visible,
  onToggle,
}: {
  visible: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onToggle}
      // tabIndex isn't skipped: a mouse user can click it, a keyboard user can tab to it,
      // same as any other control.
      aria-label={visible ? "Hide password" : "Show password"}
      aria-pressed={visible}
      className="flex h-6 w-6 items-center justify-center text-neutral-slate hover:text-neutral-ink"
    >
      {visible ? (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M3 3l18 18M10.584 10.587a2 2 0 002.828 2.83M9.363 5.365A9.466 9.466 0 0112 5c5 0 9 4 10 7-.407 1.222-1.165 2.527-2.223 3.68M6.52 6.519C4.48 7.86 2.9 9.9 2 12c1 3 5 7 10 7 1.179 0 2.298-.22 3.317-.598"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      ) : (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7-10-7-10-7z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.6" />
        </svg>
      )}
    </button>
  );
}
