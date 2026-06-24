# 📌 Doc Flow – Motor Assíncrono de Conversão de Documentos

O **Doc Flow** é um sistema SaaS de **processamento e conversão assíncrona de documentos**, estruturado como um backend orientado a mensageria, com comunicação desacoplada entre API e workers, processamento distribuído e notificações em tempo real via WebSocket.

O projeto mantém seu objetivo original de fornecer um motor técnico de conversão previsível e observável, agora evoluído com uma camada SaaS e novos recursos de renderização avançada.

O foco do projeto é demonstrar:

* Separação rigorosa de responsabilidades
* Processamento assíncrono correto
* Isolamento por cliente sem autenticação
* Controle explícito de recursos
* Efemeridade como regra arquitetural
* Pipeline seguro de conversão
* Preparação para operação em produção

O sistema não é uma plataforma de gestão documental.

É um **motor SaaS de conversão de documentos com processamento assíncrono, isolamento de recursos e execução controlada**.

---

# 🔄 Evolução do Pipeline de Conversão

O sistema mantém todos os pipelines de conversão existentes, incluindo:

* CSV ↔ Excel ↔ JSON
* Markdown ↔ HTML ↔ TXT
* TXT → PDF
* PDF → TXT
* DOCX / PPTX → PDF / Markdown

Como evolução do projeto, foi adicionado um novo pipeline especializado para:

## Markdown → PDF

Utilizando **Chromium como engine de renderização**, permitindo maior fidelidade visual através de uma etapa intermediária baseada em HTML.

Fluxo:

```
Markdown
   │
   ▼
Conversão para HTML
   │
   ▼
Renderização Chromium
   │
   ▼
PDF final
```

Esse novo pipeline permite:

* Suporte a CSS moderno
* Melhor controle de layout
* Renderização semelhante a navegadores reais
* Maior qualidade visual dos documentos gerados

---

# 🔐 Proteções do Pipeline Chromium

A renderização utilizando Chromium adiciona uma camada de processamento mais pesada, por isso foi implementado isolamento e controle para evitar impacto no restante da aplicação.

Proteções:

* Execução isolada do processo
* Controle de tempo de execução
* Limitação de recursos
* Validação de entrada
* Separação entre API e processamento pesado

O objetivo é manter a previsibilidade operacional mesmo com tarefas de maior custo computacional.

---

# 🌐 Evolução do Frontend

O frontend foi otimizado para suportar o crescimento como SaaS, mantendo as funcionalidades existentes e adicionando melhorias de aquisição e monetização.

Melhorias:

## SEO

* Melhor estrutura de páginas
* Otimização de metadata
* Melhor indexação
* Melhor desempenho de carregamento

## Monetização

Preparação da interface para utilização de anúncios:

* Espaços publicitários
* Estrutura compatível com monetização
* Preservação da experiência do usuário

---

# 🐳 Próximos Passos

## Otimização dos Builds Docker

Antes do deploy produtivo, será realizada a otimização das imagens Docker.

Objetivos:

* Reduzir tamanho das imagens
* Melhorar tempo de build
* Diminuir tempo de deploy
* Remover dependências desnecessárias
* Melhor separar responsabilidades dos containers

Possíveis melhorias:

* Multi-stage builds
* Imagens base menores
* Separação runtime/build
* Cache eficiente de camadas
* Containers específicos para serviços pesados

---

# 🚀 Deploy em Produção

Após a otimização dos builds:

* Publicação da aplicação
* Configuração do ambiente produtivo
* Validação do pipeline completo
* Monitoramento inicial
* Ajustes operacionais
