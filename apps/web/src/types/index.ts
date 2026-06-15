const conversionTypes = [
  'csv_to_json',
  'csv_to_xlsx',
  'xlsx_to_csv',
  'txt_to_pdf',
  'pdf_to_text',
  'docx_to_pdf',
  'docx_to_markdown',
  'markdown_to_pdf',
] as const;

export type ConversionType = (typeof conversionTypes)[number];

export type ProcessedFile = {
  filename: string;
  extension: string | null;
  size_bytes: number;
  size_mb: number;
  modified_at: string;
  download_url: string;
};

export type Converter = {
  slug: string;
  conversionType: ConversionType;
  title: string;
  description: string;
  input: string;
  output: string;
  examples: string[];
  howItWorks: string[];
  faq: Array<{
    question: string;
    answer: string;
  }>;
};
