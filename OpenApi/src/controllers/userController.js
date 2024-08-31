const argon2 = require('argon2');
const jwt = require('jsonwebtoken');
const User = require('../models/userModel');

const registerUser = async (req, res) => {
  const { nombre, email, clave } = req.body;
  const hashedPassword = await argon2.hash(clave);

  try {
    const newUser = await User.create(nombre, email, hashedPassword);
    res.status(201).json(newUser);
  } catch (error) {
    res.status(500).json({ error: "Error al crear el usuario" });
  }
};

// Otros métodos como login, actualizar, eliminar...

module.exports = { registerUser };