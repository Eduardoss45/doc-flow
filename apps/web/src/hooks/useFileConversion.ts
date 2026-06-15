import { useState, useCallback, useMemo, useEffect } from 'react';
import { convertFile } from '@/services/conversion';
import { toast } from 'sonner';
import { api } from '@/infra/api';
import { ensureClientId } from '@/services/auth';
import { ConversionType, ProcessedFile } from '@/types';

const CONVERSION_LABELS: Record<ConversionType, string> = {
  csv_to_json: 'CSV → JSON',
  csv_to_xlsx: 'CSV → Excel (.xlsx)',
  xlsx_to_csv: 'Excel → CSV',
  txt_to_pdf: 'Texto → PDF',
  pdf_to_text: 'PDF → Texto',
  docx_to_pdf: 'Word → PDF',
  docx_to_markdown: 'Word → Markdown',
  markdown_to_pdf: 'Markdown → PDF',
};

const INPUT_BY_CONVERSION: Record<ConversionType, string> = {
  csv_to_json: 'csv',
  csv_to_xlsx: 'csv',
  xlsx_to_csv: 'xlsx',
  txt_to_pdf: 'txt',
  pdf_to_text: 'pdf',
  docx_to_pdf: 'docx',
  docx_to_markdown: 'docx',
  markdown_to_pdf: 'md',
};

export function useFileConversion(conversionType: ConversionType) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processedFiles, setProcessedFiles] = useState<ProcessedFile[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);

  const fileExtension = useMemo(() => {
    if (!file?.name) return null;
    return file.name.split('.').pop()?.toLowerCase() ?? null;
  }, [file]);

  const isValidFile = useMemo(() => {
    if (!fileExtension) return false;

    return INPUT_BY_CONVERSION[conversionType] === fileExtension;
  }, [fileExtension, conversionType]);

  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    setHistoryError(null);
    try {
      const clientId = await ensureClientId();
      if (!clientId) {
        setProcessedFiles([]);
        setHistoryError('Não foi possível iniciar sua sessão');
        return;
      }

      const res = await api.get('/documents/files');
      if (res.data?.files && Array.isArray(res.data.files)) {
        setProcessedFiles(res.data.files);
      } else {
        setProcessedFiles([]);
      }
    } catch (err) {
      console.error('Erro ao carregar histórico:', err);
      setHistoryError('Não foi possível carregar o histórico de conversões');
      setProcessedFiles([]);
    } finally {
      setHistoryLoading(false);
    }
  }, []);
  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  useEffect(() => {
    const handleConversionCompleted = () => {
      fetchHistory();
    };

    window.addEventListener('conversion:completed', handleConversionCompleted);
    return () => {
      window.removeEventListener('conversion:completed', handleConversionCompleted);
    };
  }, [fetchHistory]);

  useEffect(() => {
    if (!loading && !error && processedFiles.length > 0) {
      const timer = setTimeout(fetchHistory, 1800);
      return () => clearTimeout(timer);
    }
  }, [loading, error, processedFiles.length, fetchHistory]);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (selected) setFile(selected);
  }, []);

  const convert = useCallback(async () => {
    if (!file) {
      setError('Selecione um arquivo primeiro');
      return;
    }

    if (!isValidFile) {
      setError(`Esta página aceita apenas arquivos .${INPUT_BY_CONVERSION[conversionType]}`);
      return;
    }

    setLoading(true);
    setError(null);
    setResultUrl(null);

    const response = await convertFile(file, conversionType);

    if (response.success && response.jobId) {
      toast.success('Processamento iniciado! Aguarde o resultado.');
    } else {
      setError(response.error ?? 'Falha na conversão');
    }

    setLoading(false);
  }, [file, conversionType, isValidFile]);

  return {
    file,
    fileExtension,
    loading,
    isValidFile,
    error,
    resultUrl,
    handleFileChange,
    convert,
    processedFiles,
    historyLoading,
    historyError,
    refreshHistory: fetchHistory,
  };
}
