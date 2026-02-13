'use client';

import { useEffect, useRef } from 'react';
import { io, Socket } from 'socket.io-client';
import { toast } from 'sonner';
import { ensureClientId } from '@/services/auth';

export function useSocket() {
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    const socket = io(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000', {
      withCredentials: true,
      autoConnect: false,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 3000,
    });

    socketRef.current = socket;

    socket.on('connect', () => {
      console.log('Socket conectado');
    });

    socket.on('connected', data => {
      toast.success(data.message, {
        duration: 10000,
      });
    });

    socket.on('job_completed', data => {
      toast.success(`Conversão concluída! Job ${data.job_id}`, {
        duration: 10000,
        description: data.filename ? `Arquivo: ${data.filename}` : undefined,
      });
    });

    socket.on('job_failed', data => {
      toast.error(`Falha no processamento do job ${data.job_id}`, {
        duration: 10000,
        description: data.error,
      });
    });

    socket.on('auth_error', data => {
      toast.error(data.message, { duration: 8000 });
      socket.disconnect();
    });

    socket.on('connect_error', err => {
      console.error('Erro de conexão socket:', err.message);
      toast.error('Falha na conexão com o servidor de notificações', { duration: 8000 });
    });

    const connectSocket = async () => {
      await ensureClientId();
      socket.connect();
    };

    connectSocket();

    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, []);

  return socketRef.current;
}
