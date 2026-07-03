export function MetricCircle({
  percent,
  size = 128,
}: {
  percent: number;
  size?: number;
}) {
  const radius = 56;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - percent / 100);

  return (
    <div
      className="relative flex items-center justify-center"
      style={{ width: size, height: size }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 128 128"
        className="-rotate-90"
      >
        <circle
          cx="64"
          cy="64"
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.05)"
          strokeWidth="12"
        />
        <circle
          cx="64"
          cy="64"
          r={radius}
          fill="none"
          stroke="#00ff9d"
          strokeWidth="12"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="neon-glow"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center font-headline-md text-headline-md text-primary">
        {percent}%
      </div>
    </div>
  );
}
