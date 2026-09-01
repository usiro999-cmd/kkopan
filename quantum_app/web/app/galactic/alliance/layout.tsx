import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "GALACTIC ALLIANCE | 銀河系同盟通信",
  description:
    "複数の創作上の銀河文明と総会、共同決議、外交通信を体験する同盟通信シミュレーター",
};

export default function AllianceLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return children;
}
