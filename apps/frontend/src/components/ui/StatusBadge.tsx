import { ReactNode } from "react";

export type StatusBadgeVariant = "pending" | "verified" | "minted" | "flagged";

const icons: Record<StatusBadgeVariant, string> = {
  pending: "hourglass_empty",
  verified: "verified",
  minted: "token",
  flagged: "report",
};

export function StatusBadge({
  variant,
  children,
}: {
  variant: StatusBadgeVariant;
  children: ReactNode;
}) {
  return (
    <span className={`status-badge badge-${variant}`}>
      <span className="material-symbols-outlined text-[16px]">
        {icons[variant]}
      </span>
      {children}
    </span>
  );
}
