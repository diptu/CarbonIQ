import { NextResponse } from "next/server";

import { deleteUpload, getUpload } from "@/lib/ingestion/client";
import { ingestionErrorResponse } from "@/lib/ingestion/route-helpers";

interface RouteParams {
  params: Promise<{ id: string }>;
}

export async function GET(_request: Request, { params }: RouteParams) {
  const { id } = await params;
  try {
    const upload = await getUpload(id);
    return NextResponse.json(upload);
  } catch (error) {
    return ingestionErrorResponse(error);
  }
}

export async function DELETE(_request: Request, { params }: RouteParams) {
  const { id } = await params;
  try {
    await deleteUpload(id);
    return NextResponse.json({ ok: true });
  } catch (error) {
    return ingestionErrorResponse(error);
  }
}
