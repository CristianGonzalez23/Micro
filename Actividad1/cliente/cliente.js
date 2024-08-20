const axios = require('axios');
const crypto = require('crypto');
const dotenv = require('dotenv');

dotenv.config();

console.log("Client is running");

const authUrl = process.env.AUTH_URL;
const saludoUrl = process.env.GREETING_URL;

const usuario = crypto.randomBytes(8).toString('hex');
const clave = crypto.randomBytes(8).toString('hex');

async function obtenerToken() {
    try {
        const payload = { usuario, clave };
        console.log('Enviando payload:', payload); // Log del payload enviado
        const response = await axios.post(authUrl, payload, {
            headers: { 'Content-Type': 'application/json' }
        });
        console.log('Respuesta del servidor de autenticación:', response.data); // Log de la respuesta del servidor
        return response.data.token;
    } catch (error) {
        console.error('Error al obtener el token:', error.response ? error.response.data : error.message);
        process.exit(1);
    }
}

async function invocarSaludo(token) {
    try {
        const response = await axios.get(saludoUrl, {
            headers: { Authorization: `Bearer ${token}` },
            params: { nombre: usuario }
        });
        console.log('Respuesta del servidor de saludo:', response.data); // Log de la respuesta del servidor
    } catch (error) {
        console.error('Error al invocar el saludo:', error.response ? error.response.data : error.message);
    }
}

// Función autoejecutable que obtiene el token y luego invoca el saludo.
(async () => {
    const token = await obtenerToken();  // Obtiene el token de autenticación.
    await invocarSaludo(token);  // Invoca el saludo usando el token obtenido.
})();