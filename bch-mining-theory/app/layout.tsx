import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BCH Mining Theory",
  description: "Live Bitcoin Cash solo-mining probability dashboard.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
