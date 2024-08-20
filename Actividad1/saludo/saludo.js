const http = require('http');
const url = require('url');
const jwt = require('jsonwebtoken');
const dotenv = require('dotenv');

dotenv.config();

const SECRET_KEY = process.env.SECRET_KEY;

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    const pathname = parsedUrl.pathname;
    const query = parsedUrl.query;

    if (pathname === '/saludo' && req.method === 'GET') {
        const authHeader = req.headers['authorization'];
        if (!authHeader) {
            res.writeHead(401, { 'Content-Type': 'text/plain' });
            res.end('Unauthorized: No token provided');
            return;
        }

        const token = authHeader.split(' ')[1];
        jwt.verify(token, SECRET_KEY, { issuer: 'ingesis.uniquindio.edu.co' }, (err, decoded) => {
            if (err) {
                res.writeHead(401, { 'Content-Type': 'text/plain' });
                res.end('Unauthorized: Invalid token');
                return;
            }

            console.log('Token decodificado:', decoded); // Log del token decodificado

            if (decoded.usuario !== query.nombre) {
                res.writeHead(403, { 'Content-Type': 'text/plain' });
                res.end('Forbidden: Token does not match the provided name');
                return;
            }

            res.writeHead(200, { 'Content-Type': 'text/plain' });
            res.end(`Hola ${query.nombre}`);
            console.log('Respuesta enviada: Hola', query.nombre); // Log de la respuesta enviada
        });
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

server.listen(3002, () => {
    console.log('Saludo server running at http://localhost:3002/');
});