    const express = require('express');
    const feController = require('../app/controllers/FeController');

    // Initialize the router
    const router = express.Router();

    // Define routes
    router.get('/', feController.home);
    router.get('/dashboard', feController.dashboard);
    router.get('/card', feController.card);


    module.exports = (app) => {
        app.use('/', router);  // Prefix all routes with /api
    };
