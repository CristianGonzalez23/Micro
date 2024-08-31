const express = require('express');
const swaggerUi = require('swagger-ui-express');
const fs = require('fs');
const yaml = require('js-yaml');
const userRoutes = require('./routes/userRoutes');

const app = express();

// Cargar especificación OpenAPI desde archivo YAML
const swaggerDocument = yaml.load(fs.readFileSync('./openapi.yaml', 'utf8'));

app.use(express.json());

// Rutas de la API
app.use('/usuarios', userRoutes);

// Ruta de documentación con Swagger UI
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

module.exports = app;