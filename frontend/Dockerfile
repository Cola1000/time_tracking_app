FROM node:18-alpine as builder

ARG VITE_THEME=dark
ARG VITE_API_URL
ENV VITE_THEME=$VITE_THEME
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/dist ./dist

RUN npm install -g serve

EXPOSE 5173

CMD ["sh", "-c", "serve -s dist -l ${FRONTEND_PORT:-5173}"]
