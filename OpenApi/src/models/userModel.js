const client = require('../database');

const User = {
  create: async (nombre, email, clave) => {
    const result = await client.query('INSERT INTO usuarios (nombre, email, clave) VALUES ($1, $2, $3) RETURNING *', [nombre, email, clave]);
    return result.rows[0];
  },
  findByEmail: async (email) => {
    const result = await client.query('SELECT * FROM usuarios WHERE email = $1', [email]);
    return result.rows[0];
  },
  // Otros métodos CRUD...
};

module.exports = User;
