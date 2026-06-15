import Link from 'next/link';
import { converters } from '@/lib/converters';

type Props = {
  currentSlug: string;
};

export default function ConverterNavigation({ currentSlug }: Props) {
  return (
    <nav
      aria-label="Related converters"
      className="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8"
    >
      <h2 className="text-2xl font-semibold">Related converters</h2>
      <ul className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {converters.map(converter => {
          const isCurrent = converter.slug === currentSlug;

          return (
            <li key={converter.slug}>
              {isCurrent ? (
                <span
                  aria-current="page"
                  className="block rounded-lg border bg-muted px-4 py-3 font-medium"
                >
                  ✓ {converter.title}
                </span>
              ) : (
                <Link
                  href={`/converters/${converter.slug}`}
                  className="block rounded-lg border px-4 py-3 font-medium transition-colors hover:bg-muted"
                >
                  {converter.title}
                </Link>
              )}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
