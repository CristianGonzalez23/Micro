import sequelize from '../config/database.mjs';
import User from './User.mjs';

const db = {
  sequelize,
  User,
};

export { sequelize, User };
export default db;