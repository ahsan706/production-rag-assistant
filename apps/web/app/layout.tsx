import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Production RAG Assistant",
  description: "Dockerized production-style RAG assistant",
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
