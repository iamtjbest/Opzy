import Link from "next/link";

export default function Logo({ size = 36 }: { size?: number }) {
  return (
    <Link href="/" className="flex items-center gap-3 transition-transform active:scale-95">
      <div
        className="flex items-center justify-center rounded-[28%] bg-primary-navy font-extrabold text-neutral-white"
        style={{ width: size, height: size, fontSize: size * 0.56 }}
      >
        z
      </div>
      <span className="text-lg font-bold text-primary-navy">Opzy</span>
    </Link>
  );
}
