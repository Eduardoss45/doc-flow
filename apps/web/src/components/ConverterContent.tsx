import { Converter } from '@/types';

type ConverterContentProps = {
  converter: Converter;
};

export default function ConverterContent({ converter }: ConverterContentProps) {
  const faqJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: converter.faq.map(item => ({
      '@type': 'Question',
      name: item.question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: item.answer,
      },
    })),
  };

  return (
    <main className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
      <section className="space-y-4">
        <p className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
          Online file converter
        </p>
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">{converter.title}</h1>
        <p className="max-w-3xl text-lg text-muted-foreground">{converter.description}</p>
      </section>

      <section className="mt-10 grid gap-8 md:grid-cols-2">
        <div>
          <h2 className="text-2xl font-semibold">Examples</h2>
          <ul className="mt-4 space-y-3 text-muted-foreground">
            {converter.examples.map(example => (
              <li key={example}>{example}</li>
            ))}
          </ul>
        </div>

        <div>
          <h2 className="text-2xl font-semibold">How it works</h2>
          <ol className="mt-4 list-decimal space-y-3 pl-5 text-muted-foreground">
            {converter.howItWorks.map(step => (
              <li key={step}>{step}</li>
            ))}
          </ol>
        </div>
      </section>

      <section className="mt-10">
        <h2 className="text-2xl font-semibold">FAQ</h2>
        <div className="mt-4 space-y-5">
          {converter.faq.map(item => (
            <article key={item.question}>
              <h3 className="font-semibold">{item.question}</h3>
              <p className="mt-2 text-muted-foreground">{item.answer}</p>
            </article>
          ))}
        </div>
      </section>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(faqJsonLd),
        }}
      />
    </main>
  );
}
