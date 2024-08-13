const http = require('http');
const url = require('url');
const jwt = require('jsonwebtoken');

const SECRET_KEY = 'your_secret_key';

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

            if (decoded.usuario !== query.nombre) {
                res.writeHead(403, { 'Content-Type': 'text/plain' });
                res.end('Forbidden: Token does not match the provided name');
                return;
            }

            res.writeHead(200, { 'Content-Type': 'text/plain' });
            res.end(`Hola ${query.nombre}`);
        });
    } else if (pathname === '/login' && req.method === 'POST') {
        let body = '';
        req.on('data', chunk => {
            body += chunk.toString();
        });
        req.on('end', () => {
            try {
                const { usuario, clave } = JSON.parse(body);
                if (usuario && clave) {
                    const token = jwt.sign(
                        { usuario },
                        SECRET_KEY,
                        { expiresIn: '1h', issuer: 'ingesis.uniquindio.edu.co' }
                    );
                    res.writeHead(200, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ token }));
                } else {
                    res.writeHead(400, { 'Content-Type': 'text/plain' });
                    res.end('Solicitud no valida: Los atributos usuario y clave son obligatorios');
                }
            } catch (error) {
                res.writeHead(400, { 'Content-Type': 'text/plain' });
                res.end('Solicitud no valida: Error en el formato del JSON');
            }
        });
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

server.listen(3000, () => {
    console.log('Server running at http://localhost:3000/');
});