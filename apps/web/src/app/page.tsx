'use client';

import { useState } from 'react';
import {
  useFileConversion,
  type ConversionType,
  type ProcessedFile,
} from '@/hooks/useFileConversion';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Upload,
  FileDown,
  Loader2,
  AlertCircle,
  X,
  Menu,
  Clock,
  ChevronLeft,
  ChevronRight,
  Download,
  FileText,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function FileConverter() {
  const {
    file,
    fileExtension,
    conversionType,
    setConversionType,
    availableConversions,
    loading,
    error,
    handleFileChange,
    convert,
    labels,
    processedFiles,
    historyLoading,
    historyError,
    refreshHistory,
  } = useFileConversion();

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const hasValidConversion = availableConversions.length > 0;
  const canConvert = !!file && hasValidConversion && !loading;

  const getDisplayFilename = (filename: string) => {
    const match = filename.match(
      /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}_(.+)$/
    );
    return match?.[1] ?? filename;
  };

  const formatModifiedAt = (modifiedAt: string) => {
    const date = new Date(modifiedAt);
    if (Number.isNaN(date.getTime())) return 'Data indisponivel';
    return date.toLocaleString('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    });
  };

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 flex">
      <div
        className={cn(
          'flex-1 flex items-center justify-center p-4 sm:p-6 transition-all duration-300 ease-in-out',
          'lg:pr-0',
          !isCollapsed && 'lg:mr-80 2xl:mr-96',
          isCollapsed && 'lg:mr-20'
        )}
      >
        <Card className="w-full max-w-2xl xl:max-w-3xl shadow-lg">
          <CardHeader className="relative pb-6">
            <CardTitle className="text-2xl sm:text-3xl">Conversor de Arquivos</CardTitle>
            <CardDescription className="text-base">
              Selecione o arquivo e o formato de destino desejado
            </CardDescription>

            <Button
              variant="ghost"
              size="icon"
              className="absolute right-4 top-4 lg:hidden"
              onClick={() => setIsSidebarOpen(true)}
            >
              <Menu className="h-6 w-6" />
            </Button>
          </CardHeader>

          <CardContent className="space-y-8 pt-2">
            <div
              className={cn(
                'flex flex-col items-center justify-center border-2 border-dashed rounded-xl p-10 sm:p-16 transition-colors duration-200',
                file
                  ? 'border-primary/60 bg-primary/5'
                  : 'border-zinc-300 dark:border-zinc-700 hover:border-primary/50'
              )}
            >
              <input type="file" id="file-upload" className="hidden" onChange={handleFileChange} />
              <label
                htmlFor="file-upload"
                className={cn(
                  'cursor-pointer flex flex-col items-center gap-4 text-center',
                  file ? 'text-primary' : 'text-muted-foreground'
                )}
              >
                <Upload className="h-12 w-12 sm:h-14 sm:w-14" />
                <div>
                  <p className="font-medium text-lg">
                    {file ? file.name : 'Clique ou arraste um arquivo aqui'}
                  </p>
                  <p className="text-sm mt-1">
                    {file
                      ? `${(file.size / 1024 / 1024).toFixed(2)} MB • ${fileExtension?.toUpperCase()}`
                      : 'Formatos suportados: CSV, XLSX, TXT, PDF, DOCX e mais'}
                  </p>
                </div>
              </label>
            </div>

            <div className="space-y-3">
              <label className="text-sm font-medium block">Formato de saída</label>

              {hasValidConversion ? (
                <Select
                  value={conversionType}
                  onValueChange={v => setConversionType(v as ConversionType)}
                  disabled={loading || !file}
                >
                  <SelectTrigger className="h-12">
                    <SelectValue placeholder="Selecione o formato desejado" />
                  </SelectTrigger>
                  <SelectContent>
                    {availableConversions.map(key => (
                      <SelectItem key={key} value={key}>
                        {labels[key]}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              ) : (
                <div className="flex items-center gap-3 rounded-lg border border-destructive/40 bg-destructive/5 px-4 py-3 text-sm text-destructive">
                  <AlertCircle className="h-5 w-5 shrink-0" />
                  {fileExtension
                    ? `Não há conversões disponíveis para arquivos .${fileExtension}`
                    : 'Selecione um arquivo para ver as opções disponíveis'}
                </div>
              )}
            </div>

            <Button
              onClick={convert}
              disabled={!canConvert}
              className="w-full h-14 text-lg font-medium gap-2.5"
            >
              {loading ? (
                <>
                  <Loader2 className="h-6 w-6 animate-spin" />
                  Convertendo...
                </>
              ) : (
                <>
                  <FileDown className="h-6 w-6" />
                  Converter Agora
                </>
              )}
            </Button>

            {error && (
              <div className="rounded-lg bg-destructive/10 p-4 text-destructive text-sm border border-destructive/20">
                {error}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <aside
        className={cn(
          'bg-white dark:bg-zinc-900 border-l border-zinc-200 dark:border-zinc-800',
          'transition-all duration-300 ease-in-out flex flex-col h-screen overflow-hidden',
          'fixed inset-y-0 right-0 z-50 w-80 sm:w-96 translate-x-full lg:translate-x-0',
          isSidebarOpen && 'translate-x-0',
          'lg:relative lg:z-auto lg:shadow-none',
          isCollapsed ? 'lg:w-20' : 'lg:w-80 2xl:w-96'
        )}
      >
        <div className="flex items-center justify-between p-5 border-b border-zinc-200 dark:border-zinc-800">
          {!isCollapsed && (
            <h2 className="text-lg font-semibold tracking-tight">Histórico de Conversões</h2>
          )}

          <div className="flex items-center gap-1">
            {!isCollapsed && !historyLoading && (
              <Button variant="ghost" size="icon" onClick={refreshHistory} title="Atualizar">
                <Loader2 className={cn('h-4 w-4', historyLoading && 'animate-spin')} />
              </Button>
            )}

            <Button
              variant="ghost"
              size="icon"
              className="hidden lg:flex"
              onClick={() => setIsCollapsed(!isCollapsed)}
            >
              {isCollapsed ? (
                <ChevronRight className="h-5 w-5" />
              ) : (
                <ChevronLeft className="h-5 w-5" />
              )}
            </Button>

            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setIsSidebarOpen(false)}
            >
              <X className="h-6 w-6" />
            </Button>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-5">
          {historyLoading ? (
            <div className="flex justify-center items-center h-32">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : historyError ? (
            <div className="text-center text-destructive py-8 text-sm px-4">
              {historyError}
              <Button variant="outline" size="sm" className="mt-4" onClick={refreshHistory}>
                Tentar novamente
              </Button>
            </div>
          ) : !isCollapsed ? (
            <>
              <div className="flex items-start gap-3 rounded-lg bg-amber-50/70 dark:bg-amber-950/30 p-4 mb-6 text-sm text-amber-800 dark:text-amber-300 border border-amber-200/60 dark:border-amber-800/40">
                <Clock className="h-5 w-5 mt-0.5 shrink-0" />
                <p>
                  Arquivos disponíveis por <strong>24 horas</strong>. Após isso são excluídos
                  automaticamente.
                </p>
              </div>

              {processedFiles.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <p className="font-medium mb-2">Nenhuma conversão recente</p>
                  <p className="text-sm">Seus arquivos convertidos aparecerão aqui</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {processedFiles.map((file: ProcessedFile) => (
                    <div
                      key={file.filename}
                      className="flex items-center justify-between p-3 bg-muted/50 dark:bg-muted/30 rounded-lg hover:bg-muted/70 transition-colors group"
                    >
                      <div className="flex items-center gap-3 min-w-0">
                        <FileText className="h-5 w-5 text-primary shrink-0" />
                        <div className="min-w-0">
                          <p className="font-medium truncate max-w-[220px]">
                            {getDisplayFilename(file.filename)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {file.size_mb.toFixed(2)} MB - {formatModifiedAt(file.modified_at)}
                          </p>
                        </div>
                      </div>

                      <Button
                        variant="ghost"
                        size="icon"
                        className="opacity-70 hover:opacity-100"
                        asChild
                      >
                        <a
                          href={file.download_url}
                          download
                          target="_blank"
                          rel="noopener noreferrer"
                          title="Baixar arquivo"
                        >
                          <Download className="h-4 w-4" />
                        </a>
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center pt-10 text-muted-foreground/70">
              <Clock className="h-8 w-8 mb-3 opacity-60" />
              <p className="text-xs font-medium">Histórico</p>
            </div>
          )}
        </div>

        <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 text-xs text-muted-foreground text-center">
          {!isCollapsed && 'Armazenamento temporário • 24h'}
        </div>
      </aside>

      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </div>
  );
}
