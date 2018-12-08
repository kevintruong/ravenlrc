var http = require('http');
var express = require("express");
var path = require("path");
var app = express();
var bodyParser = require("body-parser");
var fileUpload = require('express-fileupload');
// Use python shell

var myPythonScriptPath = 'backendcli.py';
var PythonShell = require('python-shell');
var pyshell = new PythonShell(myPythonScriptPath);


/** bodyParser.urlencoded(options)
 * Parses the text as URL encoded data (which is how browsers tend to send form data from regular forms set to POST)
 * and exposes the resulting object (containing the keys and values) on req.body
 */
app.use(bodyParser.urlencoded({
    extended: true
}));
app.use(fileUpload());

app.use(bodyParser.json());

var logger = require('morgan');

var youtube_entries = [];
app.locals.entries = youtube_entries;

app.set("views", path.resolve(__dirname, "views"));
app.set("view engine", "ejs");

app.get("/", function (request, response) {
    response.render("index", {
        message: "hello, my name kevin"
    });
});


app.get("/new-mv", function (request, response) {
    response.render("new-mv");
});

/**
 * ncturl: text http url nhaccuatui\
 * ******************************
 * coordinate: x,y
 * fontfile: text font file: file
 * fontsize : int: font size
 * fontcolor color: text hex code
 ************************************
 *  effectfile: file : effect file
 *  opacity: opacity of effect
 * ***********************************'
 * titleimg : file : title img file
 * titlecoordinate: text: coordinate of title file x,y
 *
 *
 */
app.post("/new-mv", function (request, response) {
    response.send("respond from post new-mv");

    function handle_ncturl(ncturl) {
        console.log(ncturl)
    }

    console.log(Object.keys(request.files).length);
    handle_ncturl(request.body.ncturl);
});


http.createServer(app).listen(3000, function () {
    console.log("start youtube creator app on port 3000")
});