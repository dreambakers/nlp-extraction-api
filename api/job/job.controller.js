const { Job } = require('./job.model');
const spawn = require('child_process').spawn
const constants = require('../../constants');
var path = require("path");
var moment = require('moment');

const invokeJob = async (req, res) => {
    try {
        const jobId = moment().utcOffset(-5).format('YYYY_MM_DD_HH:mm:ss');
        const toInvoke = req.body.properties.toInvoke;
        const handles = req.body.properties.handles.map(
            handleObj => `@${handleObj.handle.trim()}`
        ).join(',');

        let newJob = new Job({
            jobId,
            handles,
            toInvoke
        });
        newJob = await newJob.save();

        const pythonProcess
        = spawn(
            'python',
            [
                path.join(constants.scriptsPath, 'nlp', 'covid_twitter_script.py'),
                jobId,
                handles,
                toInvoke
            ],
            {
                cwd: path.join(constants.scriptsPath, 'nlp')
            }
        );

        pythonProcess.stdout.setEncoding('utf8');
        pythonProcess.stdout.on('data', function(data) {
            console.log('stdout: ',  data.toString());
        });

        pythonProcess.stderr.setEncoding('utf8');
        pythonProcess.stderr.on('data', function(data) {
            console.log(`An error occurred while executing the script for jobId ${jobId}`, data.toString());
        });

        pythonProcess.on('close', function(exitCode) {
            //Here you can get the exit code of the script
            if (exitCode === 0) {
                console.log(`Script execution successful for jobId ${jobId}`);
                Job.findOneAndUpdate({ _id: newJob._id} , { $set: { status : constants.status.completed } }).exec();
            } else {
                Job.findOneAndUpdate({ _id: newJob._id} , { $set: { status : constants.status.failed } }).exec();
            }
            console.log('Exit code: ' + exitCode);
        });

        res.json({
            success: !!newJob,
            job: newJob
        });
    } catch (error) {
        console.log(error);
        res.json({
            success: 0,
            msg: 'An error occured while triggering the job'
        });
    }
}

const getAllJobs = async (req, res) => {
    try {
        const jobs = await Job.find();
        res.json({
            jobs,
            success: 1
        });
    } catch (error) {
        console.log(error);
        res.json({
            success: 0,
            msg: 'An error occured while getting the jobs'
        });
    }
}

const downloadJobResult = async (req, res) => {
    try {
        const filePath = path.join(constants.scriptsPath, 'nlp', 'output', req.body.fileName);
        res.sendFile(filePath);
    } catch (error) {
        console.log(error);
        res.json({
            success: 0,
            msg: 'An error occured while downloading the job result'
        });
    }
}

module.exports = {
    invokeJob, getAllJobs, downloadJobResult
};