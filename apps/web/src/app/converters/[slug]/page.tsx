import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import FileConverter from '@/components/FileConverter';
import ConverterContent from '@/components/ConverterContent';
import ConverterNavigation from '@/components/ConverterNavigation';
import { converters, getCanonicalUrl, getConverter } from '@/lib/converters';

type Props = {
  params: Promise<{
    slug: string;
  }>;
};

export function generateStaticParams() {
  return converters.map(converter => ({
    slug: converter.slug,
  }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const converter = getConverter(slug);

  if (!converter) {
    return {
      title: 'Converter not found',
      robots: {
        index: false,
        follow: false,
      },
    };
  }

  const url = getCanonicalUrl(`/converters/${converter.slug}`);

  return {
    title: converter.title,
    description: converter.description,
    alternates: {
      canonical: url,
    },
    openGraph: {
      title: converter.title,
      description: converter.description,
      url,
      siteName: 'Doc Flow',
      type: 'website',
    },
    twitter: {
      card: 'summary',
      title: converter.title,
      description: converter.description,
    },
  };
}

export default async function ConverterPage({ params }: Props) {
  const { slug } = await params;
  const converter = getConverter(slug);

  if (!converter) {
    notFound();
  }

  return (
    <>
      <ConverterContent converter={converter} />

      <FileConverter
        conversionType={converter.conversionType}
        inputFormat={converter.input}
        outputFormat={converter.output}
      />

      <ConverterNavigation currentSlug={converter.slug} />
    </>
  );
}
