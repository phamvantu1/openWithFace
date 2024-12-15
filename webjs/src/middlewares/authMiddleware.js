const jwt = require('jsonwebtoken');

const checkAuth = (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) return res.status(401).json({ message: 'Authentication required' });

    jwt.verify(token, 'secret_key', (err, decoded) => {
        if (err) return res.status(403).json({ message: 'Invalid token' });

        req.user = decoded;
        console.log(req.user.role)
        next();
    });
};


const checkRole = (role) => (req, res, next) => {
    const token = req.headers.authorization?.split(' ')[1];
    jwt.verify(token, 'secret_key', (err, decoded) => {
        if (err) return res.status(403).json({ message: 'Invalid token' });

        req.user = decoded;
        if(req.user.role !== role) return res.status(401).json({message: "Access denied"})
        console.log(req.user.role)
    });
    next();
};

module.exports = { checkAuth, checkRole };
