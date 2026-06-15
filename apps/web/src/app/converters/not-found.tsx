import Link from 'next/link';

export default function NotFound() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
      <h1 className="text-4xl font-bold tracking-tight">Converter not found</h1>
      <p className="mt-4 text-muted-foreground">
        The converter you are looking for does not exist or is not available yet.
      </p>
      <Link href="/converters/csv-to-json" className="mt-6 inline-block font-medium underline">
        View available converters
      </Link>
    </main>
  );
}
