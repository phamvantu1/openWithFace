    const express = require('express');
    const feController = require('../app/controllers/FeController');
    const { checkAuth, checkRole } = require('../middlewares/authMiddleware');
    const siteController = require('../app/controllers/SiteController');

    // Initialize the router
    const router = express.Router();

    // Define routes
    router.get('/', feController.home);
    router.get('/dashboard', feController.dashboard);
    router.get('/card', feController.card);
    router.get('/users'  ,feController.users);
    router.get('/profile'  ,feController.profile);

    router.post('/log_access',  siteController.logAccess);

    module.exports = (app) => {
        app.use('/', router);  // Prefix all routes with /api
    };
