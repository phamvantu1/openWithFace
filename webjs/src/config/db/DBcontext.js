
const mysql = require('mysql2');

const dbConfig = {
    host: 'mysql',
    user: 'root',
    password: '123456',
    database: 'smartdoor'
};

const connection = mysql.createConnection(dbConfig);

connection.connect((err) => {
    if (err) {
        console.error('Kết nối tới cơ sở dữ liệu thất bại:', err.message);
    } else {
        console.log('Kết nối thành công');
    }
});

module.exports = connection;
