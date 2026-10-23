import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Promise Keeper — Wearable AI Staging Engine',
  description: 'Wearable AI Staging Engine for Everyday Verbal Commitments via Bee & Bedrock Nova Pro',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen bg-[var(--bg-canvas)] text-[var(--text-main)] transition-colors duration-150">
        {children}
      </body>
    </html>
  );
}
