import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "GalacticOS | 銀河運用統合システム",
  description:
    "恒星、銀河ネットワーク、文明支援、科学研究、防災安全を統合する創作上の銀河運用OSシミュレーター",
};

export default function GalacticOSLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return children;
}
