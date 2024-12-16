const express = require('express');
const jwt = require('jsonwebtoken');
const db = require('../../config/db/DBcontext');
const socket = require('../../socket/socket');
const { checkAuth, checkRole } = require('../../middlewares/authMiddleware'); // Middleware for checking auth and role
const axios = require('axios');
const fs = require('fs');
const path = require('path');

class FeController {

    home(req, res) {
        res.render('login.ejs');
    }

    login(req, res)  {
        res.render('login.ejs');
    };
    dashboard(req, res) {
        res.render('dashboard.ejs');
    }
    card(reg, res) {
        res.render('card.ejs');
    }
}
module.exports = new FeController();
