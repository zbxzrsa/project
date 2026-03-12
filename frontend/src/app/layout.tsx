import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Code Quality Platform",
  description: "AI-powered code quality and architecture analysis platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
