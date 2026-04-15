FROM node:22-alpine AS build

WORKDIR /app

COPY services/frontend/package.json services/frontend/package-lock.json ./
RUN npm ci

COPY services/frontend ./

ARG VITE_API_BASE_URL=
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

FROM caddy:2-alpine

COPY infra/docker/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/dist /srv

EXPOSE 80
