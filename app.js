const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
require('dotenv').config()

const routes = require('./routes/routes');

const app = express();
app.use(cors({ origin:true, credentials: true })); // allow cors headers
app.use(bodyParser.json());

const port = process.env.PORT || 3000;

app.use(function (req, res, next) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, PATCH, DELETE');
  res.setHeader('Access-Control-Allow-Credentials', true);
  next();
});

app.get('/', (req, res) => { res.send('API is running.') });

app.use('/', routes);

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

module.exports = { app }