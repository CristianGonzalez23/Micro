const express = require('express');
const router = express.Router();

let users = []; // In-memory user store

// Create a new user
router.post('/users', (req, res) => {
    const { id, name, email } = req.body;
    if (!id || !name || !email) {
        return res.status(400).json({ error: 'id, name, and email are required' });
    }
    users.push({ id, name, email });
    res.status(201).json({ message: 'User created', user: { id, name, email } });
});

// Read all users
router.get('/users', (req, res) => {
    res.json(users);
});

// Read a single user by ID
router.get('/users/:id', (req, res) => {
    const user = users.find(u => u.id === req.params.id);
    if (!user) {
        return res.status(404).json({ error: 'User not found' });
    }
    res.json(user);
});

// Update a user by ID
router.put('/users/:id', (req, res) => {
    const { name, email } = req.body;
    const user = users.find(u => u.id === req.params.id);
    if (!user) {
        return res.status(404).json({ error: 'User not found' });
    }
    user.name = name || user.name;
    user.email = email || user.email;
    res.json({ message: 'User updated', user });
});

// Delete a user by ID
router.delete('/users/:id', (req, res) => {
    users = users.filter(u => u.id !== req.params.id);
    res.json({ message: 'User deleted' });
});

module.exports = router;