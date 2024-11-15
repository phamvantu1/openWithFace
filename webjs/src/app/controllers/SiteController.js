const express = require('express');
const app = express();
const socket = require('../../socket/socket');
const db = require('../../config/db/DBcontext');
let userLogs = [];
const axios = require('axios');
class SiteController {

    login(req,res){
        res.render('login.html');
    }

    home(req, res) {
        if (!req.session.userID) {
            return res.redirect('/login');
        }

        res.render('main.html', {
            username: req.session.username
        });
    }

    updatepass(req, res) {
    const { currentPassword, newPassword } = req.body;
    const userId = req.session.userID; // Lấy ID người dùng hiện tại từ session hoặc token
    console.log(req.body);

    // Truy vấn để lấy mật khẩu hiện tại
    db.query('SELECT passdoor FROM user_iot WHERE id = ?', [userId], (error, results) => {
        if (error) {
            console.error("Lỗi truy vấn:", error);
            return res.status(500).json({ message: "Internal Server Error" });
        }

        if (results.length === 0) {
            return res.status(404).json({ message: "Người dùng không tồn tại." });
        }

        // Kiểm tra mật khẩu hiện tại
        const user = results[0];
        console.log(user.passdoor);
        
        if (user.passdoor !== currentPassword) {
            return res.status(400).json({ message: "Mật khẩu hiện tại không chính xác." });
        }

        // Cập nhật mật khẩu mới trong cơ sở dữ liệu
        db.query('UPDATE user_iot SET passdoor = ? WHERE id = ?', [newPassword, userId], (err, result) => {
            if (err) {
                console.error("Lỗi cập nhật mật khẩu:", err);
                return res.status(500).json({ message: "Internal Server Error" });
            }

            // Chỉ gửi phản hồi một lần
            res.json({ message: "Đổi mật khẩu thành công." });
            // Không nên có thêm res.redirect('/') ở đây nếu đã sử dụng res.json()
        });
    });
}

    handleLogin(req, res) {
        const { username, password } = req.body;

        const query = 'SELECT * FROM user_iot WHERE user = ? AND password = ?';
        db.query(query, [username, password], (err, results) => {
            if (err) {
                console.error('Lỗi truy vấn:', err.message);
                return res.render('login.html', { error: 'Đã xảy ra lỗi. Vui lòng thử lại.' });
            }

            if (results.length > 0) {
                const user = results[0];
                req.session.userID = user.id; 
                req.session.username = user.ten; 
                res.redirect('/'); 
            } else {
                res.render('login.html', { error: 'Tên người dùng hoặc mật khẩu không đúng' });
            }
        });
    }
    dulieu(req, res) {
        res.render('dulieu.html', {
            username: req.session.username
        });
    }

    logAccess(req, res) {
    const { userID, time } = req.body;
    console.log('Received:', { userID, time });

    const query = 'SELECT * FROM card_lock WHERE id_the = ?';
    db.query(query, [userID], (err, results) => {
        if (err) {
            console.error('Lỗi truy vấn:', err.message);
            return res.json({ success: false, message: 'Lỗi khi kiểm tra thẻ' });
        }

        const doorStatus = results.length > 0 ? 1 : 0;

        const logEntry = {
            id: userID,
            time: time,
            date: new Date().toLocaleDateString(),
            log: doorStatus === 1 ? "Success" : "Failure" 
        };

        userLogs.push(logEntry);
        socket.getIO().emit('doorStatus', userLogs);

        res.json({ success: true, message: 'Logged successfully', userLogs: userLogs, doorStatus: doorStatus });
        });
    }

    checkpass(req,res){
        const keyword = req.body.keyword; 
        const query = 'SELECT * FROM user_iot WHERE passdoor = ?';

        // Thực hiện truy vấn
        db.query(query, [keyword], (error, results) => {
            if (error) {
                console.error("Lỗi truy vấn:", error);
                return res.status(500).json({ message: "Internal Server Error" });
            }

            // Kiểm tra kết quả truy vấn
            if (results.length > 0) {
                res.json({ doorStatus: 1, message: "Access granted." });
            } else {
                res.json({ doorStatus: 0, message: "Access denied." });
            }
        });
    }

    checkapp(req, res) {
        const doorStatus = req.body.doorStatus; // Lấy trạng thái cửa từ body của yêu cầu
        console.log('Received doorStatus:', doorStatus);
        if (doorStatus == 1) {
            res.json({ doorStatus: 1, message: "Door opened." }); // Mở cửa
        } else {
            res.json({ doorStatus: 0, message: "Door closed." }); // Đóng cửa
        }
    }
   
    



    Quanlythe(req,res){
        const query = 'SELECT * FROM card_lock';
        db.query(query, (err, results) => {
            if (err) {
                console.error('Lỗi truy vấn:', err.message);
                return res.render('thetu.html', { error: 'Đã xảy ra lỗi khi lấy dữ liệu.' });
            }
            res.render('thetu.html', {
                cardLocks: results,
                username: req.session.username
             });
        });
    }
    createCardLock(req, res) {
    const { ten, id_the } = req.body; 

    const query = 'INSERT INTO card_lock (ten, id_the, ngaytao) VALUES (?, ?, CURDATE())';
    db.query(query, [ten, id_the], (err, results) => {
        if (err) {
            console.error('Lỗi truy vấn:', err.message);
            return res.render('main.html', { error: 'Đã xảy ra lỗi khi tạo khóa.' });
        }
        res.redirect('/thetu'); 
    });
    }
    keypad(req,res){
        res.render('keypad.html', {
            username: req.session.username
        });
    }

}
module.exports = new SiteController();