import { Converter } from '@/types';

export const converters = [
  {
    slug: 'markdown-to-pdf',
    conversionType: 'markdown_to_pdf',
    title: 'Markdown to PDF',
    description:
      'Convert Markdown files into polished PDF documents with code blocks, tables, and clean print styling.',
    input: 'markdown',
    output: 'pdf',
    examples: [
      'Export technical notes, READMEs, and release docs as PDFs.',
      'Share Markdown reports with clients who need a fixed-layout document.',
      'Preserve code snippets and structured content in a printable format.',
    ],
    howItWorks: [
      'Upload a .md file from your workspace.',
      'Doc Flow parses the Markdown and sanitizes the generated HTML.',
      'The conversion worker renders a print-ready PDF asynchronously.',
      'Download the generated PDF while the temporary file is still available.',
    ],
    faq: [
      {
        question: 'Can I convert Markdown with code blocks?',
        answer: 'Yes. Markdown code blocks are highlighted and rendered into the final PDF.',
      },
      {
        question: 'Are remote images supported?',
        answer:
          'Remote images are downloaded only from allowed domains and converted into local render assets.',
      },
      {
        question: 'Is the conversion synchronous?',
        answer:
          'No. Files are processed asynchronously so larger jobs do not block the web request.',
      },
    ],
  },
  {
    slug: 'csv-to-json',
    conversionType: 'csv_to_json',
    title: 'CSV to JSON',
    description:
      'Convert CSV files into structured JSON for APIs, scripts, imports, and data workflows.',
    input: 'csv',
    output: 'json',
    examples: [
      'Transform spreadsheet exports into JSON payloads.',
      'Prepare CSV data for JavaScript applications and API imports.',
      'Convert tabular data into a developer-friendly structure.',
    ],
    howItWorks: [
      'Upload a CSV file.',
      'Doc Flow reads the tabular data and normalizes rows.',
      'The worker writes a JSON output file.',
      'Download the converted JSON from your temporary history.',
    ],
    faq: [
      {
        question: 'Does CSV to JSON keep headers?',
        answer: 'Yes. CSV headers are used as JSON object keys when available.',
      },
      {
        question: 'Can I convert large CSV files?',
        answer: 'Uploads are limited by the current storage and quota settings for your session.',
      },
      {
        question: 'Is this page indexable?',
        answer: 'Yes. Each converter page is statically generated for search engines.',
      },
    ],
  },
  {
    slug: 'csv-to-xlsx',
    conversionType: 'csv_to_xlsx',
    title: 'CSV to XLSX',
    description:
      'Convert CSV files into Excel-compatible XLSX spreadsheets for review, sharing, and analysis.',
    input: 'csv',
    output: 'xlsx',
    examples: [
      'Open CSV exports in Excel with a native workbook format.',
      'Prepare tabular data for business review.',
      'Share spreadsheet-ready files with non-technical teams.',
    ],
    howItWorks: [
      'Upload a CSV file.',
      'Doc Flow parses the rows and columns.',
      'The worker writes an XLSX workbook.',
      'Download the Excel file from your conversion history.',
    ],
    faq: [
      {
        question: 'Does it create a real XLSX file?',
        answer: 'Yes. The output is an Excel-compatible .xlsx file.',
      },
      {
        question: 'Can I use this for exported reports?',
        answer: 'Yes. It is designed for practical report and data export workflows.',
      },
      {
        question: 'Do I need an account?',
        answer: 'The current tool uses a temporary browser session for conversions.',
      },
    ],
  },
  {
    slug: 'xlsx-to-csv',
    conversionType: 'xlsx_to_csv',
    title: 'XLSX to CSV',
    description:
      'Convert Excel XLSX spreadsheets into portable CSV files for data pipelines and imports.',
    input: 'xlsx',
    output: 'csv',
    examples: [
      'Export Excel data into a plain-text CSV file.',
      'Prepare spreadsheets for database imports.',
      'Move data from workbook workflows into scripts and automations.',
    ],
    howItWorks: [
      'Upload an XLSX file.',
      'Doc Flow reads the workbook data.',
      'The worker exports the tabular content as CSV.',
      'Download the CSV result.',
    ],
    faq: [
      {
        question: 'What happens to formulas?',
        answer:
          'The converter focuses on exported tabular values rather than preserving workbook formulas.',
      },
      {
        question: 'Is CSV easier to import?',
        answer: 'Yes. CSV is widely supported by databases, scripts, and analytics tools.',
      },
      {
        question: 'Is the conversion stored permanently?',
        answer: 'No. Converted files are temporary by design.',
      },
    ],
  },
  {
    slug: 'pdf-to-text',
    conversionType: 'pdf_to_text',
    title: 'PDF to Text',
    description:
      'Extract readable text from PDF documents for search, analysis, summaries, and lightweight processing.',
    input: 'pdf',
    output: 'txt',
    examples: [
      'Extract text from contracts, reports, and invoices.',
      'Prepare PDF content for indexing or search.',
      'Convert readable PDFs into plain text files.',
    ],
    howItWorks: [
      'Upload a PDF document.',
      'Doc Flow extracts text using the conversion worker.',
      'The result is saved as a TXT file.',
      'Download the extracted text from your history.',
    ],
    faq: [
      {
        question: 'Does it perform OCR?',
        answer: 'Not yet. The current converter is focused on PDFs with extractable text.',
      },
      {
        question: 'Will formatting be preserved?',
        answer: 'The output is plain text, so layout and visual formatting are simplified.',
      },
      {
        question: 'Can I use it for search workflows?',
        answer: 'Yes. Text extraction is useful for search, indexing, and downstream processing.',
      },
    ],
  },
  {
    slug: 'docx-to-pdf',
    conversionType: 'docx_to_pdf',
    title: 'DOCX to PDF',
    description:
      'Convert Word DOCX documents into PDF files for sharing, archiving, and consistent viewing.',
    input: 'docx',
    output: 'pdf',
    examples: [
      'Export Word documents as PDFs.',
      'Share documents with stable formatting.',
      'Create archive-friendly copies of DOCX files.',
    ],
    howItWorks: [
      'Upload a DOCX document.',
      'The worker converts it using document conversion tooling.',
      'A PDF output is generated asynchronously.',
      'Download the finished PDF.',
    ],
    faq: [
      {
        question: 'Does DOCX to PDF preserve layout?',
        answer: 'It aims to preserve common document layout, fonts, and structure where supported.',
      },
      {
        question: 'Is it processed in the browser?',
        answer: 'No. The conversion runs in the backend worker.',
      },
      {
        question: 'Can I convert many documents at once?',
        answer:
          'Batch conversion is a future premium workflow, not part of the current public tool.',
      },
    ],
  },
  {
    slug: 'txt-to-pdf',
    conversionType: 'txt_to_pdf',
    title: 'TXT to PDF',
    description:
      'Convert plain text TXT files into PDF documents for sharing, printing, archiving, and distribution.',
    input: 'txt',
    output: 'pdf',
    examples: [
      'Convert notes and plain text documents into PDFs.',
      'Prepare TXT exports for printing and sharing.',
      'Archive text-based records in a fixed-layout format.',
    ],
    howItWorks: [
      'Upload a TXT file.',
      'Doc Flow reads the text content and prepares a document layout.',
      'The conversion worker generates a PDF output file.',
      'Download the generated PDF from your temporary history.',
    ],
    faq: [
      {
        question: 'Will the text formatting be preserved?',
        answer:
          'Basic text structure such as line breaks and paragraphs is preserved in the generated PDF.',
      },
      {
        question: 'Can I convert large text files?',
        answer: 'Supported file sizes depend on the current upload and processing limits.',
      },
      {
        question: 'Why convert TXT to PDF?',
        answer:
          'PDF files are easier to share, print, archive, and display consistently across devices.',
      },
    ],
  },
  {
    slug: 'docx-to-markdown',
    conversionType: 'docx_to_markdown',
    title: 'DOCX to Markdown',
    description:
      'Convert Microsoft Word DOCX documents into Markdown files for documentation, publishing, version control, and developer workflows.',
    input: 'docx',
    output: 'markdown',
    examples: [
      'Convert Word documents into Markdown for Git repositories.',
      'Prepare content for static site generators and documentation platforms.',
      'Transform business documents into developer-friendly text formats.',
    ],
    howItWorks: [
      'Upload a DOCX document.',
      'Doc Flow extracts the document structure and content.',
      'The conversion worker generates a Markdown file.',
      'Download the converted Markdown output.',
    ],
    faq: [
      {
        question: 'Does DOCX to Markdown preserve headings?',
        answer:
          'Yes. Common document structures such as headings, paragraphs, and lists are converted into Markdown equivalents.',
      },
      {
        question: 'Can I use the output in GitHub repositories?',
        answer:
          'Yes. The generated Markdown is suitable for documentation, READMEs, and developer workflows.',
      },
      {
        question: 'Are images included in the Markdown output?',
        answer:
          'Image handling depends on the conversion capabilities and configuration of the processing engine.',
      },
    ],
  },
] satisfies Converter[];

export type ConverterSlug = (typeof converters)[number]['slug'];

export function getConverter(slug: string) {
  return converters.find(c => c.slug === slug);
}

export function getCanonicalUrl(path = '') {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000';
  return new URL(path, siteUrl).toString();
}
