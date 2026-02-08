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
  } catch (error: any) {
    let message = 'Erro ao converter o arquivo';

    if (error.response) {
      const serverMsg = error.response.data?.error || error.response.statusText;
      if (error.response.status === 400) {
        message = serverMsg.includes('client_id')
          ? 'Sessão não identificada. Tente novamente.'
          : serverMsg || 'Requisição inválida';
      } else if (error.response.status === 403) {
        message = 'Limite de cota atingido ou acesso negado';
      } else {
        message = serverMsg || `Erro ${error.response.status}`;
      }
    } else if (error.request) {
      message = 'Sem resposta do servidor. Verifique sua conexão.';
    } else {
      message = error.message || 'Erro inesperado';
    }

    toast.error(message);
    return { success: false, error: message };
  }
}
