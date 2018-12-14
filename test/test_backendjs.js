let {PythonShell} = require('python-shell');

var scripfile = __dirname + "//../backendcli.py";

var url = String.raw`https://www.nhaccuatui.com/bai-hat/nham-mat-thay-mua-he-nham-mat-thay-mua-he-ost-nguyen-ha.btmm6eYyZzW4.html`;


function download_mv(audioQuality, url, outpurdir) {
    console.log(outpurdir);
    console.log(url);
    var options = {
        mode: 'text',
        args: ['downloadcontent', audioQuality, url, outpurdir]
    };

    PythonShell.run(scripfile, options, function (err, result) {
        console.log("the script is exited ");
        if (err) {
            console.log(err);
            throw err;
        }
        console.log(result);
        return result;
    });
}

function create_youtube_mv(audiofile, bgimgfile, titleimg, titlecoordinate, subfile, affectfile, outputmv) {
    console.log("create youtube mv");
    var options = {
        mode: 'text',
        args: ['createytmv', audiofile, bgimgfile, titleimg, '--titlecoordinate', titlecoordinate, subfile, affectfile, outputmv]
    };

    PythonShell.run(scripfile, options, function (err, result) {
        console.log("the script is exited ");
        if (err) {
            console.log(err);
            throw err;
        }
        console.log(result);
        return result;
    });

}

/**
 * cralw nct lyric
 * example: crawl_nct_lyric(self.url, assfileoutput, "UTM Centur", "0x018CA7",  "250,180,530,200"
 * @param ncturl  nhaccuatui url : string
 * @param savefile output file (save file)
 * @param subfont font name : string
 * @param subcolor hex code of subcolor: string  0x018CA7
 * @param subrect string of x,y,w,h  =>  "250,180,530,200"
 */
function crawl_nct_lyric(ncturl, savefile, subfont, subcolor, subrect) {
    console.log("create youtube mv");
    var options = {
        mode: 'text',
        args: ['getsub', ncturl, savefile, subfont, subcolor, '--subrect', subrect]
    };
    PythonShell.run(scripfile, options, function (err, result) {
        console.log("the script is exited ");
        if (err) {
            console.log(err);
            throw err;
        }
        console.log(result);
        return result;
    });


}

download_mv(1, url, __dirname);
