# Usa una imagen base oficial de Node.js
FROM node:14

# Configura el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos package.json y package-lock.json al contenedor
COPY package*.json ./


# Instala las dependencias del proyecto
RUN npm install

# Copia el resto del código fuente al contenedor
COPY . .

# Expone el puerto en el que la aplicación estará escuchando
EXPOSE 3000

# Define el comando por defecto para ejecutar la aplicación
CMD ["npm", "start"]