FROM node:24-alpine

WORKDIR /app

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml ./
COPY prisma ./prisma

RUN pnpm install && \
	npx prisma generate

COPY . .
COPY tsconfig.json prisma.config.ts ./

RUN pnpm build

EXPOSE 3000

CMD ["sh", "-c", "npx prisma db push && pnpm start"]