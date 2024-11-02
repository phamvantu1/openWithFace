const { DataTypes } = require('sequelize');
const sequelize = require('../../config/db/DBcontext');

const CardLock = sequelize.define('CardLock', {
    id: {
        type: DataTypes.INTEGER,
        autoIncrement: true,
        primaryKey: true
    },
    ten: {
        type: DataTypes.STRING(100),
        allowNull: false
    },
    id_the: {
        type: DataTypes.STRING(50),
        allowNull: false,
        unique: true
    },
    ngaytao: {
        type: DataTypes.DATE,
        allowNull: false
    }
}, {
    tableName: 'card_lock',
    timestamps: false
});

module.exports = CardLock;
