FROM node:20-alpine AS builder
WORKDIR /app/apps/web

COPY apps/web/package.json apps/web/package-lock.json ./
RUN npm install --legacy-peer-deps

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

COPY apps/web .

WORKDIR /app/apps/web

RUN npm run build

FROM node:20-alpine
WORKDIR /app/apps/web

COPY --from=builder /app/apps/web/.next ./.next
COPY --from=builder /app/apps/web/public ./public
COPY --from=builder /app/apps/web/package.json ./package.json
COPY --from=builder /app/apps/web/node_modules ./node_modules

EXPOSE 3000