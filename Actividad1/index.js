const http = require('http');  // Importa el módulo HTTP para crear un servidor.
const url = require('url');  // Importa el módulo URL para analizar las URLs.
const jwt = require('jsonwebtoken');  // Importa el módulo JSON Web Token para manejar tokens JWT.

const SECRET_KEY = 'your_secret_key';  // Define una clave secreta para firmar y verificar los tokens JWT.

const server = http.createServer((req, res) => {  // Crea un servidor HTTP.
    const parsedUrl = url.parse(req.url, true);  // Analiza la URL de la solicitud.
    const pathname = parsedUrl.pathname;  // Obtiene la ruta de la URL.
    const query = parsedUrl.query;  // Obtiene los parámetros de consulta de la URL.

    if (pathname === '/saludo' && req.method === 'GET') {  // Maneja las solicitudes GET a la ruta /saludo.
        const authHeader = req.headers['authorization'];  // Obtiene el encabezado de autorización.
        if (!authHeader) {  // Si no hay encabezado de autorización, responde con un error 401.
            res.writeHead(401, { 'Content-Type': 'text/plain' });
            res.end('Unauthorized: No token provided');
            return;
        }

        const token = authHeader.split(' ')[1];  // Extrae el token del encabezado de autorización.
        jwt.verify(token, SECRET_KEY, { issuer: 'ingesis.uniquindio.edu.co' }, (err, decoded) => {  // Verifica el token.
            if (err) {  // Si el token es inválido, responde con un error 401.
                res.writeHead(401, { 'Content-Type': 'text/plain' });
                res.end('Unauthorized: Invalid token');
                return;
            }

            if (decoded.usuario !== query.nombre) {  // Si el usuario en el token no coincide con el nombre en la consulta, responde con un error 403.
                res.writeHead(403, { 'Content-Type': 'text/plain' });
                res.end('Forbidden: Token does not match the provided name');
                return;
            }

            res.writeHead(200, { 'Content-Type': 'text/plain' });  // Si todo es correcto, responde con un saludo.
            res.end(`Hola ${query.nombre}`);
        });
    } else if (pathname === '/login' && req.method === 'POST') {  // Maneja las solicitudes POST a la ruta /login.
        let body = '';
        req.on('data', chunk => {  // Recibe los datos del cuerpo de la solicitud.
            body += chunk.toString();
        });
        req.on('end', () => {  // Cuando se reciben todos los datos, procesa el cuerpo de la solicitud.
            try {
                const { usuario, clave } = JSON.parse(body);  // Analiza el cuerpo de la solicitud como JSON.
                if (usuario && clave) {  // Si el usuario y la clave están presentes, genera un token.
                    const token = jwt.sign(
                        { usuario },
                        SECRET_KEY,
                        { expiresIn: '1h', issuer: 'ingesis.uniquindio.edu.co' }
                    );
                    res.writeHead(200, { 'Content-Type': 'application/json' });  // Responde con el token en formato JSON.
                    res.end(JSON.stringify({ token }));
                } else {  // Si faltan el usuario o la clave, responde con un error 400.
                    res.writeHead(400, { 'Content-Type': 'text/plain' });
                    res.end('Solicitud no valida: Los atributos usuario y clave son obligatorios');
                }
            } catch (error) {  // Si hay un error al analizar el JSON, responde con un error 400.
                res.writeHead(400, { 'Content-Type': 'text/plain' });
                res.end('Solicitud no valida: Error en el formato del JSON');
            }
        });
    } else {  // Si la ruta no es /saludo ni /login, responde con un error 404.
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

server.listen(3000, () => {  // El servidor escucha en el puerto 3000.
    console.log('Server running at http://localhost:3000/');
});