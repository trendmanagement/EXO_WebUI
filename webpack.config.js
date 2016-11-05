/**
 * Created by ubertrader on 11/5/16.
 */

var webpack = require('webpack');
var path = require('path');

var BUILD_DIR = path.resolve(__dirname, 'assets/js');
var APP_DIR = path.resolve(__dirname, 'tmqr_frontend');

var config = {
    devtool: 'source-map',
    devServer: true,
    debug: true,

    entry: APP_DIR + '/index.jsx',

    output: {
        path: BUILD_DIR,
        filename: 'bundle.js'
    },

    module : {
        loaders : [
            {
                test : /\.jsx?/,
                include : APP_DIR,
                loader : 'babel'
            }
        ]
    }
};

module.exports = config;
