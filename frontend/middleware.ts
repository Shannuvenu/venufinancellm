import { NextRequest, NextResponse } from "next/server";

function unauthorized() {
  return new NextResponse("VenuFin requires a private deployment password.", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="VenuFin AI", charset="UTF-8"', "Cache-Control": "no-store" },
  });
}

export function middleware(request: NextRequest) {
  const password = process.env.APP_PASSWORD;
  if (!password) {
    if (process.env.NODE_ENV === "production") {
      return new NextResponse("Set APP_PASSWORD in the hosting provider before opening VenuFin.", {
        status: 503,
        headers: { "Cache-Control": "no-store" },
      });
    }
    return NextResponse.next();
  }

  const authorization = request.headers.get("authorization") || "";
  const [scheme, encoded] = authorization.split(" ", 2);
  if (scheme?.toLowerCase() !== "basic" || !encoded) return unauthorized();

  try {
    const decoded = atob(encoded);
    const separator = decoded.indexOf(":");
    const username = separator >= 0 ? decoded.slice(0, separator) : "";
    const suppliedPassword = separator >= 0 ? decoded.slice(separator + 1) : "";
    const expectedUsername = process.env.APP_USERNAME || "owner";
    if (username !== expectedUsername || suppliedPassword !== password) return unauthorized();
  } catch {
    return unauthorized();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|robots.txt).*)"],
};
