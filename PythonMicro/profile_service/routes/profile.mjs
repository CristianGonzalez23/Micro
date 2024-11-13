import express from 'express';
import { getUserProfile, updateProfile, deleteUser } from '../controllers/userController.mjs';
import { authenticate } from '../middleware/authMiddleware.mjs';
const router = express.Router();

router.get('/profile', authenticate, getUserProfile);
router.put('/profile', authenticate, updateProfile);
router.delete('/profile', authenticate, deleteUser);

export default router;