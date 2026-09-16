import type { Metadata } from "next";
import "@fontsource-variable/bricolage-grotesque";
import "./globals.css";

export const metadata: Metadata = {
  title: "Opzy — Never miss an opportunity",
  description:
    "Opzy finds the jobs, internships, scholarships, and grants you're actually eligible for, and tells you why each one fits, before the deadline passes.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
