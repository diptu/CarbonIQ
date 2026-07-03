import { NextResponse } from "next/server";

import { getDownloadUrl } from "@/lib/ingestion/client";
import { ingestionErrorResponse } from "@/lib/ingestion/route-helpers";

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function GET(_request: Request, { params }: RouteParams) {
  const { id } = await params;
  try {
    const result = await getDownloadUrl(id);
    return NextResponse.json(result);
  } catch (error) {
    return ingestionErrorResponse(error);
  }
}
