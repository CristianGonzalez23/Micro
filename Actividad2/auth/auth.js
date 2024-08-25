const http = require('http');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');
const express = require('express');
const userRoutes = require('../usuarios/usuarios'); // Importa las rutas de usuarios

dotenv.config();

const SECRET_KEY = process.env.SECRET_KEY;

if (!SECRET_KEY) {
    console.error('SECRET_KEY no está definido en el archivo .env');
    process.exit(1);
}

const app = express();
app.use(express.json()); // Middleware to parse JSON bodies

app.post('/login', (req, res) => {
    const { usuario, clave } = req.body;
    console.log('Recibido payload:', { usuario, clave }); // Log del payload recibido
    if (usuario && clave) {
        const token = jwt.sign(
            { usuario },
            SECRET_KEY,
            { expiresIn: '1h', issuer: 'ingesis.uniquindio.edu.co' }
        );
        res.status(200).json({ token });
        console.log('Token generado:', token); // Log del token generado
    } else {
        res.status(400).send('Solicitud no valida: Los atributos usuario y clave son obligatorios');
    }
});

app.use('/api', userRoutes); // Usa las rutas de usuarios

app.use((req, res) => {
    res.status(404).send('Not Found');
});

const server = http.createServer(app);

server.listen(3001, () => {
    console.log('Auth server running at http://localhost:3001/');
});