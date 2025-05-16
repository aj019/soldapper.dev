const webpack = require('webpack');

module.exports = function override(config) {
  const fallback = config.resolve.fallback || {};
  Object.assign(fallback, {
    "crypto": require.resolve("crypto-browserify"),
    "stream": require.resolve("stream-browserify"),
    "buffer": require.resolve("buffer/"),
    "process": require.resolve("process/browser"),
    "path": require.resolve("path-browserify"),
    "os": require.resolve("os-browserify/browser"),
    "http": require.resolve("stream-http"),
    "https": require.resolve("https-browserify"),
    "url": require.resolve("url/"),
    "assert": require.resolve("assert/"),
    "fs": false,
    "net": false,
    "tls": false,
    "zlib": false
  });
  
  config.resolve.fallback = fallback;
  config.resolve.extensions = [...config.resolve.extensions, '.mjs', '.js', '.jsx', '.ts', '.tsx'];
  
  config.plugins = (config.plugins || []).concat([
    new webpack.ProvidePlugin({
      process: 'process/browser',
      Buffer: ['buffer', 'Buffer'],
    }),
    new webpack.DefinePlugin({
      'process.env': JSON.stringify(process.env),
      'process.type': JSON.stringify(process.type),
      'process.version': JSON.stringify(process.version),
    }),
  ]);

  // Handle ESM modules
  config.module.rules.push({
    test: /\.m?js/,
    resolve: {
      fullySpecified: false
    }
  });

  return config;
}; 