const metadataJson = require('./metadata.json');

module.exports = {
  metadata: Array.isArray(metadataJson) ? metadataJson : []
};
