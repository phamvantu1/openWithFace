const express = require('express');
const fs = require('fs');
const path = require('path');
const morgan = require('morgan');
const methodOverride = require('method-override');
// const socketIo = require('socket.io');
const http = require('http');
const session = require('express-session');
const route = require('./routes/iot');
const db = require('./config/db/DBcontext');


const app = express();
const port = 3001;
app.use(morgan('combined'));
const server = http.createServer(app);

const socket = require('./socket/socket');
const io = socket.init(server); 

app.use(session({
    secret: 'your-secret-key', 
    resave: false,
    saveUninitialized: true,
    cookie: { secure: false } 
}));


app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(express.static(path.join(__dirname, 'public')));

app.use(methodOverride('_method'));

let userLogs = [];

app.engine('html', require('ejs').renderFile);
app.set('views', path.join(__dirname, 'resources', 'views'));
route(app);
// app.post('/log_access', (req, res) => {
//     const { userID, time } = req.body;

//     console.log('Received:', { userID, time });

//     userLogs.push({
//         userID: userID,
//         time: time,
//         date: new Date().toLocaleDateString(),
//     });

//     io.emit('newLog', userLogs); 

    
//     res.json({ message: 'Logged successfully', userLogs: userLogs });
// });


server.listen(port, () => {
    console.log(`Example app listening at http://localhost:${port}`);
});
