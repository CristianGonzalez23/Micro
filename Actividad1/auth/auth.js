const http = require('http');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');

dotenv.config();

const SECRET_KEY = process.env.SECRET_KEY;

if (!SECRET_KEY) {
    console.error('SECRET_KEY no está definido en el archivo .env');
    process.exit(1);
}

const server = http.createServer((req, res) => {
    if (req.url === '/login' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                const { usuario, clave } = JSON.parse(body);
                console.log('Recibido payload:', { usuario, clave }); // Log del payload recibido
                if (usuario && clave) {
                    const token = jwt.sign(
                        { usuario },
                        SECRET_KEY,
                        { expiresIn: '1h', issuer: 'ingesis.uniquindio.edu.co' }
                    );
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ token }));
                    console.log('Token generado:', token); // Log del token generado
                } else {
                    res.writeHead(400, { 'Content-Type': 'text/plain' });
                    res.end('Solicitud no valida: Los atributos usuario y clave son obligatorios');
                }
            } catch (error) {
                console.error('Error al parsear el JSON:', error); // Log del error
                res.writeHead(400, { 'Content-Type': 'text/plain' });
                res.end('Solicitud no valida: Error en el formato del JSON');
            }
        });
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

server.listen(3001, () => {
    console.log('Auth server running at http://localhost:3001/');
});