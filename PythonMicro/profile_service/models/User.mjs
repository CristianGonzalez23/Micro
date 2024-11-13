import { DataTypes } from 'sequelize';
import sequelize from '../config/database.mjs';

const User = sequelize.define('user', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true,
  },
  username: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
  },
  email: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: true,
  },
  password_hash: {
    type: DataTypes.STRING,
    allowNull: false,
  },
  created_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
  updated_at: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW,
  },
  personal_page: DataTypes.STRING,
  nickname: DataTypes.STRING,
  contact_public: {
    type: DataTypes.BOOLEAN,
    defaultValue: false,
  },
  address: DataTypes.STRING,
  biography: DataTypes.TEXT,
  organization: DataTypes.STRING,
  country: DataTypes.STRING,
  social_links: DataTypes.JSON,
}, {
  timestamps: false,
  tableName: 'user', // Asegúrate de que el nombre de la tabla sea correcto
});

export default User;