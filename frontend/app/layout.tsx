import type { Metadata, Viewport } from 'next';
import './globals.css';
import './reference-v3.css';
import './reference-v3-runes.css';
import './reference-fidelity-final.css';
import './reference-v5.css';
import './reference-v6.css';
import './reference-v7.css';
import './reference-v8.css';
import './reference-magical.css';
import './redesign.css';

export const metadata: Metadata = {
  title: 'FixedCoin Explorer · Solo Mining & Mempool',
  description: 'Live FixedCoin solo mining, blockchain and mempool explorer.',
  applicationName: 'FixedCoin Explorer',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: '#060a0e',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
