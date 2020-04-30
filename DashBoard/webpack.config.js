var path = require('path');

module.exports = {
  mode: 'development',
  entry: './src/cognitoFn.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'cognitoFn.bundle.js',
    library: 'Login',
	libraryTarget: 'window'
  },
  optimization: {
        minimize: false
    },
};
