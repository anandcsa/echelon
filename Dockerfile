FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY index.html src.js world.js neon-city.js districts.js campaign.js director-client.js controls.js npcs.js open-city.js vehicles.js style.css ./
COPY shared ./shared
COPY public ./public
RUN npm run build
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production PORT=8080
COPY --from=build /app/dist ./dist
COPY server ./server
COPY shared ./shared
COPY campaign.js ./campaign.js
COPY package.json ./package.json
USER node
EXPOSE 8080
CMD ["node","server/main.mjs"]
