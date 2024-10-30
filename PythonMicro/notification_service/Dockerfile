# Utiliza una imagen base de Python
FROM python:3.9

# Crea un directorio de trabajo
WORKDIR /app

# Copia los archivos de dependencias e instala
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia el resto de los archivos
COPY . .

# Expone el puerto para FastAPI
EXPOSE 5005

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5005"]
