import { useState, useCallback, useMemo, useEffect } from 'react';
import { useApi } from '@/hook/config/api';

export type ConversionType =
  | 'csv_to_json'
  | 'csv_to_xlsx'
  | 'xlsx_to_csv'
  | 'txt_to_pdf'
  | 'pdf_to_text'
  | 'docx_to_pdf'
  | 'docx_to_markdown';

const CONVERSION_LABELS: Record<ConversionType, string> = {
  csv_to_json: 'CSV → JSON',
  csv_to_xlsx: 'CSV → Excel (.xlsx)',
  xlsx_to_csv: 'Excel → CSV',
  txt_to_pdf: 'Texto → PDF',
  pdf_to_text: 'PDF → Texto',
  docx_to_pdf: 'Word → PDF',
  docx_to_markdown: 'Word → Markdown',
};

const CONVERSIONS_BY_INPUT: Record<string, ConversionType[]> = {
  csv: ['csv_to_json', 'csv_to_xlsx'],
  xlsx: ['xlsx_to_csv'],
  xls: ['xlsx_to_csv'],
  txt: ['txt_to_pdf'],
  pdf: ['pdf_to_text'],
  docx: ['docx_to_pdf', 'docx_to_markdown'],
};

const FALLBACK: ConversionType[] = [];

export function useFileConversion() {
  const { postForm } = useApi();

  const [file, setFile] = useState<File | null>(null);
  const [conversionType, setConversionType] = useState<ConversionType>('csv_to_json');
  const [loading, setLoading] = useState(false);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fileExtension = useMemo(() => {
    if (!file?.name) return null;
    const ext = file.name.split('.').pop()?.toLowerCase();
    return ext || null;
  }, [file]);

  const availableConversions = useMemo<ConversionType[]>(() => {
    if (!fileExtension) return FALLBACK;
    return CONVERSIONS_BY_INPUT[fileExtension] || FALLBACK;
  }, [fileExtension]);

  useEffect(() => {
    setResultUrl(null);
    setError(null);

    if (availableConversions.length === 0) {
      setConversionType('csv_to_json' as any);
    } else if (!availableConversions.includes(conversionType)) {
      setConversionType(availableConversions[0]);
    }
  }, [file, availableConversions, conversionType]);

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) return;

    setFile(selected);
  }, []);

  const convert = useCallback(async () => {
    if (!file) {
      setError('Selecione um arquivo primeiro');
      return;
    }
    if (!availableConversions.includes(conversionType)) {
      setError('Conversão não suportada para este tipo de arquivo');
      return;
    }

    setLoading(true);
    setError(null);
    setResultUrl(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('conversionType', conversionType);

    const response = await postForm<{ downloadUrl: string }>('/convert', formData);

    if (response.success && response.data?.downloadUrl) {
      setResultUrl(response.data.downloadUrl);
    } else {
      setError(response.error || 'Falha na conversão');
    }

    setLoading(false);
  }, [file, conversionType, availableConversions, postForm]);

  return {
    file,
    fileExtension,
    conversionType,
    setConversionType,
    availableConversions,
    loading,
    error,
    resultUrl,
    handleFileChange,
    convert,
    labels: CONVERSION_LABELS,
  };
}
