FROM node:20-alpine

WORKDIR /app

# Installer dépendances
COPY package*.json ./
RUN npm install

# Copier code
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"]