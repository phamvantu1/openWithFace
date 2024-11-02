const express = require('express');
const router = express.Router();


const siteController = require('../app/controllers/SiteController');
router.post('/keypad/update', siteController.updatepass);
router.post('/checkpass', siteController.checkpass);
router.post('/create_card_lock', siteController.createCardLock);
router.post('/log_access',siteController.logAccess);
router.post('/login',siteController.handleLogin);
router.get('/keypad',siteController.keypad);
router.get('/thetu',siteController.Quanlythe);
router.get('/dulieu',siteController.dulieu);
router.get('/login', siteController.login);
router.get('/', siteController.home);


module.exports = router;