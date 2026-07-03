export function Sparkline({
  path,
  color = "#00ff9d",
  fill = true,
  viewBox = "0 0 100 40",
  height = "100%",
}: {
  path: string;
  color?: string;
  fill?: boolean;
  viewBox?: string;
  height?: string | number;
}) {
  const gradientId = `sparkline-${path.length}-${color.replace("#", "")}`;
  const [, , , vbHeight] = viewBox.split(" ").map(Number);

  return (
    <svg
      className="w-full"
      style={{ height }}
      preserveAspectRatio="none"
      viewBox={viewBox}
    >
      <path d={path} fill="none" stroke={color} strokeWidth="2" />
      {fill && (
        <>
          <defs>
            <linearGradient id={gradientId} x1="0%" x2="0%" y1="0%" y2="100%">
              <stop offset="0%" stopColor={color} stopOpacity="0.3" />
              <stop offset="100%" stopColor={color} stopOpacity="0" />
            </linearGradient>
          </defs>
          <path
            d={`${path} V${vbHeight} H0 Z`}
            fill={`url(#${gradientId})`}
          />
        </>
      )}
    </svg>
  );
}
