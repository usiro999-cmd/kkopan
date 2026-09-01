import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "CELESTIAL LINK | 銀河文明通信シミュレーター",
  description:
    "宇宙文明レベル3の銀河文明との外交通信を体験する、創作上の量子通信シミュレーター",
};

export default function GalacticLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return children;
}
