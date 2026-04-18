FROM node:22-alpine
ENV NODE_ENV=production
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install --registry=https://registry.npmmirror.com --silent
COPY . .
RUN npm run build
EXPOSE 4173
RUN chown -R node /usr/src/app
USER node
CMD ["npm", "run", "preview"]
