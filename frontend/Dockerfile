# Frontend Dockerfile for Expo
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install system dependencies needed by Expo
RUN apk add --no-cache git bash curl python3 make g++

# Copy package files first for caching
COPY package*.json ./

# Install global Expo CLI
RUN npm install -g expo-cli

# Install local project dependencies
RUN npm install

# Copy the rest of the project
COPY . /app

# Expose default Expo ports
EXPOSE 19000 19001 19002 19006 8081

# Start Expo in LAN mode (reliable in Docker)
CMD ["npx", "expo", "start"]