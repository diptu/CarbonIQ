"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "motion/react";

import { GlassCard } from "@/components/ui";
import {
  FILE_TYPES,
  FILE_TYPE_LABELS,
  TERMINAL_STATUSES,
  type FileType,
  type IngestedFile,
} from "@/lib/ingestion/types";

import {
  FILE_TYPE_ICONS,
  STATUS_META,
  formatBytes,
  formatRelativeTime,
} from "./status-meta";

const POLL_INTERVAL_MS = 3000;
const UPLOAD_FLASH_MS = 2500;

async function parseJsonSafely(response: Response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

export function IngestionDashboard() {
  const [uploads, setUploads] = useState<IngestedFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fileType, setFileType] = useState<FileType>("bill_pdf");
  const [isDragActive, setIsDragActive] = useState(false);
  const [pendingUploads, setPendingUploads] = useState(0);
  const [uploadFlash, setUploadFlash] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchUploads = useCallback(async () => {
    try {
      const res = await fetch("/api/ingestion/uploads?size=50");
      const body = await parseJsonSafely(res);
      if (!res.ok) {
        throw new Error(body?.error?.message ?? "Failed to load uploads");
      }
      setUploads(body.items as IngestedFile[]);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load uploads");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUploads();
  }, [fetchUploads]);

  useEffect(() => {
    const hasActive = uploads.some((u) => !TERMINAL_STATUSES.includes(u.status));
    if (!hasActive) return;

    const interval = setInterval(fetchUploads, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [uploads, fetchUploads]);

  const uploadFiles = useCallback(
    async (files: FileList | File[]) => {
      const fileArray = Array.from(files);
      setPendingUploads((n) => n + fileArray.length);
      setError(null);

      for (const file of fileArray) {
        try {
          const formData = new FormData();
          formData.append("file", file);
          formData.append("file_type", fileType);

          const res = await fetch("/api/ingestion/uploads", {
            method: "POST",
            body: formData,
          });
          const body = await parseJsonSafely(res);
          if (!res.ok) {
            throw new Error(body?.error?.message ?? "Upload failed");
          }
          setUploads((prev) => [body as IngestedFile, ...prev]);
          setUploadFlash(file.name);
          setTimeout(() => setUploadFlash(null), UPLOAD_FLASH_MS);
        } catch (err) {
          setError(err instanceof Error ? err.message : "Upload failed");
        } finally {
          setPendingUploads((n) => Math.max(0, n - 1));
        }
      }
    },
    [fileType]
  );

  const handleDelete = useCallback(async (id: string) => {
    try {
      const res = await fetch(`/api/ingestion/uploads/${id}`, { method: "DELETE" });
      if (!res.ok) {
        const body = await parseJsonSafely(res);
        throw new Error(body?.error?.message ?? "Delete failed");
      }
      setUploads((prev) => prev.filter((u) => u.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  }, []);

  const handleDownload = useCallback(async (id: string) => {
    try {
      const res = await fetch(`/api/ingestion/uploads/${id}/download-url`);
      const body = await parseJsonSafely(res);
      if (!res.ok) {
        throw new Error(body?.error?.message ?? "Could not get download link");
      }
      window.open(body.url as string, "_blank", "noopener,noreferrer");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not get download link");
    }
  }, []);

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragActive(false);
    if (event.dataTransfer.files.length) {
      uploadFiles(event.dataTransfer.files);
    }
  };

  const hasAnyUploads = uploads.length > 0;
  const activeUploads = uploads.filter((u) => !TERMINAL_STATUSES.includes(u.status));
  const recentUploads = uploads.filter((u) => TERMINAL_STATUSES.includes(u.status));

  return (
    <div className="px-6 lg:px-12 py-10 max-w-7xl mx-auto space-y-10">
      <section className="space-y-2">
        <h1 className="font-headline-xl text-headline-xl text-on-surface tracking-tight">
          Data Ingestion Hub
        </h1>
        <p className="text-on-surface-variant text-body-lg max-w-2xl">
          Upload utility bills, NEM12 smart-meter exports, and renewable
          certificates. Files are structurally validated and routed to the
          right processing pipeline automatically.
        </p>
      </section>

      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="flex items-center justify-between gap-4 rounded-xl border border-error/20 bg-error/10 px-6 py-4">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-error">error</span>
                <p className="text-sm text-on-surface">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-on-surface-variant hover:text-on-surface"
              >
                <span className="material-symbols-outlined text-sm">close</span>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-gutter">
        {/* Upload area */}
        <GlassCard
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragActive(true);
          }}
          onDragLeave={() => setIsDragActive(false)}
          onDrop={handleDrop}
          className={`lg:col-span-8 p-8 flex flex-col items-center justify-center border-dashed border-2 min-h-[400px] transition-colors ${
            isDragActive ? "border-primary bg-primary/5" : "border-primary/20"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            hidden
            onChange={(event) => {
              if (event.target.files?.length) {
                uploadFiles(event.target.files);
                event.target.value = "";
              }
            }}
          />

          <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mb-6 relative">
            <AnimatePresence mode="wait">
              {uploadFlash ? (
                <motion.span
                  key="success"
                  initial={{ scale: 0.5, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.5, opacity: 0 }}
                  transition={{ type: "spring", stiffness: 300, damping: 20 }}
                  className="material-symbols-outlined text-primary text-4xl"
                >
                  check_circle
                </motion.span>
              ) : pendingUploads > 0 ? (
                <motion.span
                  key="uploading"
                  animate={{ rotate: 360 }}
                  transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                  className="material-symbols-outlined text-primary text-4xl"
                >
                  progress_activity
                </motion.span>
              ) : (
                <motion.span
                  key="idle"
                  initial={{ scale: 0.9, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="material-symbols-outlined text-primary text-4xl"
                >
                  cloud_upload
                </motion.span>
              )}
            </AnimatePresence>
          </div>

          <h3 className="font-headline-md text-headline-md mb-2">
            {uploadFlash ? (
              <span className="text-primary">Uploaded {uploadFlash}</span>
            ) : (
              "Drop your data here"
            )}
          </h3>
          <p className="text-on-surface-variant mb-6 text-center max-w-md">
            {uploadFlash
              ? "Structural validation is running in the background — watch it below."
              : "Supported: utility bill PDFs/photos, NEM12 CSVs, and REC/LGC/PPA documents. Max file size 25MB."}
          </p>

          <label className="mb-6 flex flex-col items-center gap-2">
            <span className="text-[11px] text-on-surface-variant uppercase tracking-widest">
              Data Type
            </span>
            <select
              value={fileType}
              onChange={(event) => setFileType(event.target.value as FileType)}
              className="bg-surface-container-lowest border border-white/10 rounded-lg px-4 py-2 text-sm text-on-surface focus:outline-none focus:border-primary-container"
            >
              {FILE_TYPES.map((type) => (
                <option key={type} value={type}>
                  {FILE_TYPE_LABELS[type]}
                </option>
              ))}
            </select>
          </label>

          <div className="flex gap-4">
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={pendingUploads > 0}
              className="bg-primary-container text-on-primary-container px-8 py-3 rounded-xl font-label-md neon-glow hover:opacity-90 transition-all disabled:opacity-50"
            >
              {pendingUploads > 0 ? `Uploading ${pendingUploads}…` : "Browse Files"}
            </button>
            <button
              onClick={fetchUploads}
              className="bg-surface-container-highest text-on-surface px-8 py-3 rounded-xl font-label-md border border-white/5 hover:bg-white/10 transition-all"
            >
              Refresh
            </button>
          </div>

          <div className="mt-12 grid grid-cols-3 gap-8 w-full border-t border-white/5 pt-8">
            {(["bill_pdf", "nem12_csv", "ppa_contract"] as const).map((type) => (
              <div key={type} className="text-center">
                <span className="material-symbols-outlined text-secondary mb-2 block">
                  {FILE_TYPE_ICONS[type]}
                </span>
                <p className="text-xs text-on-surface-variant uppercase tracking-tighter">
                  {FILE_TYPE_LABELS[type]}
                </p>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* AI insights (roadmap preview — not yet backed by ai-agent-service) */}
        <div className="lg:col-span-4 space-y-gutter">
          <GlassCard className="p-6 border-l-4 border-l-primary-container">
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-label-md text-label-md uppercase tracking-wider text-primary">
                AI Insights
              </h3>
              <span className="material-symbols-outlined text-primary-container">
                neurology
              </span>
            </div>
            <div className="space-y-6">
              <div className="bg-white/5 rounded-2xl p-4 border border-white/5">
                <p className="text-xs text-on-surface-variant uppercase mb-3">
                  Coming Soon
                </p>
                <p className="text-sm text-on-surface-variant">
                  Gap-filling, load-profile inference, and anomaly detection
                  arrive with{" "}
                  <span className="text-on-surface font-medium">
                    ai-agent-service
                  </span>
                  .
                </p>
              </div>
            </div>
          </GlassCard>
          <GlassCard className="p-6">
            <h4 className="font-label-md text-label-md mb-4 text-on-surface">
              Compliance Guard
            </h4>
            <div className="flex items-start gap-3">
              <div className="p-2 bg-secondary/10 rounded-lg">
                <span className="material-symbols-outlined text-secondary text-xl">
                  gavel
                </span>
              </div>
              <p className="text-sm text-on-surface-variant">
                All processed data automatically maps to{" "}
                <span className="text-on-surface font-medium">
                  GHG Protocol Scope 2
                </span>{" "}
                standards.
              </p>
            </div>
          </GlassCard>
        </div>

        {!loading && !hasAnyUploads ? (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="lg:col-span-12"
          >
            <GlassCard className="p-12 flex flex-col items-center text-center gap-3">
              <span className="material-symbols-outlined text-on-surface-variant text-5xl">
                inbox
              </span>
              <h3 className="font-headline-md text-headline-md">
                No files uploaded yet
              </h3>
              <p className="text-on-surface-variant max-w-md">
                Drop a file above to see it appear here — status updates
                live as it moves through validation and routing.
              </p>
            </GlassCard>
          </motion.div>
        ) : (
          <>
            {/* Active ingestions */}
            <div className="lg:col-span-12 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-headline-md text-headline-md">
                  Active Ingestions
                </h3>
                <span className="text-sm text-on-surface-variant">
                  {loading
                    ? "Loading…"
                    : `${activeUploads.length} in flight • ${recentUploads.length} completed`}
                </span>
              </div>

              {activeUploads.length === 0 ? (
                <GlassCard className="p-8 text-center text-on-surface-variant">
                  {loading ? "Loading ingestions…" : "Nothing in flight right now."}
                </GlassCard>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <AnimatePresence mode="popLayout">
                    {activeUploads.map((item) => {
                      const meta = STATUS_META[item.status];
                      return (
                        <motion.div
                          key={item.id}
                          layout
                          initial={{ opacity: 0, y: 12, scale: 0.96 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          exit={{ opacity: 0, scale: 0.95 }}
                          transition={{ duration: 0.25 }}
                        >
                          <GlassCard className="p-5">
                            <div className="flex justify-between items-start mb-4">
                              <div className="flex items-center gap-3">
                                <div
                                  className={`w-8 h-8 rounded flex items-center justify-center border ${meta.className}`}
                                >
                                  <span className="material-symbols-outlined text-sm">
                                    {FILE_TYPE_ICONS[item.file_type]}
                                  </span>
                                </div>
                                <div>
                                  <p className="text-sm font-medium truncate w-32">
                                    {item.original_filename}
                                  </p>
                                  <p className="text-[10px] text-on-surface-variant uppercase">
                                    {meta.label}
                                  </p>
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              {meta.pulsing ? (
                                <motion.span
                                  animate={{ rotate: 360 }}
                                  transition={{
                                    repeat: Infinity,
                                    duration: 1,
                                    ease: "linear",
                                  }}
                                  className="material-symbols-outlined text-secondary text-base"
                                >
                                  progress_activity
                                </motion.span>
                              ) : (
                                <motion.span
                                  animate={{ opacity: [0.4, 1, 0.4] }}
                                  transition={{ repeat: Infinity, duration: 1.6 }}
                                  className="material-symbols-outlined text-on-surface-variant text-base"
                                >
                                  hourglass_empty
                                </motion.span>
                              )}
                              <span className="text-[11px] text-on-surface-variant">
                                {meta.pulsing ? "Processing…" : "Waiting in queue…"}
                              </span>
                            </div>
                          </GlassCard>
                        </motion.div>
                      );
                    })}
                  </AnimatePresence>
                </div>
              )}
            </div>

            {/* Recent ingestions table */}
            <div className="lg:col-span-12">
              <GlassCard className="overflow-hidden">
                <div className="px-8 py-6 border-b border-white/5 flex items-center justify-between bg-white/5">
                  <h3 className="font-headline-md text-headline-md">
                    Recent Ingestions
                  </h3>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse min-w-[720px]">
                    <thead className="bg-surface-container-low text-on-surface-variant text-[11px] uppercase tracking-widest">
                      <tr>
                        <th className="px-8 py-4 font-medium">File</th>
                        <th className="px-8 py-4 font-medium">Data Type</th>
                        <th className="px-8 py-4 font-medium">Size</th>
                        <th className="px-8 py-4 font-medium">Uploaded</th>
                        <th className="px-8 py-4 font-medium">Status</th>
                        <th className="px-8 py-4 font-medium text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {recentUploads.length === 0 ? (
                        <tr>
                          <td
                            colSpan={6}
                            className="px-8 py-10 text-center text-on-surface-variant"
                          >
                            {loading ? "Loading…" : "No completed ingestions yet."}
                          </td>
                        </tr>
                      ) : (
                        <AnimatePresence>
                          {recentUploads.map((row) => {
                            const meta = STATUS_META[row.status];
                            return (
                              <motion.tr
                                key={row.id}
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                exit={{ opacity: 0 }}
                                className="hover:bg-white/[0.02] transition-colors"
                              >
                                <td className="px-8 py-5">
                                  <div className="flex items-center gap-3">
                                    <span className="material-symbols-outlined text-secondary text-sm">
                                      {FILE_TYPE_ICONS[row.file_type]}
                                    </span>
                                    <span className="font-medium">
                                      {row.original_filename}
                                    </span>
                                  </div>
                                  {row.validation_errors && (
                                    <p className="mt-1 text-[11px] text-error">
                                      {row.validation_errors[0]}
                                    </p>
                                  )}
                                </td>
                                <td className="px-8 py-5 text-on-surface-variant">
                                  {FILE_TYPE_LABELS[row.file_type]}
                                </td>
                                <td className="px-8 py-5 text-on-surface-variant">
                                  {formatBytes(row.size_bytes)}
                                </td>
                                <td className="px-8 py-5 text-on-surface-variant">
                                  {formatRelativeTime(row.created_at)}
                                </td>
                                <td className="px-8 py-5">
                                  <span
                                    className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${meta.className}`}
                                  >
                                    {meta.label}
                                  </span>
                                </td>
                                <td className="px-8 py-5">
                                  <div className="flex items-center justify-end gap-3">
                                    <button
                                      onClick={() => handleDownload(row.id)}
                                      className="text-on-surface-variant hover:text-primary transition-colors"
                                      title="Download"
                                    >
                                      <span className="material-symbols-outlined text-sm">
                                        download
                                      </span>
                                    </button>
                                    <button
                                      onClick={() => handleDelete(row.id)}
                                      className="text-on-surface-variant hover:text-error transition-colors"
                                      title="Delete"
                                    >
                                      <span className="material-symbols-outlined text-sm">
                                        delete
                                      </span>
                                    </button>
                                  </div>
                                </td>
                              </motion.tr>
                            );
                          })}
                        </AnimatePresence>
                      )}
                    </tbody>
                  </table>
                </div>
              </GlassCard>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
