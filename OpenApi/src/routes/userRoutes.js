const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const argon2 = require('argon2');
const mysql = require('mysql2/promise');

// Configuración de conexión a la base de datos 
const pool = mysql.createPool({ user: process.env.DB_USER, host: process.env.DB_HOST, database: process.env.DB_NAME, 
  password: process.env.DB_PASSWORD, port: process.env.DB_PORT, });
  

// Swagger documentation for each endpoint is included here

/**
 * @swagger
 * /api/users/:
 *   post:
 *     summary: Registro de un nuevo usuario
 *     description: Registra un nuevo usuario con su nombre, email y clave.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - nombre
 *               - email
 *               - clave
 *             properties:
 *               nombre:
 *                 type: string
 *               email:
 *                 type: string
 *               clave:
 *                 type: string
 *     responses:
 *       201:
 *         description: Usuario creado exitosamente
 *       400:
 *         description: Error en los datos de entrada
 *       500:
 *         description: Error interno del servidor
 */
router.post('/', async (req, res) => {
  const { nombre, email, clave } = req.body;

  // Validar los datos de entrada
  if (!nombre || !email || !clave) {
    return res.status(400).json({ message: 'Todos los campos son requeridos' });
  }

  // Validar formato del email
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({ message: 'Formato de email inválido' });
  }

  try {
    // Verifica si el usuario ya existe
    const result = await pool.query('SELECT * FROM usuarios WHERE email = ?', [email]);
    if (result[0].length > 0) {
      return res.status(409).json({ message: 'El usuario ya existe' });
    }

    // Encriptar la clave del usuario
    const hashedPassword = await argon2.hash(clave);

    // Inserta el nuevo usuario en la base de datos
    await pool.query(
      'INSERT INTO usuarios (nombre, email, password) VALUES (?, ?, ?)',
      [nombre, email, hashedPassword]
    );

    res.status(201).json({ message: 'Usuario creado exitosamente' });
  } catch (error) {
    console.error('Error al registrar usuario:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
});

/**
 * @swagger
 * /api/users/login:
 *   post:
 *     summary: Login de usuario
 *     description: Autentica a un usuario y genera un token JWT.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - email
 *               - clave
 *             properties:
 *               email:
 *                 type: string
 *               clave:
 *                 type: string
 *     responses:
 *       200:
 *         description: Autenticación exitosa
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 token:
 *                   type: string
 *       401:
 *         description: Credenciales incorrectas
 *       400:
 *         description: Datos incorrectos
 *       500:
 *         description: Error interno del servidor
 */
router.post('/login', async (req, res) => {
  const { email, clave } = req.body;
  if (!email || !clave) {
    return res.status(400).json({ message: 'Todos los campos son requeridos' });
  }

  try {
    // Verifica si el usuario existe
    const result = await pool.query('SELECT * FROM usuarios WHERE email = ?', [email]);
    const user = result[0][0];

    if (!user) {
      return res.status(401).json({ message: 'Credenciales incorrectas' });
    }

    // Verifica la contraseña
    const isMatch = await argon2.verify(user.password, clave);

    if (!isMatch) {
      return res.status(401).json({ message: 'Credenciales incorrectas' });
    }

    // Genera el token JWT
    const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, { expiresIn: '1h' });

    res.json({ token });
  } catch (error) {
    console.error('Error en el login:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
});

/**
 * @swagger
 * /api/users/{id}:
 *   get:
 *     summary: Obtener usuario por ID
 *     description: Obtiene los detalles de un usuario específico.
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Usuario encontrado
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 id:
 *                   type: integer
 *                 nombre:
 *                   type: string
 *                 email:
 *                   type: string
 *       404:
 *         description: Usuario no encontrado
 *       500:
 *         description: Error interno del servidor
 */
router.get('/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const result = await pool.query('SELECT * FROM usuarios WHERE id = ?', [id]);
    const user = result[0][0];

    if (!user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    res.json(user);
  } catch (error) {
    console.error('Error al obtener usuario:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
});

/**
 * @swagger
 * /api/users/{id}:
 *   put:
 *     summary: Actualizar usuario
 *     description: Actualiza los datos de un usuario específico.
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               nombre:
 *                 type: string
 *               email:
 *                 type: string
 *               clave:
 *                 type: string
 *     responses:
 *       200:
 *         description: Usuario actualizado exitosamente
 *       400:
 *         description: Error en los datos de entrada
 *       404:
 *         description: Usuario no encontrado
 *       500:
 *         description: Error interno del servidor
 */
router.put('/:id', async (req, res) => {
  const { id } = req.params;
  const { nombre, email, clave } = req.body;

  if (!nombre || !email || !clave) {
    return res.status(400).json({ message: 'Todos los campos son requeridos' });
  }

  try {
    // Encriptar la nueva clave del usuario
    const hashedPassword = await argon2.hash(clave);

    // Actualizar el usuario en la base de datos
    const result = await pool.query(
      'UPDATE usuarios SET nombre = ?, email = ?, password = ? WHERE id = ?',
      [nombre, email, hashedPassword, id]
    );

    if (result[0].affectedRows === 0) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    res.status(200).json({ message: 'Usuario actualizado exitosamente' });
  } catch (error) {
    console.error('Error al actualizar usuario:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
});

/**
 * @swagger
 * /api/users/{id}:
 *   delete:
 *     summary: Eliminar usuario
 *     description: Elimina un usuario específico.
 *     parameters:
 *       - in: path
 *         name: id
 *         required: true
 *         schema:
 *           type: integer
 *     responses:
 *       200:
 *         description: Usuario eliminado exitosamente
 *       404:
 *         description: Usuario no encontrado
 *       500:
 *         description: Error interno del servidor
 */
router.delete('/:id', async (req, res) => {
  const { id } = req.params;

  try {
    const result = await pool.query('DELETE FROM usuarios WHERE id = ?', [id]);
    if (result[0].affectedRows === 0) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    res.status(200).json({ message: 'Usuario eliminado exitosamente' });
  } catch (error) {
    console.error('Error al eliminar usuario:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
});

/**
 * @swagger
 * /api/users/reset-password:
 *   post:
 *     summary: Recuperar clave
 *     description: Envía un enlace de recuperación de clave al email del usuario.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - email
 *             properties:
 *               email:
 *                 type: string
 *     responses:
 *       200:
 *         description: Enlace de recuperación enviado exitosamente
 *       404:
 *         description: Usuario no encontrado
 *       500:
 *         description: Error interno del servidor
 */
router.post('/reset-password', async (req, res) => {
  const { email } = req.body;

  if (!email) {
    return res.status(400).json({ message: 'El campo email es requerido' });
  }

  try {
    // Verifica si el usuario existe
    const result = await pool.query('SELECT * FROM usuarios WHERE email = ?', [email]);
    const user = result[0][0];

    if (!user) {
      return res.status(404).json({ message: 'Usuario no encontrado' });
    }

    // Aquí deberías implementar la lógica para enviar un enlace de recuperación de clave al usuario

    res.status(200).json({ message: 'Enlace de recuperación enviado exitosamente' });
  } catch (error) {
    console.error('Error al enviar enlace de recuperación:', error);
    res.status(500).json({ message: 'Error interno del servidor' });
  }
});

module.exports = router;