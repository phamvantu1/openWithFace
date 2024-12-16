const sitesRouter = require('./site');

function route(app) {
    app.use('/', sitesRouter);
}

module.exports = route;
