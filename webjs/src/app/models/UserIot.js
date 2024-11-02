const { DataTypes } = require('sequelize');
const sequelize = require('../../config/db/DBcontext');

const UserIot = sequelize.define('UserIot', {
    id: {
        type: DataTypes.INTEGER,
        autoIncrement: true,
        primaryKey: true
    },
    ten: {
        type: DataTypes.STRING(100),
        allowNull: false
    },
    user: {
        type: DataTypes.STRING(50),
        allowNull: false,
        unique: true
    },
    password: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
    passdoor: {
        type: DataTypes.STRING(255),
        allowNull: false
    },
}, {
    tableName: 'user_iot',
    timestamps: false
});

module.exports = UserIot;
