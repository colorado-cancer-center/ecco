FROM node:22
RUN npm install -g bun@1.0.35

WORKDIR /app

COPY package.json bun.lock  ./

RUN bun install

COPY . .
