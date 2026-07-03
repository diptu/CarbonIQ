import type { FileType, IngestionStatus } from "@/lib/ingestion/types";

interface StatusMeta {
  label: string;
  icon: string;
  className: string;
  pulsing?: boolean;
}

export const STATUS_META: Record<IngestionStatus, StatusMeta> = {
  pending: {
    label: "Queued",
    icon: "hourglass_empty",
    className: "text-on-surface-variant bg-white/5 border-white/10",
  },
  validating: {
    label: "Validating",
    icon: "fact_check",
    className: "text-secondary bg-secondary/10 border-secondary/20",
    pulsing: true,
  },
  validated: {
    label: "Routing",
    icon: "check_circle",
    className: "text-primary bg-primary/10 border-primary/20",
  },
  dispatching: {
    label: "Dispatching",
    icon: "sync",
    className: "text-secondary bg-secondary/10 border-secondary/20",
    pulsing: true,
  },
  dispatched: {
    label: "Complete",
    icon: "task_alt",
    className: "text-primary bg-primary/10 border-primary/20",
  },
  validation_failed: {
    label: "Validation Failed",
    icon: "error",
    className: "text-error bg-error/10 border-error/20",
  },
  dispatch_failed: {
    label: "Dispatch Failed",
    icon: "report",
    className: "text-error bg-error/10 border-error/20",
  },
};

export const FILE_TYPE_ICONS: Record<FileType, string> = {
  bill_pdf: "picture_as_pdf",
  bill_image: "image",
  nem12_csv: "electric_meter",
  rec_certificate: "eco",
  lgc_certificate: "eco",
  ppa_contract: "description",
};

export function formatRelativeTime(iso: string): string {
  const date = new Date(iso);
  const diffMs = date.getTime() - Date.now();
  const diffSeconds = Math.round(diffMs / 1000);

  const divisions: [Intl.RelativeTimeFormatUnit, number][] = [
    ["second", 60],
    ["minute", 60],
    ["hour", 24],
    ["day", 30],
    ["month", 12],
    ["year", Infinity],
  ];

  const formatter = new Intl.RelativeTimeFormat("en", { numeric: "auto" });
  let duration = diffSeconds;
  for (const [unit, amount] of divisions) {
    if (Math.abs(duration) < amount) {
      return formatter.format(Math.round(duration), unit);
    }
    duration /= amount;
  }
  return formatter.format(Math.round(duration), "year");
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB"];
  let value = bytes / 1024;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }
  return `${value.toFixed(1)} ${units[unitIndex]}`;
}
