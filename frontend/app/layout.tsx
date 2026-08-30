import type { Metadata, Viewport } from 'next';
import './globals.css';
import './reference-v3.css';
import './reference-v3-runes.css';
import './reference-fidelity-final.css';
import './reference-v5.css';
import './reference-v6.css';

export const metadata: Metadata = {
  title: 'LiveShare · Solo Mining · Magical Network',
  description: 'FixedCoin solo mining command center',
  applicationName: 'LiveShare',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: '#05040b',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
