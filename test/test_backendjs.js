let {PythonShell} = require('python-shell');

var scripfile = __dirname + "//../backendcli.py";


function run_backend_cli(script, option) {

}

function download_mv(audioQuality, url, outpurdir) {
    console.log(outpurdir);
    console.log(url);
    var options = {
        mode: 'text',
        args: ['downloadcontent', audioQuality, url, outpurdir]
    };
    return new Promise(function (resolve, reject) {
        PythonShell.run(scripfile, options, function (err, result) {
            console.log("the script is exited ");
            if (err) {
                console.log(err);
                throw err;
            }
            console.log(result);
            return result;
        });
    });
}

download_mv(1, String.raw`https://www.nhaccuatui.com/bai-hat/nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html`, __dirname).then(function (data) {
    console.log("hello abc" + data)

});

//
// var userDetails;
//
// function initialize() {
//     // Setting URL and headers for request
//     var options = {
//         url: 'https://api.github.com/users/tkssharma',
//         headers: {
//             'User-Agent': 'request'
//         }
//     };
//     // Return new promise
//     return new Promise(function (resolve, reject) {
//         // Do async job
//         request.get(options, function (err, resp, body) {
//             if (err) {
//                 reject(err);
//             } else {
//                 resolve(JSON.parse(body));
//             }
//         });
//     });
// }
//
// initialize().then(function (data) {
//     console.log(data);
// });


