// iot.js (hoặc app.js, server.js)
const express = require('express');
const fs = require('fs');
const path = require('path');
const morgan = require('morgan');
const methodOverride = require('method-override');
const http = require('http');
const session = require('express-session');
const route = require('./routes/site');  // Đảm bảo rằng đường dẫn này đúng

const db = require('./config/db/DBcontext');
const socket = require('./socket/socket');
const cors = require('cors');
const app = express();
const port = 3000;

// Middleware để phân tích dữ liệu JSON body (đặt ở trên các route để nó hoạt động trước)
app.use(express.json());  // Đây là middleware quan trọng
app.use('/images', express.static(path.join(__dirname, 'public', 'images')));
// Các middleware khác
app.use(morgan('combined'));  // Để log các yêu cầu HTTP
const server = http.createServer(app);  // Khởi tạo HTTP server
const siteRoutes = require('./routes/home');
siteRoutes(app);
const io = socket.init(server);  // Khởi tạo socket.io
app.use(cors());

// Cấu hình session
app.use(session({
    secret: 'your-secret-key',
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false }
}));

// Cấu hình middleware để xử lý các yêu cầu URL-encoded và JSON
app.use(express.urlencoded({ extended: true }));

// Cấu hình static files
app.use(express.static(path.join(__dirname, 'public')));

// Middleware methodOverride để hỗ trợ các HTTP verbs như PUT, DELETE trong forms
app.use(methodOverride('_method'));
app.set('view engine', 'ejs'); // Sử dụng EJS làm engine template
app.set('views', path.join(__dirname, 'resources', 'views'));
// Gọi các route
route(app);

// Khởi động server
server.listen(port, () => {
    console.log(`Server is running at http://localhost:${port}`);
});
