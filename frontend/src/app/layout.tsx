import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Flight Route Optimizer - Airport Map",
  description: "Visualize US flight routes and airports",
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
