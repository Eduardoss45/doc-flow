import { api } from '@/infra/api';
import { toast } from 'sonner';
import { ensureClientId } from '@/services/auth';

type UploadResponse = {
  job_id: string;
  status: string;
  message: string;
};

export type ConvertResponse = {
  success: boolean;
  jobId?: string;
  message?: string;
  error?: string;
};

export async function convertFile(file: File, conversionType: string): Promise<ConvertResponse> {
  const clientId = await ensureClientId();
  if (!clientId) {
    toast.error('Não foi possível identificar a sessão. Tente recarregar a página.');
    return { success: false, error: 'Falha ao obter client_id' };
  }

  const formData = new FormData();
  formData.append('file', file);
  formData.append('conversion_type', conversionType);

  try {
    const { data, status } = await api.post<UploadResponse>('/documents/upload', formData);

    if (status === 202 && data.job_id) {
      toast.success('Upload recebido! Processamento em andamento...');
      return {
        success: true,
        jobId: data.job_id,
        message: data.message,
      };
    }

    toast.error(data.message || 'Falha ao enviar o arquivo');
    return {
      success: false,
      error: data.message || 'Resposta inesperada do servidor',
    };
  } catch (error: unknown) {
    const err = error as {
      response?: { data?: { error?: string }; statusText?: string; status?: number };
      request?: unknown;
      message?: string;
    };
    let message = 'Erro ao converter o arquivo';

    if (err.response) {
      const serverMsg = err.response.data?.error || err.response.statusText || '';
      if (err.response.status === 400) {
        message = serverMsg.includes('client_id')
          ? 'Sessão não identificada. Tente novamente.'
          : serverMsg || 'Requisição inválida';
      } else if (err.response.status === 403) {
        message = 'Limite de cota atingido ou acesso negado';
      } else {
        message = serverMsg || `Erro ${err.response.status}`;
      }
    } else if (err.request) {
      message = 'Sem resposta do servidor. Verifique sua conexão.';
    } else {
      message = err.message || 'Erro inesperado';
    }

    toast.error(message);
    return { success: false, error: message };
  }
}
