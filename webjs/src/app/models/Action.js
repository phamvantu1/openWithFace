const { DataTypes } = require('sequelize');
const sequelize = require('../../config/db/DBcontext');

const Action = sequelize.define('Action', {
    id: {
        type: DataTypes.INTEGER,
        autoIncrement: true,
        primaryKey: true
    },
    card_number: {
        type: DataTypes.STRING(255),
        allowNull: true // Có thể để NULL
    },
    action_type: {
        type: DataTypes.ENUM('keypad', 'web', 'card'),
        allowNull: false
    },
    status: {
        type: DataTypes.ENUM('success', 'failure'),
        allowNull: false
    },
    timestamp: {
        type: DataTypes.DATE,
        defaultValue: DataTypes.NOW
    }
}, {
    tableName: 'action',
    timestamps: false
});

module.exports = Action;
