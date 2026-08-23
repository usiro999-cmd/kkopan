import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Multiverse Quantum AI Academy",
  description: "Graduate-level educational quantum AI drug-discovery simulator",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
