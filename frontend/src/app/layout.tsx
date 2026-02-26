import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JobHunter AI",
  description: "Autonomous job search agent dashboard",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
