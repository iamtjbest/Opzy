export default function Input({
  label,
  placeholder,
  type = "text",
  name,
  defaultValue,
  value,
  onChange,
  error,
  required = false,
  autoComplete,
  rightSlot,
}: {
  label: string;
  placeholder: string;
  type?: string;
  name?: string;
  defaultValue?: string;
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  required?: boolean;
  autoComplete?: string;
  rightSlot?: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-2">
      <span className="text-[13px] font-bold text-neutral-ink">{label}</span>
      <span className="relative flex items-center">
        <input
          type={type}
          name={name}
          placeholder={placeholder}
          defaultValue={defaultValue}
          value={value}
          onChange={onChange ? (e) => onChange(e.target.value) : undefined}
          required={required}
          autoComplete={autoComplete}
          aria-invalid={error ? true : undefined}
          className={`w-full rounded-lg border bg-white px-3.5 py-3 text-sm text-neutral-ink placeholder:text-neutral-slate focus:outline-none ${
            error
              ? "border-danger-red focus:border-danger-red"
              : "border-neutral-border focus:border-primary-blue"
          }`}
        />
        {rightSlot && <span className="absolute right-3.5">{rightSlot}</span>}
      </span>
      {error && <span className="text-xs text-danger-red">{error}</span>}
    </label>
  );
}
