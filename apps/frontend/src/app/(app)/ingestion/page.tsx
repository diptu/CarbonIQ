import type { Metadata } from "next";

import { IngestionDashboard } from "./IngestionDashboard";

export const metadata: Metadata = {
  title: "Data Ingestion Hub",
  description: "Upload and track utility bills, NEM12 files, and renewable certificates.",
};

export default function IngestionPage() {
  return <IngestionDashboard />;
}
