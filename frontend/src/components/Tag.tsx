export default function Tag({
  children,
  tone = "mist",
}: {
  children: string;
  tone?: "mist" | "on-dark" | "emerald-outline";
}) {
  const styles = {
    mist: "bg-neutral-mist text-neutral-ink",
    "on-dark": "bg-white/15 border border-white/15 text-white",
    "emerald-outline": "bg-success-emerald/10 border border-success-emerald/30 text-success-emerald",
  }[tone];

  return (
    <span className={`inline-flex items-center rounded-full px-[22px] py-3 text-base font-medium whitespace-nowrap ${styles}`}>
      {children}
    </span>
  );
}
