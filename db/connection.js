var mongoose = require('mongoose');

const { dbConnectionUrl } = require('../config/config');

mongoose.connect(dbConnectionUrl, {
    useUnifiedTopology: true,
    useNewUrlParser: true,
    useFindAndModify: false
});

mongoose.set('useCreateIndex', true);

module.exports = { mongoose };