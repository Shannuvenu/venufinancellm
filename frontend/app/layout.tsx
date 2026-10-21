import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: "VenuFin AI — Financial intelligence", description: "Source-grounded financial research workspace" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
