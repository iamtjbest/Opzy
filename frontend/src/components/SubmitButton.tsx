"use client";

import { useFormStatus } from "react-dom";

/** Submit control that disables itself while its form is in flight. */
export default function SubmitButton({
  children,
  pendingLabel,
  className = "",
}: {
  children: React.ReactNode;
  pendingLabel?: string;
  className?: string;
}) {
  const { pending } = useFormStatus();

  return (
    <button
      type="submit"
      disabled={pending}
      className={`inline-flex items-center justify-center rounded-lg bg-primary-navy px-5 py-3 text-sm font-bold tracking-[0.2px] text-white transition-all hover:bg-primary-blue active:scale-95 disabled:cursor-not-allowed disabled:opacity-60 ${className}`}
    >
      {pending && pendingLabel ? pendingLabel : children}
    </button>
  );
}
