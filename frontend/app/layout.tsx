import type { Metadata, Viewport } from 'next';
import './globals.css';
import './redesign.css';

export const metadata: Metadata = {
  title: 'FixedCoin | Mining & Network Explorer',
  description: 'Live FixedCoin node, solo mining and blockchain telemetry.',
  applicationName: 'FixedCoin Explorer',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: '#101820',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
