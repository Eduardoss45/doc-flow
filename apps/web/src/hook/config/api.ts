import axios, { AxiosError } from 'axios';
import { useCallback } from 'react';
const url = process.env.NEXT_API_URL || '';

const api = axios.create({
  baseURL: url + '/api',
  timeout: 3600,
});

type ApiResponse<T = any> = {
  success: boolean;
  data?: T;
  error?: string;
};

export function useApi() {
  const postForm = useCallback(
    async <T>(endpoint: string, formData: FormData): Promise<ApiResponse<T>> => {
      try {
        const response = await api.post<ApiResponse<T>>(endpoint, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        return response.data;
      } catch (err) {
        const error = err as AxiosError<ApiResponse>;
        return {
          success: false,
          error: error.response?.data?.error || error.message || 'Erro desconhecido',
        };
      }
    },
    []
  );

  return { postForm };
}
