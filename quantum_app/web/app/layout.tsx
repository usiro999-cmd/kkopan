import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SpaceAI KAWARAMACHI | Earth Intelligence Platform",
  description:
    "衛星・AI・ドローン・量子技術で、農地、海洋、災害を見守る地域インテリジェンスプラットフォーム",
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
