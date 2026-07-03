import { NextRequest, NextResponse } from "next/server";

import { createUpload, listUploads } from "@/lib/ingestion/client";
import { ingestionErrorResponse } from "@/lib/ingestion/route-helpers";
import type { FileType, IngestionStatus } from "@/lib/ingestion/types";

export async function GET(request: NextRequest) {
  const params = request.nextUrl.searchParams;

  try {
    const page = await listUploads({
      page: params.get("page") ? Number(params.get("page")) : undefined,
      size: params.get("size") ? Number(params.get("size")) : undefined,
      file_type: (params.get("file_type") as FileType) || undefined,
      upload_status: (params.get("upload_status") as IngestionStatus) || undefined,
    });
    return NextResponse.json(page);
  } catch (error) {
    return ingestionErrorResponse(error);
  }
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get("file");
    const fileType = formData.get("file_type");

    if (!(file instanceof File) || typeof fileType !== "string") {
      return NextResponse.json(
        {
          error: {
            code: "validation_error",
            message: "Request must include a 'file' and a 'file_type'",
          },
        },
        { status: 422 }
      );
    }

    const uploaded = await createUpload(formData);
    return NextResponse.json(uploaded, { status: 201 });
  } catch (error) {
    return ingestionErrorResponse(error);
  }
}
