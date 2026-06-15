import FileConverter from '@/components/FileConverter';
import { converters } from '@/lib/converters';

export default function AppPage() {
  const defaultConverter = converters[0];

  return (
    <FileConverter
      conversionType={defaultConverter.conversionType}
      inputFormat={defaultConverter.input}
      outputFormat={defaultConverter.output}
    />
  );
}
