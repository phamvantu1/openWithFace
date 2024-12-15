const express = require('express');
const siteController = require('../app/controllers/SiteController');
const { checkAuth, checkRole } = require('../middlewares/authMiddleware');

// Initialize the router
const router = express.Router();

// Define routes
router.get('/', siteController.home);
router.post('/login', siteController.login);
router.post('/logout', checkAuth ,siteController.logout);
router.put('/update-password', checkAuth, siteController.updatePass);
router.post('/log_access',  siteController.logAccess);
router.post('/checkpass',  siteController.checkPass);
router.post('/create-card',checkAuth,  siteController.createCardLock);
router.put('/update-card/:cardID',  siteController.updateCard);
router.delete('/delete-card/:cardID',  siteController.deleteCard);
router.get('/get-all-cards', checkAuth, siteController.getAllCards); // Get all cards (admin or own)
router.get('/get-all-users', checkAuth, siteController.getAllUsers); // Get all users except admin

router.post('/register', siteController.register);

module.exports = (app) => {
    app.use('/api', router);  // Prefix all routes with /api
};
