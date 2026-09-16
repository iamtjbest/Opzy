export default function Input({
  label,
  placeholder,
  type = "text",
  rightSlot,
}: {
  label: string;
  placeholder: string;
  type?: string;
  rightSlot?: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-2">
      <span className="text-[13px] font-bold text-neutral-ink">{label}</span>
      <span className="relative flex items-center">
        <input
          type={type}
          placeholder={placeholder}
          className="w-full rounded-lg border border-neutral-border bg-white px-3.5 py-3 text-sm text-neutral-ink placeholder:text-neutral-slate focus:border-primary-blue focus:outline-none"
        />
        {rightSlot && <span className="absolute right-3.5">{rightSlot}</span>}
      </span>
    </label>
  );
}
