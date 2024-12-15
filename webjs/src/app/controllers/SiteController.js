const express = require('express');
const jwt = require('jsonwebtoken');
const db = require('../../config/db/DBcontext');
const socket = require('../../socket/socket');
const { checkAuth, checkRole } = require('../../middlewares/authMiddleware'); // Middleware for checking auth and role
const axios = require('axios');
const fs = require('fs');
const path = require('path');
class SiteController {

    // User login API
    async login(req, res) {
        const { username, password } = req.body;
        console.log(username);
        console.log(password);
        const query = 'SELECT * FROM user_iot WHERE user = ? AND password = ?';

        db.query(query, [username, password], (err, results) => {
            if (err) {
                console.error('Database error:', err.message);
                return res.status(500).json({
                    status: 'error',
                    message: 'Database error',
                    data: null
                });
            }
            if (results.length > 0) {
                const user = results[0];
                console.log(user);

                const token = jwt.sign({ userID: user.id, username: user.ten, role: user.role}, 'secret_key', { expiresIn: '1h' });
                return res.status(200).json({
                    status: 'success',
                    message: 'Login successful',
                    data: { token }
                });
            } else {
                console.log(results);
                return res.status(400).json({
                    status: 'fail',
                    message: 'Invalid username or password',
                    data: null
                });
            }
        });
    }

    // Middleware protected home route
    home(req, res) {
        res.json({
            status: 'success',
            message: 'Welcome',
            data: null
        });
    }

    // Update password (authentication required)
    async updatePass(req, res) {
        const { currentPassword, newPassword } = req.body;
        const userId = req.user.userID;  // Get user ID from JWT token
        console.log(req.user)
        db.query('SELECT passdoor FROM user_iot WHERE id = ?', [userId], (error, results) => {
            if (error) return res.status(500).json({
                status: 'error',
                message: "Internal Server Error",
                data: null
            });
            if (results.length === 0) return res.status(404).json({
                status: 'fail',
                message: "User not found",
                data: null
            });

            const user = results[0];
            if (user.passdoor !== currentPassword) {
                return res.status(400).json({
                    status: 'fail',
                    message: "Incorrect current password",
                    data: null
                });
            }

            db.query('UPDATE user_iot SET passdoor = ? WHERE id = ?', [newPassword, userId], (err, result) => {
                if (err) return res.status(500).json({
                    status: 'error',
                    message: "Failed to update password",
                    data: null
                });
                res.status(200).json({
                    status: 'success',
                    message: "Password updated successfully",
                    data: null
                });
            });
        });
    }

    // Log access (authentication required)
    logAccess = async (req, res) => {
        const { userID, time } = req.body;
        const imageUrl = "http://127.0.0.1:5000/get-image";
        const imageFolder = path.join(__dirname, 'images');

        // Tạo thư mục nếu chưa tồn tại
        if (!fs.existsSync(imageFolder)) {
            fs.mkdirSync(imageFolder, { recursive: true });
        }

        // Tải ảnh và lưu vào thư mục
        const downloadImage = async () => {
            const imageFileName = `${Date.now()}.jpg`; // Đặt tên file dựa trên timestamp
            const imagePath = path.join(imageFolder, imageFileName);

            try {
                const response = await axios({
                    method: 'get',
                    url: imageUrl,
                    responseType: 'stream',
                });

                const writer = fs.createWriteStream(imagePath);
                response.data.pipe(writer);

                return new Promise((resolve, reject) => {
                    writer.on('finish', () => resolve(imagePath));
                    writer.on('error', reject);
                });
            } catch (error) {
                throw new Error(`Error downloading image: ${error.message}`);
            }
        };
        console.log("ds");
        try {
            const imagePath = await downloadImage(); // Chờ tải ảnh xong
            console.log('Image saved:', imagePath);

            // Tiếp tục xử lý cơ sở dữ liệu
            console.log(userID, time);
            db.query('SELECT * FROM card_lock WHERE id_the = ?', [userID], (err, results) => {
                if (err) {
                    return res.status(500).json({
                        status: 'error',
                        message: 'Error querying database',
                        data: null,
                    });
                }

                const doorStatus = results.length > 0 ? 1 : 0;
                const logEntry = {
                    id: userID,
                    time,
                    date: new Date().toLocaleDateString(),
                    log: doorStatus === 1 ? "Success" : "Failure",
                    image: imagePath,
                };

                socket.getIO().emit('doorStatus', logEntry);

                if (doorStatus === 1) {
                    console.log(results);
                    const user_id = results[0].user_id;
                    const actionQuery =
                        'INSERT INTO action (card_number, action_type, status, user_id, image) VALUES (?, ?, ?, ?, ?)';
                    db.query(
                        actionQuery,
                        [results[0].ten, 'card', 'SUCCESS', user_id, imagePath],
                        (actionErr) => {
                            if (actionErr) console.error('Error inserting action:', actionErr.message);
                        }
                    );
                }

                res.status(200).json({
                    status: 'success',
                    message: 'Log entry created',
                    data: { logEntry },
                });
            });
        } catch (error) {
            console.error(error.message);
            res.status(500).json({
                status: 'error',
                message: error.message,
            });
        }
    };


    // Check password (authentication required)
    checkPass(req, res) {
        const { keyword } = req.body;

        db.query('SELECT * FROM user_iot WHERE passdoor = ?', [keyword], (error, results) => {
            if (error) return res.status(500).json({
                status: 'error',
                message: 'Database error',
                data: null
            });
            if (results.length > 0) {
                db.query('INSERT INTO action (card_number, action_type, status) VALUES (?, ?, ?)', ['Pass', 'keypad', 'SUCCESS'], (actionErr) => {
                    if (actionErr) return res.status(500).json({
                        status: 'error',
                        message: 'Failed to log action',
                        data: null
                    });
                    res.json({
                        status: 'success',
                        doorStatus: 1,
                        message: 'Access granted',
                        data: null
                    });
                });
            } else {
                res.json({
                    status: 'fail',
                    doorStatus: 0,
                    message: 'Access denied',
                    data: null
                });
            }
        });
    }

    // Create card lock (admin)
    async createCardLock(req, res) {
        const { ten, id_the } = req.body;
        const userId =  req.user.userID;

        const query = 'INSERT INTO card_lock (ten, id_the, ngaytao, user_id) VALUES (?, ?, CURDATE(), ?)';
        db.query(query, [ten, id_the, userId], (err, results) => {
            if (err) return res.status(500).json({
                status: 'error',
                message: 'Database error',
                data: null
            });
            res.status(201).json({
                status: 'success',
                message: 'Card created successfully',
                data: { cardID: results.insertId }
            });
        });
    }

    // Update card lock (admin)
    updateCard(req, res) {
        const { cardID } = req.params;
        const { ten, id_the } = req.body;

        const query = 'UPDATE card_lock SET ten = ?, id_the = ? WHERE id = ?';
        db.query(query, [ten, id_the, cardID], (err, results) => {
            if (err) return res.status(500).json({
                status: 'error',
                message: 'Database error',
                data: null
            });
            if (results.affectedRows > 0) {
                res.status(200).json({
                    status: 'success',
                    message: 'Card updated successfully',
                    data: null
                });
            } else {
                res.status(404).json({
                    status: 'fail',
                    message: 'Card not found',
                    data: null
                });
            }
        });
    }

    // Delete card lock (admin)
    deleteCard(req, res) {
        const { cardID } = req.params;

        db.query('DELETE FROM card_lock WHERE id = ?', [cardID], (err, results) => {
            if (err) return res.status(500).json({
                status: 'error',
                message: 'Database error',
                data: null
            });
            if (results.affectedRows > 0) {
                res.status(200).json({
                    status: 'success',
                    message: 'Card deleted successfully',
                    data: null
                });
            } else {
                res.status(404).json({
                    status: 'fail',
                    message: 'Card not found',
                    data: null
                });
            }
        });
    }

    // Logout (authentication required)
    logout(req, res) {
        // Optional: You can clear session or token-based invalidation logic here if needed
        res.status(200).json({
            status: 'success',
            message: 'Logged out successfully',
            data: null
        });
    }

    // Get all card locks (Admin only)
// Get all cards (Admin can view all, non-admin can view their own cards only)
async getAllCards(req, res) {
    const userId = req.user.userID;

    // Check if the user has an admin role
    if (req.user.role === 'admin') {
        // Admin can see all cards
        db.query('SELECT * FROM card_lock', (err, results) => {
            if (err) {
                return res.status(500).json({
                    status: 'error',
                    message: 'Database error',
                    data: null
                });
            }
            res.status(200).json({
                status: 'success',
                message: 'All cards retrieved successfully',
                data: results
            });
        });
    } else {
        // Non-admin can only see their own cards
        db.query('SELECT * FROM card_lock WHERE user_id = ?', [userId], (err, results) => {
            if (err) {
                return res.status(500).json({
                    status: 'error',
                    message: 'Database error',
                    data: null
                });
            }

            res.status(200).json({
                status: 'success',
                message: 'Your cards retrieved successfully',
                data: results
            });
        });
    }
}


async getAllUsers(req, res) {
    const userId = req.user.userID;

    // Check if the user has an admin role
    if (req.user.role !== 'admin') {
        return res.status(403).json({
            status: 'fail',
            message: 'Access denied: Admins only',
            data: null
        });
    }

    db.query('SELECT * FROM user_iot WHERE role != "admin"', (err, results) => {
        if (err) {
            return res.status(500).json({
                status: 'error',
                message: 'Database error',
                data: null
            });
        }

        res.status(200).json({
            status: 'success',
            message: 'All users retrieved successfully',
            data: results
        });
    });
}

// Register a new user
async register(req, res) {
    const { username, password, passdoor, ten } = req.body;

    // Check if all required fields are provided
    if (!username || !password || !passdoor) {
        return res.status(400).json({
            status: 'fail',
            message: 'Please provide all required fields: username, password, passdoor',
            data: null
        });
    }

    // Check if username already exists
    db.query('SELECT * FROM user_iot WHERE user = ?', [username], (err, results) => {
        if (err) {
            return res.status(500).json({
                status: 'error',
                message: 'Database error',
                data: null
            });
        }

        if (results.length > 0) {
            return res.status(400).json({
                status: 'fail',
                message: 'Username already exists',
                data: null
            });
        }

        // Insert the new user into the database
        const query = 'INSERT INTO user_iot (user, password, passdoor, ten) VALUES (?, ?, ?, ?)';
        db.query(query, [username, password, passdoor, ten], (err, results) => {
            if (err) {
                return res.status(500).json({
                    status: 'error',
                    message: 'Failed to register user',
                    data: null
                });
            }

            res.status(201).json({
                status: 'success',
                message: 'User registered successfully',
                data: { userID: results.insertId, username }
            });
        });
    });
}

}

module.exports = new SiteController();
