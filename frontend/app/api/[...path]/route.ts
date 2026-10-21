import { NextRequest, NextResponse } from "next/server";

type RouteContext = { params: Promise<{ path: string[] }> };

async function proxy(request: NextRequest, context: RouteContext) {
  const backend = process.env.BACKEND_URL || (process.env.NODE_ENV === "development" ? "http://127.0.0.1:8000" : "");
  if (!backend) return NextResponse.json({ detail: "Set BACKEND_URL in the frontend hosting environment." }, { status: 503 });

  const token = process.env.APP_INTERNAL_TOKEN || "";
  if (process.env.NODE_ENV === "production" && !token) {
    return NextResponse.json({ detail: "Production API gateway token is not configured." }, { status: 503 });
  }

  const { path } = await context.params;
  const route = path.join("/");
  const upstreamPath = route === "docs" ? "/docs" : route === "openapi.json" ? "/openapi.json" : `/api/${route}`;
  const upstream = new URL(upstreamPath, backend);
  upstream.search = request.nextUrl.search;
  if (route === "docs") upstream.searchParams.set("url", "/api/openapi.json");

  const headers = new Headers(request.headers);
  for (const name of ["host", "connection", "content-length", "authorization", "cookie", "accept-encoding"]) headers.delete(name);
  if (token) headers.set("x-internal-api-key", token);

  const method = request.method;
  const body = method === "GET" || method === "HEAD" ? undefined : await request.arrayBuffer();
  try {
    const response = await fetch(upstream, { method, headers, body, cache: "no-store", redirect: "manual" });
    const responseHeaders = new Headers(response.headers);
    for (const name of ["connection", "transfer-encoding", "content-encoding", "content-length", "set-cookie"]) responseHeaders.delete(name);
    responseHeaders.set("Cache-Control", "no-store");
    return new Response(response.body, { status: response.status, headers: responseHeaders });
  } catch {
    return NextResponse.json({ detail: "The VenuFin API could not be reached. Check BACKEND_URL and backend health." }, { status: 502 });
  }
}

export const GET = proxy;
export const POST = proxy;
export const DELETE = proxy;
