import Link from "next/link";
import { ReactNode } from "react";

type Variant = "primary" | "outline-dark" | "outline-light" | "on-dark";

const variants: Record<Variant, string> = {
  primary: "bg-primary-navy text-white hover:bg-primary-blue",
  "outline-dark":
    "border border-neutral-border text-white hover:bg-primary-navy hover:border-primary-navy",
  "outline-light":
    "border border-white text-white hover:bg-primary-navy hover:border-primary-navy",
  "on-dark": "bg-white text-primary-navy hover:bg-primary-navy hover:text-white",
};

export default function Button({
  children,
  variant = "primary",
  className = "",
  href,
  onClick,
  type = "button",
}: {
  children: ReactNode;
  variant?: Variant;
  className?: string;
  href?: string;
  onClick?: () => void;
  type?: "button" | "submit";
}) {
  const classes = `inline-flex items-center justify-center rounded-lg px-5 py-3 text-sm font-bold tracking-[0.2px] transition-all active:scale-95 cursor-pointer ${variants[variant]} ${className}`;
  if (href) {
    return (
      <Link href={href} className={classes}>
        {children}
      </Link>
    );
  }
  return (
    <button type={type} onClick={onClick} className={classes}>
      {children}
    </button>
  );
}
