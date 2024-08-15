const axios = require('axios');  // Importa la librería axios para hacer peticiones HTTP.
const crypto = require('crypto');  // Importa la librería crypto para generar datos aleatorios.

// Mensaje de inicio del cliente.
console.log("Client is running");

// Obtiene las URLs de autenticación y saludo desde las variables de entorno.
const authUrl = process.env.AUTH_URL;
const saludoUrl = process.env.SALUDO_URL;

// Genera un usuario y una clave aleatorios usando la librería crypto.
const usuario = crypto.randomBytes(8).toString('hex');
const clave = crypto.randomBytes(8).toString('hex');

// Función asíncrona para obtener un token de autenticación.
async function obtenerToken() {
    try {
        // Hace una petición POST a la URL de autenticación con el usuario y la clave.
        const response = await axios.post(authUrl, { usuario, clave });
        // Retorna el token recibido en la respuesta.
        return response.data.token;
    } catch (error) {
        // Maneja errores en la petición y muestra un mensaje de error.
        console.error('Error al obtener el token:', error.response ? error.response.data : error.message);
        // Termina el proceso con un código de error.
        process.exit(1);
    }
}

// Función asíncrona para invocar el saludo usando el token de autenticación.
async function invocarSaludo(token) {
    try {
        // Hace una petición GET a la URL de saludo con el token de autenticación en los headers y el nombre del usuario en los parámetros.
        const response = await axios.get(saludoUrl, {
            headers: { Authorization: `Bearer ${token}` },
            params: { nombre: usuario }
        });
        // Muestra la respuesta del servidor.
        console.log('Respuesta del servidor:', response.data);
    } catch (error) {
        // Maneja errores en la petición y muestra un mensaje de error.
        console.error('Error al invocar el saludo:', error.response ? error.response.data : error.message);
    }
}

// Función autoejecutable que obtiene el token y luego invoca el saludo.
(async () => {
    const token = await obtenerToken();  // Obtiene el token de autenticación.
    await invocarSaludo(token);  // Invoca el saludo usando el token obtenido.
})();