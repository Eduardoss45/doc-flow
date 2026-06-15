import type { Metadata } from 'next';
import { ClientWrapper } from '@/components/ClientWrapper';
import EnsureClientId from '@/components/EnsureClientId';

export const metadata: Metadata = {
  title: 'App',
  robots: {
    index: false,
    follow: false,
  },
};

export default function AppLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <EnsureClientId />
      <ClientWrapper>{children}</ClientWrapper>
    </>
  );
}
