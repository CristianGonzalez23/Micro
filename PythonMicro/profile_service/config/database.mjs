import { Sequelize } from 'sequelize';

const sequelize = new Sequelize('mydatabase', 'root', 'rootpassword', {
  host: 'mysql_db',
  dialect: 'mysql',
  define: {
    freezeTableName: true, // Para evitar que Sequelize pluralice los nombres de las tablas
  },
});

export default sequelize;