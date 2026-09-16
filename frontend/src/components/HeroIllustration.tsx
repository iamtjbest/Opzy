export default function HeroIllustration() {
  return (
    <svg viewBox="0 0 400 300" className="h-full w-full" role="img" aria-label="Illustration of matched opportunity cards">
      <rect x="70" y="40" width="220" height="130" rx="16" fill="#F3F5F8" stroke="#E2E5EA" strokeWidth="1.5" transform="rotate(-8 180 105)" />
      <rect x="90" y="70" width="220" height="130" rx="16" fill="#FFFFFF" stroke="#E2E5EA" strokeWidth="1.5" transform="rotate(4 200 135)" />
      <g transform="rotate(-2 200 165)">
        <rect x="80" y="100" width="230" height="140" rx="18" fill="#FFFFFF" stroke="#14213D" strokeWidth="2" />
        <rect x="102" y="122" width="72" height="24" rx="8" fill="#10B981" />
        <text x="138" y="138" fontFamily="Arial, sans-serif" fontWeight="700" fontSize="12" fill="#FFFFFF" textAnchor="middle">92% match</text>
        <rect x="102" y="160" width="150" height="10" rx="5" fill="#1F2430" />
        <rect x="102" y="180" width="190" height="8" rx="4" fill="#E2E5EA" />
        <rect x="102" y="196" width="120" height="8" rx="4" fill="#E2E5EA" />
        <rect x="102" y="216" width="64" height="20" rx="10" fill="#F3F5F8" />
      </g>
      <circle cx="330" cy="70" r="22" fill="none" stroke="#2F6FED" strokeWidth="3" opacity="0.5" />
      <circle cx="342" cy="55" r="7" fill="#10B981" />
      <circle cx="60" cy="220" r="5" fill="#2F6FED" opacity="0.6" />
      <circle cx="45" cy="200" r="3" fill="#10B981" opacity="0.6" />
    </svg>
  );
}
