const express = require('express');
const router = express.Router();

const job = require("../api/job/job.index");

router
    .use('/job', job)

module.exports = router;