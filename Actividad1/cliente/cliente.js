const axios = require('axios');
const crypto = require('crypto');

// Your client code here
console.log("Client is running");

const authUrl = process.env.AUTH_URL;
const saludoUrl = process.env.SALUDO_URL;

const usuario = crypto.randomBytes(8).toString('hex');
const clave = crypto.randomBytes(8).toString('hex');

async function obtenerToken() {
    try {
        const response = await axios.post(authUrl, { usuario, clave });
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
        console.log('Respuesta del servidor:', response.data);
    } catch (error) {
        console.error('Error al invocar el saludo:', error.response ? error.response.data : error.message);
    }
}

(async () => {
    const token = await obtenerToken();
    await invocarSaludo(token);
})();