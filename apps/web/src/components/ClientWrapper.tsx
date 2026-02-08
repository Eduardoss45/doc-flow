'use client';

import { useSocket } from '@/hooks/useSocket';
import { Toaster } from '@/components/ui/sonner';

export function ClientWrapper({ children }: { children: React.ReactNode }) {
  useSocket();

  return (
    <>
      <Toaster richColors position="bottom-right" />
      {children}
    </>
  );
}
