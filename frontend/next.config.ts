import type { NextConfig } from "next";

// Sent with every response. Deliberately no full Content-Security-Policy yet: Next's
// inline bootstrap scripts need nonces to live under one, which is its own piece of work.
const SECURITY_HEADERS = [
  // Nobody may frame the site, so a hidden-iframe clickjack on Settings (delete account,
  // cadence) or the login form is off the table. Both spellings: CSP for modern browsers,
  // X-Frame-Options for old ones.
  { key: "Content-Security-Policy", value: "frame-ancestors 'none'" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "X-Content-Type-Options", value: "nosniff" },
  // /reset-password and /verify-email carry a live token in the query string. Cross-site,
  // send only the origin, so following an outbound link can't hand the token to that site.
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
];

const nextConfig: NextConfig = {
  poweredByHeader: false,
  // Traces and copies only the files a production server actually needs into
  // .next/standalone, so the deploy image doesn't carry the full node_modules tree.
  output: "standalone",
  async headers() {
    return [{ source: "/:path*", headers: SECURITY_HEADERS }];
  },
};

export default nextConfig;
