FROM node:20-alpine

WORKDIR /app

# System deps (Expo sometimes needs these)
RUN apk add --no-cache git bash curl python3 make g++

# Copy package files first (better caching)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy rest of project
COPY . .

# Expose Expo ports
EXPOSE 19000 19001 19002 19006 8081

# Use modern Expo CLI (local)
CMD ["npx", "expo", "start", "--tunnel"]