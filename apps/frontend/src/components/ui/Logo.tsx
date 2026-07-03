export function Logo({ size = 32 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M12 2L3 7V17L12 22L21 17V7L12 2Z"
        stroke="#00FF9D"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M12 22V12"
        stroke="#00FF9D"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M21 7L12 12L3 7"
        stroke="#00FF9D"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="12" cy="12" r="3" fill="url(#ciq-logo-grad)" />
      <defs>
        <linearGradient
          id="ciq-logo-grad"
          x1="12"
          y1="9"
          x2="12"
          y2="15"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#00FF9D" />
          <stop offset="1" stopColor="#00D1FF" />
        </linearGradient>
      </defs>
    </svg>
  );
}
