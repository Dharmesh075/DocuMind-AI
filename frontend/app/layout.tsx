import type { Metadata } from "next";
import "@/styles/compiled.css";
import AppShell from "@/components/layout/AppShell";

export const metadata: Metadata = {
  title: "DocuMind AI - Own your documents",
  description: "Transform unstructured documents into intelligent data. Autonomous AI Document Intelligence platform with Liquid Glass interface.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="overflow-x-hidden">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
