import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LiveShare · FixedCoin Solo Mining",
  description: "FixedCoin solo mining arcane command center",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
