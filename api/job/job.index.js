const express = require('express');
const controller = require('./job.controller')

const router = express.Router();

router
    .post('/invoke', controller.invokeJob)
    .post('/download', controller.downloadJobResult)
    .get('/all', controller.getAllJobs);

module.exports = router;