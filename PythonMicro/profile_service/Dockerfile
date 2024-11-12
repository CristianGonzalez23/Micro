# Usa una imagen base de Go
FROM golang:1.21-alpine

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Ejecuta go mod tidy para actualizar las dependencias
RUN go mod tidy

# Compila la aplicación
RUN go build -o main .

# Expone el puerto en el que la aplicación correrá
EXPOSE 8086

# Comando para correr la aplicación
CMD ["./main"]