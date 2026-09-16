import Link from "next/link";
import Logo from "./Logo";

const links = [
  { href: "/feed", label: "Feed" },
  { href: "/saved", label: "Saved" },
  { href: "/applications", label: "Applications" },
];

export default function AppNav({ active }: { active: string }) {
  return (
    <div className="flex h-[72px] w-full items-center justify-between border-b border-neutral-border bg-white px-16">
      <div className="flex items-center gap-10">
        <Logo size={36} />
        <nav className="flex items-center gap-6">
          {links.map((l) => (
            <Link
              key={l.label}
              href={l.href}
              className={`text-sm ${
                active === l.label ? "font-bold text-primary-navy" : "text-neutral-slate hover:text-primary-navy"
              }`}
            >
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
      <Link href="/settings" className="h-10 w-10 rounded-full border border-neutral-border bg-neutral-mist" />
    </div>
  );
}
