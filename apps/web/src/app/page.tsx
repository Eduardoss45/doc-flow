'use client';

import { useState } from 'react';

import { useFileConversion, type ConversionType } from '@/hooks/useFileConversion';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload, FileDown, Loader2, AlertCircle, X, Menu, Clock } from 'lucide-react';
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
    resultUrl,
    handleFileChange,
    convert,
    labels,
  } = useFileConversion();

  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const hasValidConversion = availableConversions.length > 0;
  const canConvert = !!file && hasValidConversion && !loading;

  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 flex">
      {/* Área principal - ocupa toda a tela quando sidebar fechada */}
      <div
        className={cn(
          'flex-1 flex items-center justify-center p-4 transition-all duration-300',
          isSidebarOpen ? 'mr-0 lg:mr-80' : 'mr-0'
        )}
      >
        <Card className="w-full max-w-lg">
          <CardHeader className="relative">
            <CardTitle className="text-2xl">Conversor de Arquivos</CardTitle>
            <CardDescription>Selecione o arquivo e o tipo de conversão desejado</CardDescription>

            {/* Botão para abrir sidebar */}
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-4 top-4 lg:hidden"
              onClick={() => setIsSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>
          </CardHeader>

          <CardContent className="space-y-6">
            {/* Upload area */}
            <div className="flex flex-col items-center justify-center border-2 border-dashed border-zinc-300 dark:border-zinc-700 rounded-xl p-10 transition hover:border-primary/50">
              <input type="file" id="file-upload" className="hidden" onChange={handleFileChange} />
              <label
                htmlFor="file-upload"
                className={cn(
                  'cursor-pointer flex flex-col items-center gap-3',
                  file ? 'text-primary' : 'text-muted-foreground'
                )}
              >
                <Upload className="h-10 w-10" />
                <div className="text-center">
                  <p className="font-medium">
                    {file ? file.name : 'Clique ou arraste um arquivo aqui'}
                  </p>
                  <p className="text-sm">
                    {file
                      ? `${(file.size / 1024 / 1024).toFixed(2)} MB • ${fileExtension?.toUpperCase()}`
                      : 'Formatos suportados: csv, xlsx, txt, pdf, docx'}
                  </p>
                </div>
              </label>
            </div>

            {/* Tipo de conversão */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Tipo de conversão</label>

              {hasValidConversion ? (
                <Select
                  value={conversionType}
                  onValueChange={v => setConversionType(v as ConversionType)}
                  disabled={loading || !file}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Escolha a conversão" />
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
                <div className="flex items-center gap-2 rounded-md border border-destructive/50 bg-destructive/5 px-3 py-2 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4" />
                  {fileExtension
                    ? `Não há conversões disponíveis para .${fileExtension}`
                    : 'Selecione um arquivo para ver as opções'}
                </div>
              )}
            </div>

            <Button
              onClick={convert}
              disabled={!canConvert}
              className="w-full h-12 text-base gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Convertendo...
                </>
              ) : (
                <>
                  <FileDown className="h-5 w-5" />
                  Converter arquivo
                </>
              )}
            </Button>

            {error && (
              <div className="rounded-lg bg-destructive/10 p-4 text-destructive text-sm">
                {error}
              </div>
            )}

            {resultUrl && (
              <div className="rounded-lg border bg-muted/40 p-4">
                <p className="text-sm font-medium mb-2">Arquivo convertido com sucesso!</p>
                <Button asChild variant="outline" className="w-full">
                  <a href={resultUrl} download target="_blank" rel="noopener noreferrer">
                    Baixar arquivo convertido
                  </a>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Sidebar direita - desliza da direita */}
      <div
        className={cn(
          'fixed inset-y-0 right-0 z-50 w-full max-w-xs sm:max-w-sm lg:max-w-md bg-white dark:bg-zinc-900 border-l border-zinc-200 dark:border-zinc-800 transform transition-transform duration-300 ease-in-out shadow-2xl',
          isSidebarOpen ? 'translate-x-0' : 'translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Cabeçalho da sidebar */}
          <div className="p-5 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Arquivos Processados</h2>
            <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(false)}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Conteúdo principal da sidebar */}
          <div className="flex-1 p-5 overflow-y-auto">
            {/* Aviso de expiração */}
            <div className="flex items-start gap-3 rounded-lg bg-amber-50 dark:bg-amber-950/40 p-4 mb-6 text-sm text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800/50">
              <Clock className="h-5 w-5 mt-0.5 shrink-0" />
              <p>
                Os arquivos convertidos ficam disponíveis por <strong>24 horas</strong>. Após esse
                período, eles são removidos automaticamente.
              </p>
            </div>

            {/* Aqui virá a lista de arquivos no futuro */}
            <div className="text-center text-muted-foreground py-10">
              <p className="mb-2">Nenhum arquivo processado ainda</p>
              <p className="text-sm">Faça uma conversão para ver os arquivos aqui</p>
            </div>

            {/* Placeholder para quando tiver itens */}
            {/* 
            <div className="space-y-3">
              {processedFiles.map(file => (
                <div key={file.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                  <div>
                    <p className="font-medium truncate max-w-[180px]">{file.name}</p>
                    <p className="text-xs text-muted-foreground">{file.date} • {file.size}</p>
                  </div>
                  <Button variant="ghost" size="icon">
                    <FileDown className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
            */}
          </div>

          {/* Rodapé opcional */}
          <div className="p-4 border-t border-zinc-200 dark:border-zinc-800 text-xs text-muted-foreground text-center">
            Arquivos são armazenados temporariamente
          </div>
        </div>
      </div>

      {/* Overlay escuro quando sidebar aberta em mobile */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}
    </div>
  );
}
