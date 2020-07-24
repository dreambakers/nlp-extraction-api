const { mongoose } = require('../../db/connection');
const constants = require('../../constants');
const Schema = mongoose.Schema;

const jobSchema = new mongoose.Schema({
    status: {
        type: String,
        default: constants.status.running,
        enum: constants.getStatusList()
    },
    handles: String,
    toInvoke: String,
    jobId: String
}, {
    timestamps: true
});

const Job = mongoose.model('Job', jobSchema);
module.exports = {
    Job
};