import { User } from '../models/index.mjs';
import jwt from 'jsonwebtoken';
import axios from 'axios';
const SECRET_KEY = 'super-secret-key';

export const getUserProfile = async (req, res) => {
  try {
    const token = req.headers.authorization.split(' ')[1];
    const email = req.query.email;

    if (!email) {
      console.log('Email no proporcionado');
      return res.status(400).json({ error: 'Email no proporcionado' });
    }

    console.log('Token recibido:', token);
    console.log('Email recibido:', email);

    // Enviar el token a app.py para su verificación
    const response = await axios.post('http://python_app:5000/verify_token', {
      token
    });

    if (response.data.valid) {
      const user = await User.findOne({ where: { email } });

      if (!user) {
        console.log('Usuario no encontrado');
        return res.status(404).json({ error: 'Usuario no encontrado' });
      }

      res.json(user);
    } else {
      console.log('Token inválido o expirado');
      return res.status(401).json({ error: 'Token inválido o expirado' });
    }
  } catch (error) {
    console.error('Error al verificar el token:', error);
    res.status(500).json({ error: error.message });
  }
};

export const updateProfile = async (req, res) => {
  try {
    const token = req.headers.authorization.split(' ')[1];
    const email = req.query.email;
    console.log('Token recibido:', token);

    // Enviar el token a app.py para obtener el email
    const response = await axios.post('http://python_app:5000/verify_token', {
      token
    });

    if (response.data.valid) {
      
      console.log('Email recibido:', email);

      const updatedData = req.body;
      const [updated] = await User.update(updatedData, { where: { email } });

      if (updated) {
        const updatedUser = await User.findOne({ where: { email } });
        res.json({ message: 'Perfil actualizado con éxito', user: updatedUser });
      } else {
        console.log('Usuario no encontrado');
        return res.status(404).json({ error: 'Usuario no encontrado' });
      }
    } else {
      console.log('Token inválido o expirado');
      return res.status(401).json({ error: 'Token inválido o expirado' });
    }
  } catch (error) {
    console.error('Error al verificar el token:', error);
    res.status(500).json({ error: error.message });
  }
};

export const deleteUser = async (req, res) => {
  try {
    const token = req.headers.authorization.split(' ')[1];
    const email = req.query.email;
    console.log('Token recibido:', token);

    // Enviar el token a app.py para obtener el email
    const response = await axios.post('http://python_app:5000/verify_token', {
      token
    });

    if (response.data.valid) {
     
      console.log('Email recibido:', email);

      const user = await User.findOne({ where: { email } });

      if (!user) {
        console.log('Usuario no encontrado');
        return res.status(404).json({ error: 'Usuario no encontrado' });
      }

      const deleted = await User.destroy({ where: { email } });

      if (deleted) {
        res.json({ message: 'Usuario eliminado con éxito' });
      } else {
        console.log('Error al eliminar el usuario');
        return res.status(500).json({ error: 'Error al eliminar el usuario' });
      }
    } else {
      console.log('Token inválido o expirado');
      return res.status(401).json({ error: 'Token inválido o expirado' });
    }
  } catch (error) {
    console.error('Error al verificar el token:', error);
    res.status(500).json({ error: error.message });
  }
};