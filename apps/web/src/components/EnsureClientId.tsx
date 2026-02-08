'use client';

import { useEffect } from 'react';
import { api } from '@/infra/api';

async function ensureClientId() {
  try {
    const res = await api.post('/auth/client-id');

    if (res.status >= 400) {
      console.error('Falha ao obter client_id', res.status, res.data);
      return null;
    }

    const data = res.data;
    console.log('Client ID obtido:', data.client_id);
    return data.client_id;
  } catch (err) {
    console.error('Erro ao garantir client_id:', err);
    return null;
  }
}

export default function EnsureClientId() {
  useEffect(() => {
    ensureClientId();
  }, []);

  return null;
}
