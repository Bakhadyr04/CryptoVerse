# frontend/Dockerfile

FROM bitnami/node:18

# Создаем рабочую директорию
WORKDIR /app

# Копируем package.json и устанавливаем зависимости
COPY package.json package-lock.json* ./
RUN npm install --omit=dev

# Копируем остальной проект
COPY . .

# Открываем порт
EXPOSE 3000

# Команда запуска
CMD ["npm", "run", "dev"]
