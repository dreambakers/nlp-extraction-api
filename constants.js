var path = require("path");

module.exports = {
    status: {
        running: 'running',
        completed: 'completed',
        failed: 'failed',
    },
    getStatusList: function() {
        return Object.values(this.status);
    },
    scriptsPath: path.join(__dirname, 'scripts')
}
