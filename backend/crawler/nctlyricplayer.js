var NCTPlayer = function () {
    this.version = "0.2";
    this.debug = false;
    this.author = "HoanND - NhacCuaTui.com";
    this.open = true;
    this.currentModule = "";
    this.nctPlayerMp3 = new NCTPlayerMp3();
    this.pe = "nctPlayer";
    this.peConfig = {
        width: "100%",
        height: "100%",
        xmlURL: "test.xml",
        autoPlay: true,
        curPlayIndex: 0,
        currentDefault: 0,
        showControlBar: true,
        isShowNameSong: false,
        logoActive: true,
        fakeCLick: true,
        logoClickTarget: "_blank",
        volumeDefault: 1,
        timeDownVolume: 3,
        mp3ListAutoNext: true,
        pushGASecond: [],
        pushGAPercent: [],
        lyricStatus: true,
        lyricUrl: NCTInfo.ROOT_URL + "lyric/xml?type=2&key="
    };
    this.adsMp3 = {
        open: false,
        type: "mp3",
        link: "ads.xml",
        callNQC: true,
        callSpecialNQC: true,
        outOne: false,
        openAudioAds: false
    };
    this.load = function (a) {
        if (a == null || a == "") {
            a = "nctPlayer"
        }
        this.pe = a;
        __data[a] = {};
        __data[a].debug = this.debug;
        __data[a].peConfig = this.peConfig;
        __data[a].adsMp3 = this.adsMp3;
        __data[a].arrayPlaylist = [];
        __data[a].arrayPlaylistRandomed = [];
        document.getElementById(a).onselectstart = function () {
            return false
        }
        ;
        if (putils.isSafariMacOS11()) {
            __data[a].peConfig.autoPlay = false
        }
        $("#" + a).addClass("nctPlayer").width(this.peConfig.width).height(this.peConfig.height);
        __debug.log("Begin load player " + a, a);
        this.currentModule = "nctPlayerMp3";
        this.nctPlayerMp3.load(a);
        if (putils.isMobileDevice()) {
            if (__data[a].adsMp3.callNQC && typeof (runNQCAdv) != "undefined") {
                runNQCAdv();
                __data[a].adsMp3.callNQC = false
            }
            if (__data[a].adsMp3.outOne && typeof (loadAdsMp3Loaded) == "function") {
                loadAdsMp3Loaded()
            } else {
                __data[a].adsMp3.outOne = true
            }
            __data[a].peConfig.fakeCLick = false
        }
    }
    ;
    this.resize = function () {
        if (this.currentModule == "nctPlayerMp3") {
            this.nctPlayerMp3.resize()
        }
    }
    ;
    this.playIndex = function (a) {
        if (isNaN(a)) {
            a = 0
        } else {
            a = parseInt(a)
        }
        if (this.currentModule == "nctPlayerMp3") {
            this.nctPlayerMp3.playIndex(a)
        }
    }
    ;
    this.currentPlayingSecond = function () {
        var a = 0;
        if (this.currentModule == "nctPlayerMp3") {
            a = this.nctPlayerMp3.streamingMp3.getCurrentTime()
        }
        return a
    }
};
var NCTPlayerMp3 = function () {
    this.pe = "";
    this.peConfig = {};
    this.mainScreen = new __mainScreenMp3();
    this.controlbar = new __controlbarMp3();
    this.streamingMp3 = new __streamMp3();
    this.shortkey = new __shortKey();
    this.load = function (a) {
        __debug.log("NCTPlayerMp3.load", a);
        this.pe = a;
        this.peConfig = __data[a].peConfig;
        this.streamingMp3.curPlayIndex = this.peConfig.curPlayIndex;
        this.streamingMp3.quality = "default";
        if ($("#" + a).html(__renderMp3.renderPlayerMp3(a))) {
            var b = new __parseXMLMp3();
            b.load(a);
            b.parse(this)
        }
    }
    ;
    this.mainFunction = function () {
    }
    ;
    this.xmlParseComplete = function () {
        var a = this.pe;
        if ($("#playerMp3" + a).append(__renderMp3.renderMainScreen(a))) {
            this.streamingMp3.load(a);
            this.mainScreen.load(a);
            this.mainFunction();
            if (this.peConfig.showControlBar) {
                var b = false;
                if (typeof isPlayingPlaylist != "undefined" && isPlayingPlaylist == true) {
                    b = true
                }
                if ($("#playerMp3" + a).append(__renderMp3.renderControlbar(a, b))) {
                    this.controlbar.streamingMp3 = this.streamingMp3;
                    this.controlbar.load(a)
                }
            }
            this.shortkey.streamingMp3 = this.streamingMp3;
            this.shortkey.load(a)
        }
    }
    ;
    this.resize = function () {
    }
    ;
    this.playIndex = function (a) {
        this.streamingMp3.curPlayIndex = a;
        this.streamingMp3.renewStreamIndex(a)
    }
};
var __renderMp3 = {
    renderPlayerMp3: function (a) {
        var b = '<div id="playerMp3' + a + '" class="playerDiv"></div>';
        return b
    },
    renderMp3Tag: function (a) {
        var b = '<audio id="mp3' + a + '" -webkit-playsinline playsinline class="mp3Tag" preload="auto"><p>Trình duyệt của bạn quá cũ không hỗ trợ định dạng Mp3 này. Vui lòng nâng cấp trình duyệt.</p></audio>';
        return b
    },
    renderMainScreen: function (a) {
        var b = '<div id="mainScreen' + a + '" class="mainScreen">' + '<div id="coverImage' + a + '" class="coverImage"></div>' + '<div id="coverSinger' + a + '" class="coverSinger"></div>' + '<div id="avatarSinger' + a + '" class="avatarSinger"><a id="linkAvatarSinger' + a + '" class="linkAvatarSinger"></a></div>' + '<div id="arrowUp' + a + '" class="arrowUp"></div>' + '<div id="shadowSinger' + a + '" class="shadowSinger"></div>' + '<div id="nameSinger' + a + '" class="nameSinger"></div>' + this.renderMp3Tag(a) + '</div>';
        return b
    },
    renderControlbar: function (a, b) {
        var c = '<div id="controlbar' + a + '" class="controlbar">';
        if (b) {
            c += '<div id="prevButton' + a + '" class="prevButton"></div>'
        }
        c += '<div id="playButton' + a + '" class="playButton"></div>';
        if (b) {
            c += '<div id="nextButton' + a + '" class="nextButton"></div>'
        } else {
            c += '<div id="nextAutoPlayButton' + a + '" class="nextButtonAutoplay hide"></div>'
        }
        c += '<div id="volumeControl' + a + '" class="volume">' + '<div id="volume' + a + '" class="muteButton"></div>' + '<div id="volumeCurrent' + a + '" class="volumeCurrent">' + '<div id="volumeCurrentInside' + a + '" class="volumeCurrentInside"></div>' + '</div>' + '<div id="volumeSlider' + a + '" class="volumeSlider">' + '<div id="volumeSliderClick' + a + '" class="volumeSliderCurrent">' + '<div id="volumeSliderCurrent' + a + '" class="volumeSliderCurrentInside"></div>' + '<div id="volumeSliderHolder' + a + '" class="volumeSliderHolder"><div class="volumeSliderHolderInside"></div></div>' + '</div>' + '</div>' + '</div>' + '<div id="timeCounter' + a + '" class="timeCounter">' + '<div id="utCurrentTime' + a + '" class="utCurrentTime">00:00</div>' + '<div class="timeCounterSlash">/</div>' + '<div id="utTotalTime' + a + '" class="utTotalTime">00:00</div>' + '</div>' + '<div id="logo' + a + '" class="logoNCT"><a></a></div>' + '<div id="timeSlider' + a + '" class="timeSlider">' + '<div class="timeSliderBuffer">' + '<div id="timeSliderBuffer' + a + '" class="timeSliderBufferInside"></div>' + '</div>' + '<div id="timeSliderCurrent' + a + '" class="timeSliderCurrent"></div>' + '<div id="timeSliderHolder' + a + '" class="timeSliderHolder">' + '<div class="timeSliderHolderInside"></div>' + '</div>' + '</div>' + '<div id="switchQuality' + a + '" class="switchQuality">' + '<div id="switchQualityText' + a + '" class="switchQualityText"><span id="txtQLT' + a + '">128kbps</span><span class="iconhd">VIP</span></div>' + '<div id="boxSwitchQuality' + a + '" class="boxSwitchQuality">' + '<div id="SwitchQualityText' + a + '" class="SwitchQualityText">Chất lượng</div>' + '<div id="SwitchQualityHigh' + a + '" class="switchQualityCode">320kbps<span class="iconhd">VIP</span></div>' + '<div id="SwitchQualityPU' + a + '" class="switchQualityCode" style="color: #585858">320kbps<span class="iconhd" style="color: #585858">VIP</span></div>' + '<div id="SwitchQualityDefault' + a + '" class="switchQualityCode">128kbps</div>' + '</div>' + '</div>' + '<div id="repeatButton' + a + '" class="repeatButton hide">' + '<div id="repeatTooltip' + a + '" class="boxTooltipRepeat boxTooltip">Lặp 1 bài</div>' + '</div>';
        if (b) {
            c += '<div id="randomButton' + a + '" class="randomButton">' + '<div id="randomTooltip' + a + '" class="boxTooltipRandom boxTooltip">Ngẫu nhiên</div>' + '</div>'
        }
        c += '</div></div>' + '<div class="mp3LyricBox hide" id="lyricBox' + a + '">' + '<div class="mp3Kara" id="mp3Kara1' + a + '"></div><div class="clr"></div>' + '<div class="mp3Kara mp3Kara2" id="mp3Kara2' + a + '"></div>' + '</div>';
        return c
    },
    renderErrorNotification: function (a, b, c) {
        $("#errorNotification" + a).remove();
        var d = '<div id="errorNotification' + a + '" class="errorNotification"><div class="boxErrorNotification">' + b + '</div></div>';
        return d
    },
};
var __debug = {
    log: function (a, b) {
        if (__data[b].debug) {
            console.log(a)
        }
    },
    info: function (a, b) {
        if (__data[b].debug) {
            console.info(a)
        }
    }
};
var putils = {
    generateAdsParam: function (a) {
        var b = "";
        var c = new Date();
        var d = new Date(1970, 0, 1, 0, 0, 0, 0);
        var e = c - d;
        var f = "34vcgj8,ggh@344567gfvntrt!@46";
        var g = "";
        e = Math.round(e / 1000);
        g = md5(a + e + f);
        b += "type=" + a + "&time=" + e + "&token=" + g;
        return b
    },
    arrayRandom: "",
    randomIntFromInterval: function (a, b) {
        return Math.floor(Math.random() * (b - a + 1) + a)
    },
    replaceTwoObject: function (a, b) {
        var c = {};
        return c
    },
    addZero: function (a, b) {
        var s = a + "";
        while (s.length < b)
            s = "0" + s;
        return s
    },
    getTypeVideo: function (a) {
        try {
            if (a.lastIndexOf("m3u8") == a.length - 4) {
                return "m3u8"
            }
            return "mp4"
        } catch (e) {
            console.log("checkTypeVideo" + e)
        }
    },
    formatTime: function (a) {
        if (!isNaN(a)) {
            a = Math.round(a);
            minutes = Math.floor(a / 60);
            minutes = (minutes >= 10) ? minutes : "0" + minutes;
            a = Math.floor(a % 60);
            a = (a >= 10) ? a : "0" + a;
            return minutes + ":" + a
        } else {
            return ""
        }
    },
    formatNumber: function (a) {
        if (typeof a !== "undefined" && a !== null && a !== "") {
            var b = a.toString();
            if (b.length > 3) {
                var c = "";
                var d = b.length % 3;
                for (var i = 0; i < b.length; i++) {
                    c += b.charAt(i);
                    if ((i + 1) % 3 == d && i !== (b.length - 1))
                        c += "."
                }
                return c
            }
            return a
        } else {
            return 0
        }
    },
    isiPhone: function () {
        return ((navigator.userAgent.toLowerCase().indexOf("iphone") != -1) || (navigator.userAgent.toLowerCase().indexOf("ipod") != -1))
    },
    isBB10: function () {
        return (navigator.userAgent.toLowerCase().indexOf("blackberry") != -1 && navigator.platform.toLowerCase().indexOf("10") != -1)
    },
    isiPad: function () {
        return (navigator.userAgent.toLowerCase().indexOf("ipad") != -1)
    },
    isAndroid: function () {
        return ((navigator.userAgent.toLowerCase().indexOf("android") != -1) || (navigator.platform.toLowerCase().indexOf("android") != -1))
    },
    isFirefox: function () {
        return (navigator.userAgent.toLowerCase().indexOf("firefox") != -1)
    },
    isAndroid4: function () {
        var a = navigator.userAgent;
        if (a.toLowerCase().indexOf("android") >= 0) {
            var b = parseFloat(a.slice(a.toLowerCase().indexOf("android") + 8));
            if (b >= 4) {
                return true
            }
        }
        return false
    },
    isWP8: function () {
        return (((navigator.userAgent.toLowerCase().indexOf("windows phone") != -1) || (navigator.userAgent.toLowerCase().indexOf("windowsphone") != -1) || (navigator.platform.toLowerCase().indexOf("wp") != -1)) && (navigator.userAgent.toLowerCase().indexOf("8") != -1))
    },
    isWP7: function () {
        return (((navigator.userAgent.toLowerCase().indexOf("windows phone") != -1) || (navigator.userAgent.toLowerCase().indexOf("windowsphone") != -1) || (navigator.platform.toLowerCase().indexOf("wp") != -1)) && (navigator.userAgent.toLowerCase().indexOf("7") != -1))
    },
    isSafari: function () {
        return (navigator.userAgent.toLowerCase().indexOf("applewebkit") != -1 && navigator.userAgent.toLowerCase().indexOf("safari") == -1)
    },
    isMobileDevice: function () {
        var a = false;
        if (putils.isiPad() || putils.isiPhone() || putils.isAndroid() || putils.isWP7() || putils.isWP8() || putils.isBB10()) {
            a = true
        }
        return a
    },
    isSafariMacOS11: function () {
        var a = navigator.userAgent.toLowerCase().indexOf("mac os x") != -1 && navigator.userAgent.toLowerCase().indexOf("safari") != -1;
        if (a) {
            console.log("IS MAC OS SAFARI 11", true)
        }
        return a
    },
    support: {
        touch: (window.Modernizr && Modernizr.touch === true) || (function () {
                return !!(("ontouchstart" in window) || window.DocumentTouch && document instanceof DocumentTouch)
            }
        )(),
        transforms3d: (window.Modernizr && Modernizr.csstransforms3d === true) || (function () {
                var a = document.createElement('div').style;
                return ("webkitPerspective" in a || "MozPerspective" in a || "OPerspective" in a || "MsPerspective" in a || "perspective" in a)
            }
        )(),
        transforms: (window.Modernizr && Modernizr.csstransforms === true) || (function () {
                var a = document.createElement('div').style;
                return ('transform' in a || 'WebkitTransform' in a || 'MozTransform' in a || 'msTransform' in a || 'MsTransform' in a || 'OTransform' in a)
            }
        )(),
        transitions: (window.Modernizr && Modernizr.csstransitions === true) || (function () {
                var a = document.createElement('div').style;
                return ('transition' in a || 'WebkitTransition' in a || 'MozTransition' in a || 'msTransition' in a || 'MsTransition' in a || 'OTransition' in a)
            }
        )(),
        tagVideo: function () {
            var a = document.createElement("video");
            var b = (a.play) ? true : false;
            if (window.navigator.platform.toLowerCase().indexOf("linux") != -1 && putils.isFirefox()) {
                b = false
            }
            return b
        },
        tagAudio: function () {
            var b = document.createElement("audio");
            var c = (b.play) ? true : false;
            if (c) {
                var a = document.createElement('audio');
                return (!!(a.canPlayType && a.canPlayType('audio/mpeg;').replace(/no/, '')))
            } else {
                return false
            }
        }
    },
    browser: {
        ie8: (function () {
                var a = -1;
                if (navigator.appName == 'Microsoft Internet Explorer') {
                    var b = navigator.userAgent;
                    var c = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
                    if (c.exec(b) != null)
                        a = parseFloat(RegExp.$1)
                }
                return a != -1 && a < 9
            }
        )(),
        ie10: window.navigator.msPointerEnabled,
        ie11: window.navigator.pointerEnabled,
        isIE: function () {
            return navigator.userAgent.toLowerCase().indexOf("msie") != -1 || navigator.userAgent.toLowerCase().indexOf(".net") != -1 || putils.isWP8() || putils.isWP7()
        }
    },
    mouseStart: function () {
        if (this.browser.ie10)
            return 'MSPointerDown';
        if (this.browser.ie11)
            return 'pointerdown';
        return 'mousedown'
    },
    touchStart: function () {
        var a = ['MSPointerDown', 'MSPointerMove', 'MSPointerUp'];
        if (this.browser.ie11)
            a = ['pointerdown', 'pointermove', 'pointerup'];
        return this.support.touch ? 'touchstart' : a[0]
    },
    touchEnd: function () {
        var a = ['MSPointerDown', 'MSPointerMove', 'MSPointerUp'];
        if (this.browser.ie11)
            a = ['pointerdown', 'pointermove', 'pointerup'];
        return this.support.touch ? 'touchend' : a[2]
    },
    touchMove: function () {
        var a = ['MSPointerDown', 'MSPointerMove', 'MSPointerUp'];
        if (this.browser.ie11)
            a = ['pointerdown', 'pointermove', 'pointerup'];
        return this.support.touch ? 'touchmove' : a[1]
    },
    setCookie: function (a, b, c) {
        var d = new Date();
        d.setTime(d.getTime() + (c * 24 * 60 * 60 * 1000));
        var e = "expires=" + d.toUTCString();
        document.cookie = a + "=" + b + "; " + e
    },
    getCookie: function (a) {
        var b = a + "=";
        var d = document.cookie.split(';');
        for (var i = 0; i < d.length; i++) {
            var c = d[i];
            while (c.charAt(0) == ' ')
                c = c.substring(1);
            if (c.indexOf(b) != -1)
                return c.substring(b.length, c.length)
        }
        return ""
    },
    parseXml: function (a) {
        try {
            return (new window.DOMParser()).parseFromString(a, "text/xml")
        } catch (e) {
            console.log(e)
        }
        return ""
    },
    supportFlash: function () {
        var a = false;
        try {
            var b = new ActiveXObject('ShockwaveFlash.ShockwaveFlash');
            if (b) {
                a = true
            }
        } catch (e) {
            if (navigator.mimeTypes && typeof navigator.mimeTypes['application/x-shockwave-flash'] != "undefined" && navigator.mimeTypes['application/x-shockwave-flash'].enabledPlugin) {
                a = true
            }
        }
        return a
    },
    handleErrorImage: function (a) {
        if ((typeof (a.onerror) === 'function' && state === 'fail') || (a.width === 0)) {
            a.src = "http://stc.id.nixcdn.com/v/images/img-video-full.png"
        }
    },
    rc4: function (a, b) {
        var s = [], j = 0, x, res = '';
        for (var i = 0; i < 256; i++) {
            s[i] = i
        }
        for (i = 0; i < 256; i++) {
            j = (j + s[i] + a.charCodeAt(i % a.length)) % 256;
            x = s[i];
            s[i] = s[j];
            s[j] = x
        }
        i = 0;
        j = 0;
        for (var y = 0; y < b.length; y++) {
            i = (i + 1) % 256;
            j = (j + s[i]) % 256;
            x = s[i];
            s[i] = s[j];
            s[j] = x;
            res += String.fromCharCode(b.charCodeAt(y) ^ s[(s[i] + s[j]) % 256])
        }
        return res
    },
    hexFromString: function (a) {
        a += 'nct';
        var b = [];
        for (var i = 0, l = a.length; i < l; i++) {
            var c = Number(a.charCodeAt(i)).toString(16);
            b.push(c)
        }
        return b.join('')
    },
    hexToArray: function (a) {
        var b = [];
        while (a.length >= 2) {
            b.push(parseInt(a.toString().substring(0, 2), 16));
            a = a.toString().substring(2, a.length)
        }
        return b
    },
    hexFromArray: function (a) {
        var s = '';
        for (i = 0; i < a.length; i++) {
            try {
                if (i == 0) {
                    if (typeof utf8char[a[i]] != "undefined") {
                        s += utf8char[a[i] + ""]
                    }
                } else {
                    if (a[i] >= 224) {
                        if (utf8char[a[i] + " " + a[i + 1] + " " + a[i + 2]] != undefined) {
                            s += utf8char[a[i] + " " + a[i + 1] + " " + a[i + 2]]
                        }
                    } else if (a[i] >= 128) {
                        if (utf8char[a[i] + " " + a[i + 1]] != undefined) {
                            s += utf8char[a[i] + " " + a[i + 1]]
                        }
                    } else {
                        if ((i > 0 && a[i - 1] < 128) || i > 1 && a[i - 2] < 200) {
                            if (utf8char[a[i]] != undefined) {
                                s += utf8char[a[i] + ""]
                            }
                        }
                    }
                }
            } catch (e) {
                console.log(e)
            }
        }
        var b = "";
        for (i = 0; i < s.length; i++) {
            if (i > 0 && s.charAt(i) == "[" && s.charAt(i - 1) != "]") {
                b += "\n" + s.charAt(i)
            } else {
                b += s.charAt(i)
            }
        }
        return b
    },
    getQueryVariable: function (a, b) {
        if (a.indexOf("?") > -1 && typeof a.split('?')[1] != 'undefined') {
            var c = a.split('?')[1];
            var d = c.split('&');
            for (var i = 0; i < d.length; i++) {
                var e = d[i].split('=');
                if (decodeURIComponent(e[0]) == b) {
                    return decodeURIComponent(e[1])
                }
            }
        }
        return ""
    }
};
var arc4 = function () {
    this.i = 0;
    this.j = 0;
    this.S = [];
    this.psize = 256;
    this.load = function (a) {
        this.S = [];
        if (a) {
            this.init(a)
        }
    }
    ;
    this.init = function (a) {
        var i = 0;
        var j = 0;
        var t = 0;
        for (i = 0; i < 256; ++i) {
            this.S[i] = i
        }
        j = 0;
        for (i = 0; i < 256; ++i) {
            j = (j + this.S[i] + a[i % a.length]) & 255;
            t = this.S[i];
            this.S[i] = this.S[j];
            this.S[j] = t
        }
        this.i = 0;
        this.j = 0
    }
    ;
    this.next = function () {
        var t = 0;
        this.i = (this.i + 1) & 255;
        this.j = (this.j + this.S[this.i]) & 255;
        t = this.S[this.i];
        this.S[this.i] = this.S[this.j];
        this.S[this.j] = t;
        return this.S[(t + this.S[this.i]) & 255]
    }
    ;
    this.getBlockSize = function () {
        return 1
    }
    ;
    this.encrypt = function (a) {
        var i = 0;
        while (i < a.length) {
            a[i++] ^= this.next()
        }
        return a
    }
    ;
    this.decrypt = function (a) {
        return this.encrypt(a)
    }
    ;
    this.dispose = function () {
        var i = 0;
        if (this.S != null) {
            for (i = 0; i < this.S.length; i++) {
                this.S[i] = Math.random() * 256
            }
            this.S.length = 0;
            this.S = null
        }
        this.i = 0;
        this.j = 0
    }
};
var md5 = (function () {
        function e(e, t) {
            var o = e[0]
                , u = e[1]
                , a = e[2]
                , f = e[3];
            o = n(o, u, a, f, t[0], 7, -680876936);
            f = n(f, o, u, a, t[1], 12, -389564586);
            a = n(a, f, o, u, t[2], 17, 606105819);
            u = n(u, a, f, o, t[3], 22, -1044525330);
            o = n(o, u, a, f, t[4], 7, -176418897);
            f = n(f, o, u, a, t[5], 12, 1200080426);
            a = n(a, f, o, u, t[6], 17, -1473231341);
            u = n(u, a, f, o, t[7], 22, -45705983);
            o = n(o, u, a, f, t[8], 7, 1770035416);
            f = n(f, o, u, a, t[9], 12, -1958414417);
            a = n(a, f, o, u, t[10], 17, -42063);
            u = n(u, a, f, o, t[11], 22, -1990404162);
            o = n(o, u, a, f, t[12], 7, 1804603682);
            f = n(f, o, u, a, t[13], 12, -40341101);
            a = n(a, f, o, u, t[14], 17, -1502002290);
            u = n(u, a, f, o, t[15], 22, 1236535329);
            o = r(o, u, a, f, t[1], 5, -165796510);
            f = r(f, o, u, a, t[6], 9, -1069501632);
            a = r(a, f, o, u, t[11], 14, 643717713);
            u = r(u, a, f, o, t[0], 20, -373897302);
            o = r(o, u, a, f, t[5], 5, -701558691);
            f = r(f, o, u, a, t[10], 9, 38016083);
            a = r(a, f, o, u, t[15], 14, -660478335);
            u = r(u, a, f, o, t[4], 20, -405537848);
            o = r(o, u, a, f, t[9], 5, 568446438);
            f = r(f, o, u, a, t[14], 9, -1019803690);
            a = r(a, f, o, u, t[3], 14, -187363961);
            u = r(u, a, f, o, t[8], 20, 1163531501);
            o = r(o, u, a, f, t[13], 5, -1444681467);
            f = r(f, o, u, a, t[2], 9, -51403784);
            a = r(a, f, o, u, t[7], 14, 1735328473);
            u = r(u, a, f, o, t[12], 20, -1926607734);
            o = i(o, u, a, f, t[5], 4, -378558);
            f = i(f, o, u, a, t[8], 11, -2022574463);
            a = i(a, f, o, u, t[11], 16, 1839030562);
            u = i(u, a, f, o, t[14], 23, -35309556);
            o = i(o, u, a, f, t[1], 4, -1530992060);
            f = i(f, o, u, a, t[4], 11, 1272893353);
            a = i(a, f, o, u, t[7], 16, -155497632);
            u = i(u, a, f, o, t[10], 23, -1094730640);
            o = i(o, u, a, f, t[13], 4, 681279174);
            f = i(f, o, u, a, t[0], 11, -358537222);
            a = i(a, f, o, u, t[3], 16, -722521979);
            u = i(u, a, f, o, t[6], 23, 76029189);
            o = i(o, u, a, f, t[9], 4, -640364487);
            f = i(f, o, u, a, t[12], 11, -421815835);
            a = i(a, f, o, u, t[15], 16, 530742520);
            u = i(u, a, f, o, t[2], 23, -995338651);
            o = s(o, u, a, f, t[0], 6, -198630844);
            f = s(f, o, u, a, t[7], 10, 1126891415);
            a = s(a, f, o, u, t[14], 15, -1416354905);
            u = s(u, a, f, o, t[5], 21, -57434055);
            o = s(o, u, a, f, t[12], 6, 1700485571);
            f = s(f, o, u, a, t[3], 10, -1894986606);
            a = s(a, f, o, u, t[10], 15, -1051523);
            u = s(u, a, f, o, t[1], 21, -2054922799);
            o = s(o, u, a, f, t[8], 6, 1873313359);
            f = s(f, o, u, a, t[15], 10, -30611744);
            a = s(a, f, o, u, t[6], 15, -1560198380);
            u = s(u, a, f, o, t[13], 21, 1309151649);
            o = s(o, u, a, f, t[4], 6, -145523070);
            f = s(f, o, u, a, t[11], 10, -1120210379);
            a = s(a, f, o, u, t[2], 15, 718787259);
            u = s(u, a, f, o, t[9], 21, -343485551);
            e[0] = m(o, e[0]);
            e[1] = m(u, e[1]);
            e[2] = m(a, e[2]);
            e[3] = m(f, e[3])
        }

        function t(e, t, n, r, i, s) {
            t = m(m(t, e), m(r, s));
            return m(t << i | t >>> 32 - i, n)
        }

        function n(e, n, r, i, s, o, u) {
            return t(n & r | ~n & i, e, n, s, o, u)
        }

        function r(e, n, r, i, s, o, u) {
            return t(n & i | r & ~i, e, n, s, o, u)
        }

        function i(e, n, r, i, s, o, u) {
            return t(n ^ r ^ i, e, n, s, o, u)
        }

        function s(e, n, r, i, s, o, u) {
            return t(r ^ (n | ~i), e, n, s, o, u)
        }

        function o(t) {
            var n = t.length, r = [1732584193, -271733879, -1732584194, 271733878], i;
            for (i = 64; i <= t.length; i += 64) {
                e(r, u(t.substring(i - 64, i)))
            }
            t = t.substring(i - 64);
            var s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
            for (i = 0; i < t.length; i++)
                s[i >> 2] |= t.charCodeAt(i) << (i % 4 << 3);
            s[i >> 2] |= 128 << (i % 4 << 3);
            if (i > 55) {
                e(r, s);
                for (i = 0; i < 16; i++)
                    s[i] = 0
            }
            s[14] = n * 8;
            e(r, s);
            return r
        }

        function u(e) {
            var t = [], n;
            for (n = 0; n < 64; n += 4) {
                t[n >> 2] = e.charCodeAt(n) + (e.charCodeAt(n + 1) << 8) + (e.charCodeAt(n + 2) << 16) + (e.charCodeAt(n + 3) << 24)
            }
            return t
        }

        function c(e) {
            var t = ""
                , n = 0;
            for (; n < 4; n++)
                t += a[e >> n * 8 + 4 & 15] + a[e >> n * 8 & 15];
            return t
        }

        function h(e) {
            for (var t = 0; t < e.length; t++)
                e[t] = c(e[t]);
            return e.join("")
        }

        function d(e) {
            return h(o(unescape(encodeURIComponent(e))))
        }

        function m(e, t) {
            return e + t & 4294967295
        }

        var a = "0123456789abcdef".split("");
        return d
    }
)();
var objectFlashMovie = {
    playSound: function (a) {
        player.playIndex(a)
    }
};

function flashMovie(a) {
    if (player.open) {
        return objectFlashMovie
    } else {
        if (window.document[a]) {
            return window.document[a]
        } else {
            return document.getElementById(a)
        }
    }
}

var __streamMp3 = function () {
    this.pe = "";
    this.listMp3 = [];
    this.item = {};
    this.mp3Interval = null;
    this.mp3IntervalTimeout = null;
    this.curPlayIndex = 0;
    this.quality = "default";
    this.playType = "mp3";
    this.location = "";
    this.bufferTime = 5;
    this.parseLyric = new __parseKaraoke();
    this.lyric = new __karaoke();
    this.load = function (a) {
        __debug.log("StreamMp3.load", a);
        this.pe = a;
        if (__data[this.pe].peConfig.lyricStatus) {
            $("#lyricBox" + this.pe).removeClass("hide");
            this.lyric.load(this.pe);
            this.lyric.parseLyric = this.parseLyric
        }
        var b = putils.getCookie("qualityPlayerMp3");
        if (typeof b != "undefined") {
            if (b == "high") {
                this.quality = "high";
                __data[this.pe].curQuality = "high"
            } else {
                this.quality = "default";
                __data[this.pe].curQuality = "default"
            }
            $("#switchQuality" + this.pe).trigger("resetSwitch")
        }
        this.listMp3 = __data[a].mp3;
        if (typeof this.listMp3[this.curPlayIndex] != "undefined" && this.listMp3[this.curPlayIndex] != null) {
            this.item = this.listMp3[this.curPlayIndex];
            if (typeof this.item != "undefined" && this.item != null) {
                this.renSource(this.item);
                this.mainFunction()
            }
        }
    }
    ;
    this.renSource = function (c) {
        var d = this;
        __data[this.pe].curMp3Item = c;
        __data[this.pe].curMp3Item.curPlayIndex = this.curPlayIndex;
        __data[this.pe].curMp3Item.currentTime = 0;
        __data[this.pe].curMp3Item.duration = 0;
        __data[this.pe].curMp3Item.played = false;
        __data[this.pe].curMp3Item.seekInBuffered = 0;
        __data[this.pe].curMp3Item.blCheck80 = true;
        __data[this.pe].curMp3Item.blCheck60s = true;
        __data[this.pe].curMp3Item.timePlayed = 0;
        __data[this.pe].curMp3Item.tempPushGASecond = Object.create(__data[this.pe].peConfig.pushGASecond);
        __data[this.pe].curMp3Item.temppushGAPercent = Object.create(__data[this.pe].peConfig.pushGAPercent);
        var e = putils.getCookie("qualityPlayerMp3");
        if (typeof e != "undefined") {
            if (e == "high") {
                this.quality = "high";
                __data[this.pe].curQuality = "high"
            }
        }
        if (this.quality == "high") {
            this.location = c.highquality
        } else {
            this.location = c.location
        }
        if (this.location == "") {
            this.location = c.location;
            this.quality = "default";
            __data[this.pe].curQuality = "default"
        }
        this.parseLyric.load(this.pe);
        this.playType = "mp3";
        $("#mp3" + this.pe + ' source').each(function (a, b) {
            $(this).attr('src', '')
        });
        if (this.location.indexOf("googleapis.com") != -1) {
            document.getElementById("mp3" + this.pe).src = $.trim(this.location)
        } else if (this.location.indexOf("?") != -1) {
            $("#mp3" + this.pe).html('<source src="' + $.trim(this.location) + "&t=" + (new Date()).getTime() + '"/>')
        } else {
            $("#mp3" + this.pe).html('<source src="' + $.trim(this.location) + "?t=" + (new Date()).getTime() + '"/>')
        }
        if (c.coverimage != "") {
            $("#coverImage" + this.pe).css("background", "url('" + c.coverimage + "')  no-repeat left center").css("-webkit-background-size", "contain").css("-moz-background-size", "contain").css("background-size", "contain").css("-o-background-size", "contain")
        } else {
            $("#coverImage" + this.pe).attr("style", "")
        }
        $("#coverSinger" + this.pe).css("background", "url('" + c.bgimage + "')  no-repeat center top").css("-webkit-background-size", "cover").css("-moz-background-size", "cover").css("background-size", "cover").css("-o-background-size", "cover");
        $("#avatarSinger" + this.pe).css("background", "url('" + c.avatar + "')  no-repeat center center").css("-webkit-background-size", "cover").css("-moz-background-size", "cover").css("background-size", "cover").css("-o-background-size", "cover");
        $("#linkAvatarSinger" + this.pe).attr("href", c.info);
        if (!__data[this.pe].peConfig.isShowNameSong) {
            $("#nameSinger" + this.pe).html('<h2><a href="' + c.newtab + '" target="_blank">' + c.creator + '</a></h2>')
        } else {
            $("#arrowUp" + this.pe).css("top", "163px");
            $("#shadowSinger" + this.pe).css("top", "44px");
            $("#avatarSinger" + this.pe).css("top", "20px");
            $("#nameSinger" + this.pe).css("top", "100px").html('<h2><a href="' + c.info + '" target="_blank" style="font-weight: 400; color:#E8E8E8; font-size: 18px;">' + c.title + '</a></h2><h3 style="margin-top: 5px;"><a href="' + c.newtab + '" target="_blank" style="color: #C2C2C2; font-size: 14px;">' + c.creator + '</a></h3>')
        }
        if (putils.getQueryVariable(window.location.href.toString(), "debug") == "true") {
            console.log(this.location)
        }
        $("#switchQuality" + this.pe).trigger("resetSwitch");
        if (typeof getSongIndex != "undefined") {
            getSongIndex(this.curPlayIndex, this.pe)
        }
        if (__data[this.pe].adsMp3.type == "playlist") {
            $("#mainScreen" + this.pe).trigger("resetAds")
        }
    }
    ;
    this.mainFunction = function () {
        var k = this;
        var l = 0;
        $("#mp3" + this.pe).bind("playMp3", function () {
            __data[k.pe].curMp3Item.played = true;
            k.play();
            __data[k.pe].curMp3Item.tempBuffer = 0;
            clearTimeout(k.mp3IntervalTimeout);
            k.mp3Interval = function () {
                k.processBuffering();
                k.mp3IntervalTimeout = setTimeout(function () {
                    k.mp3Interval()
                }, 500)
            }
            ;
            k.mp3Interval();
            __data[k.pe].curMp3Item.timePlayedCheck = true;
            if ($("#a_ads_media").size() > 0) {
                $("#mp3" + k.pe).trigger("pauseMp3")
            }
        }).bind("pauseMp3", function () {
            __data[k.pe].curMp3Item.played = false;
            k.pause();
            clearInterval(k.mp3Interval);
            __data[k.pe].curMp3Item.timePlayedCheck = false
        }).bind("nextMp3", function () {
            k.next()
        }).bind("prevMp3", function () {
            k.prev()
        }).bind("playing", function (e) {
            __data[k.pe].curMp3Item.timePlayedCheck = true;
            $("#mp3" + k.pe).trigger("totalTimeUpdate")
        }).bind("error", function (e) {
            k.error(e)
        }).on("play", function (e) {
            if (putils.isSafariMacOS11()) {
                $("#mp3" + k.pe).trigger("playMp3")
            }
        }).bind("loadeddata", function (e) {
            if (putils.isSafariMacOS11()) {
                if ($("#titleAutoSong" + k.pe).size() == 0) {
                    try {
                        document.getElementById("mp3" + k.pe).play()
                    } catch (e) {
                    }
                }
            } else {
                console.log(__data[k.pe].peConfig.autoPlay);
                if (__data[k.pe].peConfig.autoPlay && !putils.isMobileDevice() && $("#titleAutoSong" + k.pe).size() == 0) {
                    $("#mp3" + k.pe).trigger("playMp3");
                    if (!putils.isiPad() && !putils.isiPhone()) {
                        $("#mp3" + k.pe + " source").remove()
                    }
                } else {
                    __data[k.pe].peConfig.autoPlay = true;
                    if (!putils.isiPad() && !putils.isiPhone()) {
                        $("#mp3" + k.pe).trigger("pauseMp3")
                    }
                }
            }
            if (typeof __data[k.pe] != "undefined" && typeof __data[k.pe].curMp3Item.reloadTime != "undefined" && __data[k.pe].curMp3Item.reloadTime > 0) {
                k.seek(parseFloat(__data[k.pe].curMp3Item.reloadTime / document.getElementById("mp3" + k.pe).duration * 100).toFixed(3));
                __data[k.pe].curMp3Item.reloadTime = 0
            } else if (parseInt(__data[k.pe].peConfig.currentDefault) > 0) {
                k.seek(parseFloat(__data[k.pe].peConfig.currentDefault / document.getElementById("mp3" + k.pe).duration * 100).toFixed(3));
                __data[k.pe].peConfig.currentDefault = 0
            }
            if (!putils.isMobileDevice()) {
                if (__data[k.pe].adsMp3.outOne && typeof (loadAdsMp3Loaded) == "function") {
                    loadAdsMp3Loaded()
                } else {
                    __data[k.pe].adsMp3.outOne = true
                }
            }
            var b = putils.getCookie("volume");
            var c = putils.getCookie("volumeMute");
            if (typeof c != 'undefined' && c == "1") {
                $("#volume" + k.pe).parent().addClass("mute");
                $("#volumeCurrent" + k.pe).addClass("hide")
            } else if (typeof b != 'undefined' && b != "") {
                $("#volume" + k.pe).parent().removeClass("mute");
                $("#volumeCurrent" + k.pe).removeClass("hide");
                k.setVolume(b / 100)
            } else {
                $("#volume" + k.pe).parent().removeClass("mute");
                $("#volumeCurrent" + k.pe).removeClass("hide");
                k.setVolume(1)
            }
            try {
                var d = {
                    action: "getInfoTracking",
                    t: "song",
                    key: __data[k.pe].curMp3Item.key,
                    mineKey: NCTInfo.mineKey
                };
                var f = "repeat_one";
                if (__data[k.pe].peConfig.repeatStatus == "no") {
                    f = "not_repeat"
                } else if (__data[k.pe].peConfig.repeatStatus == "no") {
                    f = "repeat_all"
                }
                var g = __data[k.pe].curQuality;
                var h = document.getElementById("mp3" + k.pe).duration;
                var i = document.getElementById("mp3" + k.pe).paused;
                var j = typeof (idDownloadTracking) != "undefined" && window.location.href.indexOf("/playlist/") != -1 ? idDownloadTracking : "null";
                $.post(NCTInfo.ROOT_URL + "ajax/playlist", d, function (a) {
                    if (i) {
                        trackingSmarty.mp3_player_stop(a.data.id_tracking, j, f, "null", "null", h, g)
                    } else {
                        trackingSmarty.mp3_player_play(a.data.id_tracking, j, f, "null", "null", h, g)
                    }
                }, "json")
            } catch (e) {
            }
        });
        var m = false;
        $("#mp3" + this.pe).bind("ended", function () {
            console.warn("ended");
            __data[k.pe].curMp3Item.blCheck80 = true;
            __data[k.pe].curMp3Item.blCheck60s = true;
            __data[k.pe].curMp3Item.timePlayed = 0;
            __data[k.pe].curMp3Item.tempPushGASecond = Object.create(__data[k.pe].peConfig.pushGASecond);
            __data[k.pe].curMp3Item.temppushGAPercent = Object.create(__data[k.pe].peConfig.pushGAPercent);
            var a = 0;
            var b = 0;
            var c = false;
            if (__data[k.pe].peConfig.randomListPlayer) {
                if (__data[k.pe].arrayPlaylist.length <= 0) {
                    if (m) {
                        c = true
                    }
                    m = true;
                    k.getArrayPlaylist(k.pe)
                }
                a = __data[k.pe].arrayPlaylist[b];
                __data[k.pe].arrayPlaylist.splice(b, 1)
            } else {
                a = parseInt(__data[k.pe].curMp3Item.curPlayIndex) + 1
            }
            if (__data[k.pe].peConfig.repeatStatus == "one") {
                k.renewStreamIndex(k.curPlayIndex)
            } else {
                k.curPlayIndex = a;
                k.renewStreamIndex(k.curPlayIndex)
            }
            __data[k.pe].curMp3Item.timePlayedCheck = false;
            __data[k.pe].curMp3Item.timePlayed = 0;
            var d = false;
            goURLAfterAudioAds = false;
            l = putils.getCookie("showAudioAds");
            if (l == "")
                l = 0;
            if (l == 1 && __data[k.pe].adsMp3.openAudioAds && putils.getCookie("NCT_ONOFF_ADV") != "1") {
                if (typeof playerAudioAds != "undefined") {
                    d = true;
                    playerAudioAds();
                    putils.setCookie("showAudioAds", 0, 7)
                }
            } else {
                putils.setCookie("showAudioAds", 1, 7)
            }
            if (__data[k.pe].peConfig.repeatStatus != "one") {
                if (typeof autoplay != "undefined" && typeof autoplay.optionAutoplay != "undefined" && autoplay.optionAutoplay == true && __data[k.pe].adsMp3.type == "playlist") {
                    if (k.listMp3.length == 1) {
                        if (typeof autoplay.url != "undefined" && autoplay.url != "") {
                            goURLAfterAudioAds = true;
                            if (!d) {
                                $("#mp3" + k.pe).trigger("pauseMp3");
                                window.location = autoplay.url
                            }
                        }
                    } else if (__data[k.pe].peConfig.randomListPlayer) {
                        if (c) {
                            if (typeof autoplay.url != "undefined" && autoplay.url != "") {
                                goURLAfterAudioAds = true;
                                if (!d) {
                                    $("#mp3" + k.pe).trigger("pauseMp3");
                                    window.location = autoplay.url
                                }
                            }
                        }
                    } else if (__data[k.pe].curMp3Item.curPlayIndex == 0) {
                        if (typeof autoplay.url != "undefined" && autoplay.url != "") {
                            goURLAfterAudioAds = true;
                            if (!d) {
                                $("#mp3" + k.pe).trigger("pauseMp3");
                                window.location = autoplay.url
                            }
                        }
                    }
                }
            }
            if (typeof autoplay != "undefined" && typeof autoplay.optionAutoplay != "undefined" && autoplay.optionAutoplay == true && __data[k.pe].adsMp3.type == "mp3") {
                if (typeof autoplay.url != "undefined" && autoplay.url != "") {
                    goURLAfterAudioAds = true;
                    if (!d) {
                        $("#mp3" + k.pe).trigger("pauseMp3");
                        window.location = autoplay.url
                    }
                }
            }
            if (typeof (informMp3PlayComplete) == "function") {
                informMp3PlayComplete()
            }
        });
        __data[this.pe].curMp3Item.timePlayedFunction = function () {
            if (__data[k.pe].curMp3Item.timePlayedCheck && __data[k.pe].curMp3Item.timePlayed != -1) {
                __data[k.pe].curMp3Item.timePlayed++;
                var b = __data[k.pe].curMp3Item.timePlayed;
                if (b > 1) {
                    if (!putils.isMobileDevice()) {
                        if (__data[k.pe].adsMp3.callNQC && typeof (runNQCAdv) != "undefined") {
                            runNQCAdv();
                            __data[k.pe].adsMp3.callNQC = false
                        }
                    }
                }
                for (i = 0; i < __data[k.pe].curMp3Item.tempPushGASecond.length; i++) {
                    var c = __data[k.pe].curMp3Item.tempPushGASecond[i];
                    if (Math.round(b) == c) {
                        try {
                            _gaq.push(['_trackEvent', 'PushGASecondHTML5', "-" + c + "s", "SongKey: " + __data[k.pe].curMp3Item.key])
                        } catch (e) {
                            console.log("tracker false: " + e)
                        }
                        __data[k.pe].curMp3Item.tempPushGASecond.splice(i, 1);
                        break
                    }
                }
                try {
                    if (document.getElementById("mp3" + k.pe).currentTime >= Math.round(k.getTotalTime() * 0.75)) {
                        try {
                            if (__data[k.pe].adsMp3.callSpecialNQC) {
                                NqcCore.Core.runSpecialNQC(__data[k.pe].curMp3Item.key);
                                __data[k.pe].adsMp3.callSpecialNQC = false
                            }
                        } catch (e) {
                            console.log("error runSpecialNQC:" + e);
                            __data[k.pe].adsMp3.callSpecialNQC = false
                        }
                    }
                } catch (e) {
                }
                for (j = 0; j < __data[k.pe].curMp3Item.temppushGAPercent.length; j++) {
                    if (b == Math.round(k.getTotalTime() / 100 * __data[k.pe].curMp3Item.temppushGAPercent[j]) || (__data[k.pe].curMp3Item.temppushGAPercent[j] == 100 && b > Math.round(Number((k.getTotalTime() / 100) * 98)) && b > 20)) {
                        try {
                            _gaq.push(['_trackEvent', 'PushGAPercentHTML5', "-" + __data[k.pe].curMp3Item.temppushGAPercent[j] + "%", "SongKey: " + __data[k.pe].curMp3Item.key])
                        } catch (e) {
                            console.log("tracker false percent: " + e)
                        }
                        __data[k.pe].curMp3Item.temppushGAPercent.splice(i, 1);
                        break
                    }
                }
                if (__data[k.pe].curMp3Item.blCheck80) {
                    if (__data[k.pe].curMp3Item.timePlayed > k.getTotalTime() * 75 / 100 && __data[k.pe].curMp3Item.timePlayed > 30) {
                        try {
                            __data[k.pe].curMp3Item.blCheck80 = false;
                            if (typeof (onListenSong) == "function") {
                                onListenSong()
                            }
                        } catch (e) {
                            if (OPEN_SENTRY)
                                Raven.captureException(e);
                            console.log("not function listen on")
                        }
                    }
                }
                if (__data[k.pe].curMp3Item.blCheck60s) {
                    if (__data[k.pe].curMp3Item.timePlayed > 60) {
                        try {
                            __data[k.pe].curMp3Item.blCheck60s = false;
                            if (typeof (onListenSong) == "function" && typeof (dataSong) != "undefined") {
                                var d = "false";
                                if (typeof is_auto_play != "undefined" && is_auto_play == true) {
                                    d = "true"
                                }
                                var f = {
                                    key: dataSong.key,
                                    type: "song60s",
                                    auto_play: d,
                                    v: new Date().getTime()
                                };
                                $.post(NCTInfo.ROOT_URL + "ajax/incsong80", f, function (a) {
                                })
                            }
                        } catch (e) {
                            if (OPEN_SENTRY)
                                Raven.captureException(e);
                            console.log("not function listen on")
                        }
                    }
                }
                try {
                    if (__data[k.pe].curMp3Item.timePlayed == Math.round(Number((k.getTotalTime() / 100) * 1))) {
                        document.getElementById("scribelogBox").src = ('https:' == document.location.protocol ? 'https://' : 'http://') + "log4x.nixcdn.com/w.gif?action=playing&type=song&key=" + __data[k.pe].curMp3Item.key + "&relkey=&user=" + NCTInfo.userName + "&extra=start&time=" + (new Date()).getTime()
                    }
                } catch (e) {
                    if (OPEN_SENTRY)
                        Raven.captureException(e)
                }
                try {
                    if (__data[k.pe].curMp3Item.timePlayed == Math.round(Number((k.getTotalTime() / 100) * 25))) {
                        document.getElementById("scribelogBox").src = ('https:' == document.location.protocol ? 'https://' : 'http://') + "log4x.nixcdn.com/w.gif?action=playing&type=song&key=" + __data[k.pe].curMp3Item.key + "&relkey=&user=" + NCTInfo.userName + "&extra=25&time=" + (new Date()).getTime()
                    }
                } catch (e) {
                    if (OPEN_SENTRY)
                        Raven.captureException(e);
                    console.error(e)
                }
                try {
                    if (__data[k.pe].curMp3Item.timePlayed == Math.round(Number((k.getTotalTime() / 100) * 50))) {
                        document.getElementById("scribelogBox").src = ('https:' == document.location.protocol ? 'https://' : 'http://') + "log4x.nixcdn.com/w.gif?action=playing&type=song&key=" + __data[k.pe].curMp3Item.key + "&relkey=&user=" + NCTInfo.userName + "&extra=50&time=" + (new Date()).getTime()
                    }
                } catch (e) {
                    if (OPEN_SENTRY)
                        Raven.captureException(e);
                    console.error(e)
                }
                try {
                    if (__data[k.pe].curMp3Item.timePlayed == Math.round(Number((k.getTotalTime() / 100) * 75))) {
                        document.getElementById("scribelogBox").src = ('https:' == document.location.protocol ? 'https://' : 'http://') + "log4x.nixcdn.com/w.gif?action=playing&type=song&key=" + __data[k.pe].curMp3Item.key + "&relkey=&user=" + NCTInfo.userName + "&extra=75&time=" + (new Date()).getTime()
                    }
                } catch (e) {
                    if (OPEN_SENTRY)
                        Raven.captureException(e);
                    console.error(e)
                }
                try {
                    if (__data[k.pe].curMp3Item.timePlayed == Math.round(Number((k.getTotalTime() / 100) * 95))) {
                        document.getElementById("scribelogBox").src = ('https:' == document.location.protocol ? 'https://' : 'http://') + "log4x.nixcdn.com/w.gif?action=playing&type=song&key=" + __data[k.pe].curMp3Item.key + "&relkey=&user=" + NCTInfo.userName + "&extra=end&time=" + (new Date()).getTime()
                    }
                } catch (e) {
                    if (OPEN_SENTRY)
                        Raven.captureException(e);
                    console.error(e)
                }
                if (__data[k.pe].curMp3Item.timePlayed >= k.getTotalTime() - 1) {
                    __data[k.pe].curMp3Item.timePlayed = -1;
                    __data[k.pe].curMp3Item.timePlayedCheck = false
                }
            }
            setTimeout(__data[k.pe].curMp3Item.timePlayedFunction, 1000)
        }
        ;
        __data[this.pe].curMp3Item.timePlayedFunction()
    }
    ;
    this.play = function () {
        try {
            document.getElementById("mp3" + this.pe).play()
        } catch (e) {
        }
    }
    ;
    this.pause = function () {
        document.getElementById("mp3" + this.pe).pause()
    }
    ;
    this.loadStream = function () {
        if (document.getElementById("mp3" + this.pe).load()) {
        }
    }
    ;
    this.renewStreamIndex = function (a) {
        if (a > this.listMp3.length - 1) {
            a = 0;
            this.curPlayIndex = a
        }
        if (a < 0) {
            a = this.listMp3.length - 1;
            this.curPlayIndex = a
        }
        this.item = this.listMp3[a];
        if (typeof this.item != "undefined" && this.item != null) {
            this.renSource(this.item);
            this.loadStream()
        }
    }
    ;
    this.seek = function (a) {
        try {
            var b = document.getElementById("mp3" + this.pe);
            if (!isNaN(a) && !isNaN(b.duration)) {
                var c = (b.duration * a / 100);
                b.currentTime = c;
                if (!__data[this.pe].curMp3Item.played) {
                    this.pause()
                }
            }
        } catch (e) {
            console.log(e)
        }
    }
    ;
    this.seekSecond = function (a) {
        try {
            var b = document.getElementById("mp3" + this.pe);
            if (!isNaN(a) && !isNaN(b.duration)) {
                b.currentTime = a;
                if (!__data[this.pe].curVideoItem.played) {
                    this.pause()
                }
            }
        } catch (e) {
        }
    }
    ;
    this.getCurrentTime = function () {
        return parseFloat(document.getElementById("mp3" + this.pe).currentTime).toFixed(3)
    }
    ;
    this.getTotalTime = function () {
        var a = document.getElementById("mp3" + this.pe).duration;
        if (!isNaN(a)) {
            __data[this.pe].curMp3Item.duration = a
        }
        return __data[this.pe].curMp3Item.duration
    }
    ;
    this.getBufferTime = function () {
        try {
            var a = document.getElementById("mp3" + this.pe);
            return a.buffered && a.buffered.length ? a.buffered.end(0) : a.duration
        } catch (e) {
            return 0
        }
    }
    ;
    this.checkReloadTime = 0;
    this.processBuffering = function () {
        try {
            var a = document.getElementById("mp3" + this.pe).currentTime;
            if (__data[this.pe].curMp3Item.played) {
                if (a <= __data[this.pe].curMp3Item.currentTime && (isNaN(document.getElementById("mp3" + this.pe).duration) || __data[this.pe].curMp3Item.currentTime <= document.getElementById("mp3" + this.pe).duration - 3 && a > 1)) {
                    __data[this.pe].curMp3Item.tempBuffer++;
                    $("#mp3" + this.pe).trigger("bufferingMp3");
                    __data[this.pe].curMp3Item.timePlayedCheck = false;
                    if (__data[this.pe].curMp3Item.tempBuffer > 20) {
                        this.checkReloadTime++;
                        if (this.checkReloadTime <= 3) {
                            if (a > 0) {
                                __data[this.pe].curMp3Item.reloadTime = a
                            }
                            this.renSource(__data[this.pe].curMp3Item);
                            this.loadStream()
                        } else {
                            $("#playerMp3" + this.pe).append(__renderMp3.renderErrorNotification(this.pe, __language.errorNetwork))
                        }
                    }
                } else {
                    $("#mp3" + this.pe).trigger("bufferedMp3");
                    __data[this.pe].curMp3Item.tempBuffer = 0;
                    this.checkReloadTime = 0;
                    $("#errorNotification" + this.pe).remove()
                }
            }
            __data[this.pe].curMp3Item.currentTime = a
        } catch (e) {
            console.log(e)
        }
    }
    ;
    this.mute = function () {
        document.getElementById("mp3" + this.pe).volume = 0
    }
    ;
    this.unMute = function () {
        document.getElementById("mp3" + this.pe).volume = __data[this.pe].volume
    }
    ;
    this.setVolume = function (a) {
        if (a > 1 || a < 0) {
            a = 1
        }
        if (!isNaN(a)) {
            __data[this.pe].volume = a;
            document.getElementById("mp3" + this.pe).volume = a
        }
    }
    ;
    this.error = function (e) {
        var a = this;
        var b = "";
        switch (e.target.error.code) {
            case e.target.error.MEDIA_ERR_ABORTED:
                b = 'MEDIA_ERR_ABORTED';
                break;
            case e.target.error.MEDIA_ERR_NETWORK:
                __data[this.pe].curMp3Item.reloadTime = __data[this.pe].curMp3Item.currentTime;
                this.renSource(__data[this.pe].curMp3Item);
                this.loadStream();
                $("#mp3" + this.pe).trigger("playMp3");
                b = 'MEDIA_ERR_NETWORK';
                break;
            case e.target.error.MEDIA_ERR_DECODE:
                b = 'MEDIA_ERR_DECODE';
                $("#mp3" + this.pe).trigger("ended");
                b = "";
                break;
            case e.target.error.MEDIA_ERR_SRC_NOT_SUPPORTED:
                b = 'MEDIA_ERR_SRC_NOT_SUPPORTED';
                $("#SwitchQualityDefault" + this.pe).click();
                break;
            default:
                b = 'OTHER';
                break
        }
        if (b != "") {
            if (a.location == a.item.location) {
                document.getElementById("mp3" + a.pe).src = a.item.highquality;
                document.getElementById("mp3" + a.pe).play()
            } else if (a.location == a.item.highquality) {
                document.getElementById("mp3" + a.pe).src = a.item.location;
                document.getElementById("mp3" + a.pe).play()
            }
            if (OPEN_SENTRY)
                Raven.captureException(e)
        }
        var c = NCTInfo.ROOT_URL + "api/flashlog.ashx";
        var d = {
            flashversion: "html5 mp3",
            error: b,
            url: window.location.toString(),
            type: "mp3",
            stream: a.location
        };
        console.log(b)
    }
    ;
    this.updatetimeLyric = function () {
        this.lyric.updateTime(this.getCurrentTime())
    }
    ;
    this.getArrayPlaylist = function (c) {
        var d = c;
        if (__data[d].arrayPlaylistRandomed.length > 0) {
            __data[d].arrayPlaylistRandomed.forEach(function (a) {
                __data[d].arrayPlaylist.push(a)
            })
        } else {
            __data[d].arrayPlaylist = [];
            for (var i = 0; i <= __data[d].mp3.length - 1; i++) {
                if (__data[d].curMp3Item.curPlayIndex != i) {
                    __data[d].arrayPlaylist.push(i)
                }
            }
            __data[d].arrayPlaylist.sort(function (a, b) {
                return 0.5 - Math.random()
            });
            __data[d].arrayPlaylistRandomed = [];
            __data[d].arrayPlaylistRandomed.push(__data[d].curMp3Item.curPlayIndex);
            __data[d].arrayPlaylist.forEach(function (a) {
                __data[d].arrayPlaylistRandomed.push(a)
            })
        }
    }
};
var __data = [];
var __language = {
    errorParseXml: "Không thể parse được file xml",
    errorLoadXml: "Không thể load được file xml",
    errorNetwork: "Có lỗi xảy ra với Internet. Vui lòng kiểm tra lại kết nối của bạn hoặc refresh lại trang.",
    fullScreen: "Toàn màn hình",
    listRecommend: "Playlist",
    update_browser: "Trình duyệt của bạn quá cũ không hỗ trợ định dạng Video này. Vui lòng nâng cấp trình duyệt.",
    loading: "Đang tải...",
    off: "Tắt",
    configReplay: "",
    repeatAll: "Lặp tất cả",
    noRepeat: "Không lặp",
    repeat: "Lặp",
    repeatOne: "Lặp một bài"
};
var __parseKaraoke = function () {
    this.pe = "";
    this.load = function (b) {
        __debug.log("ParseSRT.load", b);
        this.pe = b;
        if (__data[b].peConfig.lyricStatus) {
            __data[b].peConfig.lyricStatus = false;
            $.ajaxSetup({
                "beforeSend": function (a) {
                    a.overrideMimeType("text/text; charset=UTF-8")
                }
            });
            var c = __data[b].curMp3Item.lyric;
            if (c != '' && c.toString().indexOf("null") == -1) {
                this.getLyric(c);
                __data[b].peConfig.lyricTempStatus = true
            } else {
                __data[b].peConfig.lyricTempStatus = true
            }
            __data[b].peConfig.lyricStatus = true
        }
    }
    ;
    this.getLyric = function (g) {
        var h = this;
        var i = this.pe;
        __data[i].curMp3Item.listLyric = [];
        $.ajax({
            type: "GET",
            url: g,
            data: {},
            success: function (e, f) {
                var a = putils.hexToArray(e);
                var b = putils.hexToArray(putils.hexFromString("Lyr1cjust4"));
                var c = new arc4();
                c.load(b);
                var d = c.decrypt(a);
                e = putils.hexFromArray(d);
                if (putils.getQueryVariable(window.location.href.toString(), "showlyric") == "true") {
                    console.log(e)
                }
                __data[i].curMp3Item.activeLineIndex = 0;
                __data[i].curMp3Item.showNextLine = true;
                __data[i].curMp3Item.listLyric = h.parseLrc(e)
            },
            dataType: 'text',
            async: false,
            cache: false,
            statusCode: {
                404: function () {
                    __data[i].curMp3Item.listLyric = null
                }
            }
        }).fail(function (e) {
        })
    }
    ;
    this.parseLrc = function (c) {
        try {
            if (typeof c != "undefined" && c != "" && c != null) {
                var d = c.replace(/\r+/g, '');
                d = d.replace(/\n+/g, '\n');
                d = d.replace(/^\s+|\s+$/g, '');
                d = d.replace(/<[a-zA-Z\/][^>]*>/g, '');
                var f = [];
                var g = '';
                var j = [];
                var m = [];
                var n = d.split('\n');
                for (p = 0; p < n.length; p++) {
                    var o = 0;
                    arrTempLineLyric = [];
                    do {
                        arrTempLineLyric.push(n[p].substr(o + 1, 8));
                        o = n[p].indexOf("[", o + 8)
                    } while (o != -1)
                    var q = arrTempLineLyric.length;
                    for (s = 0; s < q; s++) {
                        var r = {};
                        r.id = s;
                        r.content = g;
                        r.duration = 0;
                        var t = (arrTempLineLyric[arrTempLineLyric.length - 1 - s]).split(":");
                        t = parseFloat(t[0]) * 60 + parseFloat(t[1]);
                        r.start = t;
                        j.push(r.start);
                        if (r.start >= 4) {
                            f.push(p)
                        }
                    }
                }
                for (i = 0; i < n.length; i++) {
                    var o = 0;
                    var u = [];
                    if (isNaN(j[0])) {
                        do {
                            if (i < f[1]) {
                                u.push("00:0" + parseInt(i + 1) + ":00")
                            } else {
                                u.push(n[i].substr(o + 1, 8))
                            }
                            o = n[i].indexOf("[", o + 8)
                        } while (o != -1);
                        if (n[i].lastIndexOf("]") == n[i].length - 1) {
                            g = " "
                        } else {
                            if (i == 0) {
                                g = n[0].substring(4, parseInt(n[0].lastIndexOf("]")))
                            }
                            if (i == 1) {
                                g = n[1].substring(4, parseInt(n[1].lastIndexOf("]")))
                            }
                            if (i == 2) {
                                g = n[2].substring(4, parseInt(n[2].lastIndexOf("]")))
                            }
                            if (i == 3) {
                                g = ""
                            }
                            if (i >= 4) {
                                g = n[i].substring(n[i].lastIndexOf("]") + 1)
                            }
                        }
                        var v = u.length;
                        for (k = 0; k < v; k++) {
                            var w = {};
                            w.id = k;
                            w.content = g;
                            w.duration = 0;
                            var t = (u[u.length - 1 - k]).split(":");
                            t = parseFloat(t[0]) * 60 + parseFloat(t[1]);
                            w.start = t - 0.1;
                            m.push(w)
                        }
                    } else {
                        do {
                            u.push(n[i].substr(o + 1, 8));
                            o = n[i].indexOf("[", o + 8)
                        } while (o != -1);
                        if (n[i].lastIndexOf("]") == n[i].length - 1) {
                            g = " "
                        } else {
                            g = n[i].substring(n[i].lastIndexOf("]") + 1)
                        }
                        var x = u.length;
                        for (h = 0; h < x; h++) {
                            var y = {};
                            y.id = h;
                            y.content = g;
                            y.duration = 0;
                            var t = (u[u.length - 1 - h]).split(":");
                            t = parseFloat(t[0]) * 60 + parseFloat(t[1]);
                            y.start = t - 0.1;
                            m.push(y)
                        }
                    }
                }
                m.sort(function (a, b) {
                    if (a.start > b.start) {
                        return 1
                    } else if (a.start < b.start) {
                        return -1
                    } else {
                        return 0
                    }
                });
                for (l = 0; l < m.length; l++) {
                    if (l < m.length - 1) {
                        m[l].duration = m[l + 1].start - m[l].start
                    }
                    if (l % 2 == 0) {
                        m[l].pos = 1
                    } else {
                        m[l].pos = 2
                    }
                }
            }
            return m
        } catch (e) {
            console.log("Lyric wrong style")
        }
    }
};
var xmlDocAds;
var __parseXMLAds = function () {
    this.pe = "";
    this.load = function (a) {
        this.pe = a
    }
    ;
    this.parse = function (c) {
        var d = this.pe;
        var f = __data[d].adsMp3.link;
        if (f.indexOf("?") != -1) {
            f += "&" + putils.generateAdsParam(__data[d].adsMp3.type)
        } else {
            f += "?" + putils.generateAdsParam(__data[d].adsMp3.type)
        }
        try {
            if (window.XMLHttpRequest) {
                xmlhttp = new XMLHttpRequest()
            } else {
                xmlhttp = new ActiveXObject("Microsoft.XMLHTTP")
            }
            xmlhttp.addEventListener("load", function (a) {
                if (a.target.status == 200 && a.target.readyState == 4) {
                    if (putils.browser.isIE()) {
                        xmlDocAds = putils.parseXml(a.srcElement.responseText)
                    } else {
                        xmlDocAds = a.currentTarget.responseXML;
                        if (xmlDocAds == undefined || xmlDocAds == "" || xmlDocAds == null || xmlDocAds == "null") {
                            xmlDocAds = putils.parseXml(a.currentTarget.responseText)
                        }
                    }
                    try {
                        var b = xmlDocAds.getElementsByTagName("ads")[0].getElementsByTagName("adsitem");
                        for (i = 0; i < b.length; i++) {
                            __data[d].adsMp3.linkClick = xmlDocAds.getElementsByTagName("link")[i].childNodes[0].wholeText;
                            __data[d].adsMp3.openAdsMp3 = xmlDocAds.getElementsByTagName("enable")[i].childNodes[0].wholeText;
                            __data[d].adsMp3.file = xmlDocAds.getElementsByTagName("file")[i].childNodes[0].wholeText;
                            __data[d].adsMp3.fallback = xmlDocAds.getElementsByTagName("fallback")[i].childNodes[0].wholeText;
                            __data[d].adsMp3.iframe = xmlDocAds.getElementsByTagName("iframe")[i].childNodes[0].wholeText
                        }
                    } catch (e) {
                        __data[d].adsMp3.linkClick = "";
                        __data[d].adsMp3.openAdsMp3 = "";
                        __data[d].adsMp3.iframe = "";
                        __data[d].adsMp3.file = ""
                    }
                    c.xmlAdsParseComplete()
                }
            }, false);
            xmlhttp.open("GET", f, true);
            xmlhttp.send()
        } catch (e) {
        }
    }
};
var xmlDoc;
var __parseXMLMp3 = function () {
    this.pe = "";
    this.load = function (a) {
        this.pe = a
    }
    ;
    this.parse = function (d) {
        var f = this.pe;
        var g = __data[this.pe].peConfig.xmlURL;
        if (window.XMLHttpRequest) {
            xmlhttp = new XMLHttpRequest()
        } else {
            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP")
        }
        xmlhttp.addEventListener("load", function (a) {
            if (a.target.status == 200 && a.target.readyState == 4) {
                try {
                    if (putils.browser.isIE()) {
                        if (typeof a.srcElement != "undefined" && a.srcElement != null && typeof a.srcElement.responseText != "undefined") {
                            xmlDoc = putils.parseXml(a.srcElement.responseText)
                        } else {
                            xmlDoc = putils.parseXml(a.currentTarget.responseText)
                        }
                    } else {
                        xmlDoc = a.currentTarget.responseXML;
                        if (xmlDoc == undefined || xmlDoc == "" || xmlDoc == null || xmlDoc == "null") {
                            xmlDoc = putils.parseXml(a.currentTarget.responseText)
                        }
                    }
                    var b = [];
                    var c = xmlDoc.getElementsByTagName("tracklist")[0].getElementsByTagName("track");
                    for (i = 0; i < c.length; i++) {
                        b[i] = {};
                        b[i].title = xmlDoc.getElementsByTagName("title")[i].childNodes[0].wholeText;
                        b[i].key = xmlDoc.getElementsByTagName("key")[i].childNodes[0].wholeText;
                        b[i].info = xmlDoc.getElementsByTagName("info")[i].childNodes[0].wholeText;
                        b[i].location = xmlDoc.getElementsByTagName("location")[i].childNodes[0].wholeText;
                        b[i].highquality = $.trim(xmlDoc.getElementsByTagName("locationHQ")[i].childNodes[0].wholeText);
                        b[i].lyric = xmlDoc.getElementsByTagName("lyric")[i].childNodes[0].wholeText;
                        b[i].time = xmlDoc.getElementsByTagName("time")[i].childNodes[0].wholeText;
                        b[i].avatar = xmlDoc.getElementsByTagName("avatar")[i].childNodes[0].wholeText;
                        b[i].bgimage = xmlDoc.getElementsByTagName("bgimage")[i].childNodes[0].wholeText;
                        b[i].creator = xmlDoc.getElementsByTagName("creator")[i].childNodes[0].wholeText;
                        b[i].newtab = xmlDoc.getElementsByTagName("newtab")[i].childNodes[0].wholeText;
                        b[i].kbit = xmlDoc.getElementsByTagName("kbit")[i].childNodes[0].wholeText;
                        b[i].hasHQ = $.trim(xmlDoc.getElementsByTagName("hasHQ")[i].childNodes[0].wholeText);
                        try {
                            b[i].coverimage = $.trim(xmlDoc.getElementsByTagName("coverimage")[i].childNodes[0].wholeText)
                        } catch (ex) {
                            b[i].coverimage = ""
                        }
                    }
                    __data[f].mp3 = b;
                    d.xmlParseComplete()
                } catch (e) {
                    if (!putils.isMobileDevice()) {
                        if (__data[f].adsMp3.callNQC && typeof (runNQCAdv) != "undefined") {
                            runNQCAdv();
                            __data[f].adsMp3.callNQC = false
                        }
                        if (__data[f].adsMp3.outOne && typeof (loadAdsMp3Loaded) == "function") {
                            loadAdsMp3Loaded()
                        } else {
                            __data[f].adsMp3.outOne = true
                        }
                        $(document).ready(function () {
                            $("#adv_lyrics").remove()
                        })
                    }
                }
            } else {
                $("#playerMp3" + f).append(__renderMp3.renderErrorNotification(f, __language.errorLoadXml))
            }
        }, false);
        xmlhttp.open("GET", g, false);
        xmlhttp.send()
    }
};
var __controlbarMp3 = function () {
    this.pe = "";
    this.streamingMp3 = null;
    this.parseLyric = new __parseKaraoke();
    this.lyric = new __karaoke();
    this.load = function (a) {
        __debug.log("Controlbar.load", a);
        this.pe = a;
        __data[this.pe].startScrollTime = false;
        __data[this.pe].arrayPlaylist = [];
        this.mainFunction();
        this.setEventPlayButton();
        if (__data[this.pe].peConfig.logoActive) {
            this.setEventLogoButton()
        } else {
            $("#logo" + this.pe).addClass("notActive")
        }
        this.setEventTimeSlider();
        this.setEventVolumeButton();
        this.setEventVolumeSlider();
        if (typeof isPlayingPlaylist != "undefined" && isPlayingPlaylist == true) {
            $("#repeatButton" + this.pe).removeClass("hide");
            this.setEventRepatControl()
        }
        this.setEventRandomControl();
        if (__data[a].mp3.length > 1) {
            this.setEventPrevNextButton()
        } else {
            this.setEventNextButtonAutoplay()
        }
        if (__data[this.pe].peConfig.lyricStatus) {
            $("#lyricBox" + this.pe).removeClass("hide");
            this.lyric.streamingMp3 = this.streamingMp3;
            this.lyric.load(this.pe);
            this.lyric.parseLyric = this.parseLyric
        }
        var b = new __switchQuality();
        b.streamingMp3 = this.streamingMp3;
        b.load(a)
    }
    ;
    this.mainFunction = function () {
        try {
            var a = this;
            $("#mp3" + this.pe).bind("playMp3", function () {
                a.showPauseIcon()
            }).bind("pauseMp3", function () {
                a.hidePauseIcon()
            }).bind("timeupdate", function () {
                a.updateTimeCounter();
                a.updateTimeSliderCurrent()
            }).bind("totalTimeUpdate", function () {
                a.updateTotalTimeCounter()
            }).bind("progress", function () {
                a.updateTimeSliderBuffer()
            }).bind("durationchange", function () {
                a.updateTimeSliderBuffer()
            });
            __data[a.pe].timelyricInterval = function () {
                try {
                    a.updatetimeLyric()
                } catch (e) {
                }
                setTimeout(function () {
                    try {
                        __data[a.pe].timelyricInterval()
                    } catch (e) {
                        setTimeout(function () {
                            __data[a.pe].timelyricInterval()
                        }, 1000)
                    }
                }, 60)
            }
            ;
            __data[a.pe].timelyricInterval()
        } catch (e) {
            console.warn(e)
        }
    }
    ;
    this.setEventTimeSlider = function () {
        var l = this;
        $("#timeSlider" + this.pe).click(function (e) {
            e.preventDefault();
            var b = 0;
            if (typeof e.pageX != "undefined") {
                b = e.pageX
            } else if (typeof e.originalEvent.x != "undefined") {
                b = e.originalEvent.x
            } else {
                b = e.changedTouches[0].pageX
            }
            var c = parseFloat((b - $("#timeSlider" + l.pe).offset().left) / $(this).width() * 100);
            if (c >= 0 && c <= 100) {
                l.lyric.updateActiveIndex(c);
                l.streamingMp3.seek(c);
                try {
                    var d = {
                        action: "getInfoTracking",
                        t: "song",
                        key: __data[l.pe].curMp3Item.key,
                        mineKey: NCTInfo.mineKey
                    };
                    var f = "repeat_one";
                    if (__data[l.pe].peConfig.repeatStatus == "no") {
                        f = "not_repeat"
                    }
                    var g = __data[l.pe].curQuality;
                    var h = document.getElementById("mp3" + l.pe).duration;
                    var i = typeof (idDownloadTracking) != "undefined" && window.location.href.indexOf("/playlist/") != -1 ? idDownloadTracking : "null";
                    $.post(NCTInfo.ROOT_URL + "ajax/playlist", d, function (a) {
                        trackingSmarty.mp3_player_time_slider_seek(a.data.id_tracking, i, c, "null", f, h, g)
                    }, "json")
                } catch (e) {
                }
            }
            var j = putils.getCookie("volume");
            var k = putils.getCookie("volumeMute");
            if (typeof k != 'undefined' && k == "1") {
                $("#volume" + l.pe).parent().addClass("mute");
                $("#volumeCurrent" + l.pe).addClass("hide")
            } else if (typeof j != 'undefined' && j != "") {
                l.streamingMp3.setVolume(j / 100);
                $("#volume" + l.pe).parent().removeClass("mute");
                $("#volumeCurrent" + l.pe).removeClass("hide")
            } else {
                $("#volume" + l.pe).parent().removeClass("mute");
                $("#volumeCurrent" + l.pe).removeClass("hide");
                l.streamingMp3.setVolume(1)
            }
        });
        if ((putils.support.touch || putils.isMobileDevice()) && !putils.browser.isIE()) {
            $("#timeSlider" + this.pe).addClass("touch");
            var m = document.getElementById('timeSliderHolder' + this.pe);
            m.addEventListener(putils.touchStart(), function (e) {
                e.preventDefault();
                __data[l.pe].startScrollTime = true
            }, false);
            document.addEventListener(putils.touchMove(), function (e) {
                if (__data[l.pe].startScrollTime == true) {
                    e.preventDefault();
                    if (typeof e.changedTouches[0].pageX != "undefined") {
                        l.timeSliderScrollEvent(e.changedTouches[0].pageX)
                    } else {
                        l.timeSliderScrollEvent(e.pageX)
                    }
                }
            }, false);
            document.addEventListener(putils.touchEnd(), function (e) {
                if (__data[l.pe].startScrollTime == true) {
                    e.preventDefault();
                    __data[l.pe].startScrollTime = false;
                    var a = 0;
                    if (typeof e.changedTouches[0].pageX != "undefined") {
                        a = e.changedTouches[0].pageX
                    } else {
                        a = e.pageX
                    }
                    var b = $("#timeSlider" + l.pe);
                    var c = b.width();
                    var d = parseFloat((a - b.offset().left) / c * 100);
                    if (d >= 0 && d <= 100) {
                        l.lyric.updateActiveIndex(d);
                        l.streamingMp3.seek(d)
                    }
                }
            }, false)
        }
        if (putils.browser.isIE()) {
            if (navigator.userAgent.toLowerCase().indexOf("touch") != -1) {
                $("#timeSlider" + this.pe).addClass("touch")
            }
            $("#timeSliderHolder" + this.pe).bind(putils.touchStart(), function (e) {
                __data[l.pe].startScrollTime = true
            });
            $(document).bind(putils.touchMove(), function (e) {
                if (__data[l.pe].startScrollTime) {
                    var a = $("#timeSlider" + l.pe);
                    var b = parseFloat((e.originalEvent.x - 3) / a.width() * 100);
                    if (b >= 0 && b <= 100) {
                        $("#timeSliderHolder" + l.pe).css("left", b + "%");
                        $("#timeSliderCurrent" + l.pe).width(b + "%")
                    }
                }
            }).bind(putils.touchEnd(), function (e) {
                if (__data[l.pe].startScrollTime) {
                    __data[l.pe].startScrollTime = false
                }
            })
        } else {
            $("#timeSliderHolder" + this.pe).mousedown(function () {
                __data[l.pe].startScrollTime = true
            });
            $(document).mousemove(function (e) {
                if (__data[l.pe].startScrollTime) {
                    l.timeSliderScrollEvent(e.pageX)
                }
            }).mouseup(function (e) {
                if (__data[l.pe].startScrollTime) {
                    __data[l.pe].startScrollTime = false;
                    var a = $("#timeSlider" + l.pe);
                    var b = a.width();
                    var c = parseFloat((e.pageX - a.offset().left) / b * 100);
                    if (c < 0) {
                        c = 0
                    }
                    if (c > 100) {
                        c = 100
                    }
                    l.lyric.updateActiveIndex(c);
                    l.streamingMp3.seek(c);
                    var d = putils.getCookie("volume");
                    if (d != "") {
                        l.streamingMp3.setVolume(d / 100)
                    }
                }
            })
        }
    }
    ;
    this.timeSliderScrollEvent = function (x) {
        var a = $("#timeSlider" + this.pe);
        var b = parseFloat((x - a.offset().left - 3) / a.width() * 100);
        if (b >= 0 && b <= 100) {
            $("#timeSliderHolder" + this.pe).css("left", b + "%");
            $("#timeSliderCurrent" + this.pe).width(b + "%")
        } else if (b < 0) {
            $("#timeSliderHolder" + this.pe).css("left", "1%");
            $("#timeSliderCurrent" + this.pe).width("1%")
        } else if (b > 100) {
            $("#timeSliderHolder" + this.pe).css("left", "99%");
            $("#timeSliderCurrent" + this.pe).width("99%")
        }
    }
    ;
    this.updateTimeSliderBuffer = function () {
        var a = this.streamingMp3.getBufferTime() / this.streamingMp3.getTotalTime() * 100;
        $("#timeSliderBuffer" + this.pe).width(a + "%")
    }
    ;
    this.updateDownVolume = function () {
    }
    ;
    this.updateTimeSliderCurrent = function () {
        if (!__data[this.pe].startScrollTime) {
            var a = parseFloat(this.streamingMp3.getCurrentTime() / this.streamingMp3.getTotalTime() * 100).toFixed(1);
            $("#timeSliderHolder" + this.pe).css("left", a + "%");
            $("#timeSliderCurrent" + this.pe).width(a + "%")
        }
    }
    ;
    this.setEventPlayButton = function () {
        var i = this;
        $("#playButton" + this.pe).click(function () {
            if (document.getElementById("mp3" + i.pe).paused) {
                $("#mp3" + i.pe).trigger("playMp3")
            } else {
                $("#mp3" + i.pe).trigger("pauseMp3")
            }
            try {
                var b = {
                    action: "getInfoTracking",
                    t: "song",
                    key: __data[i.pe].curMp3Item.key,
                    mineKey: NCTInfo.mineKey
                };
                var c = "repeat_one";
                if (__data[i.pe].peConfig.repeatStatus == "no") {
                    c = "not_repeat"
                }
                var d = __data[i.pe].curQuality;
                var f = document.getElementById("mp3" + i.pe).duration;
                var g = document.getElementById("mp3" + i.pe).paused;
                var h = typeof (idDownloadTracking) != "undefined" && window.location.href.indexOf("/playlist/") != -1 ? idDownloadTracking : "null";
                $.post(NCTInfo.ROOT_URL + "ajax/playlist", b, function (a) {
                    if (g) {
                        trackingSmarty.mp3_player_stop(a.data.id_tracking, h, c, "null", "null", f, d)
                    } else {
                        trackingSmarty.mp3_player_play(a.data.id_tracking, h, c, "null", "null", f, d)
                    }
                }, "json")
            } catch (e) {
            }
        })
    }
    ;
    this.showPauseIcon = function () {
        $("#playButton" + this.pe).addClass("pause")
    }
    ;
    this.hidePauseIcon = function () {
        $("#playButton" + this.pe).removeClass("pause")
    }
    ;
    this.setEventPrevNextButton = function () {
        var n = this;
        var o = 0;
        $("#prevButton" + this.pe).click(function () {
            var b = 0;
            try {
                var c = {
                    action: "getInfoTracking",
                    t: "song",
                    key: __data[n.pe].curMp3Item.key,
                    mineKey: NCTInfo.mineKey
                };
                $.post(NCTInfo.ROOT_URL + "ajax/playlist", c, function (a) {
                    b = a.data.id_tracking
                }, "json")
            } catch (e) {
            }
            var d = 0;
            if (__data[n.pe].peConfig.randomListPlayer) {
                if (__data[n.pe].arrayPlaylist.length <= 0) {
                    n.getArrayPlaylist()
                }
                if (__data[n.pe].arrayPlaylistRandomed.length - 1 == __data[n.pe].arrayPlaylist.length) {
                    var f = __data[n.pe].arrayPlaylist.length;
                    for (k = 0; k < f - 1; k++) {
                        __data[n.pe].arrayPlaylist.splice(0, 1)
                    }
                    d = __data[n.pe].arrayPlaylist[0];
                    __data[n.pe].arrayPlaylist.splice(0, 1)
                } else {
                    d = __data[n.pe].curMp3Item.curPlayIndex;
                    var g = true;
                    __data[n.pe].arrayPlaylist = [];
                    __data[n.pe].arrayPlaylistRandomed.forEach(function (a) {
                        __data[n.pe].arrayPlaylist.push(a);
                        if (a == __data[n.pe].curMp3Item.curPlayIndex) {
                            g = false
                        }
                        if (g) {
                            d = a
                        }
                    });
                    g = true;
                    __data[n.pe].arrayPlaylistRandomed.forEach(function (a) {
                        if (g) {
                            __data[n.pe].arrayPlaylist.splice(0, 1)
                        }
                        if (a == d) {
                            g = false
                        }
                    })
                }
            } else {
                d = parseInt(__data[n.pe].curMp3Item.curPlayIndex) - 1
            }
            __data[n.pe].curMp3Item.curPlayIndex = d;
            n.streamingMp3.curPlayIndex = d;
            n.streamingMp3.renewStreamIndex(d);
            try {
                var h = {
                    action: "getInfoTracking",
                    t: "song",
                    key: __data[n.pe].curMp3Item.key,
                    mineKey: NCTInfo.mineKey
                };
                var i = "repeat_one";
                if (__data[n.pe].peConfig.repeatStatus == "no") {
                    i = "not_repeat"
                }
                var j = __data[n.pe].curQuality;
                var l = document.getElementById("mp3" + n.pe).duration;
                var m = typeof (idDownloadTracking) != "undefined" && window.location.href.indexOf("/playlist/") != -1 ? idDownloadTracking : "null";
                $.post(NCTInfo.ROOT_URL + "ajax/playlist", h, function (a) {
                    trackingSmarty.mp3_player_play_prev(a.data.id_tracking, m, i, "null", "null", l, j, b)
                }, "json")
            } catch (e) {
            }
        });
        $("#nextButton" + this.pe).click(function () {
            var b = 0;
            try {
                var c = {
                    action: "getInfoTracking",
                    t: "song",
                    key: __data[n.pe].curMp3Item.key,
                    mineKey: NCTInfo.mineKey
                };
                $.post(NCTInfo.ROOT_URL + "ajax/playlist", c, function (a) {
                    b = a.data.id_tracking
                }, "json")
            } catch (e) {
            }
            var d = 0;
            if (__data[n.pe].peConfig.randomListPlayer) {
                if (__data[n.pe].arrayPlaylist.length <= 0) {
                    n.getArrayPlaylist()
                }
                o = 0;
                d = __data[n.pe].arrayPlaylist[o];
                __data[n.pe].arrayPlaylist.splice(o, 1)
            } else {
                d = parseInt(__data[n.pe].curMp3Item.curPlayIndex) + 1
            }
            __data[n.pe].curMp3Item.curPlayIndex = d;
            n.streamingMp3.curPlayIndex = d;
            n.streamingMp3.renewStreamIndex(d);
            try {
                var f = {
                    action: "getInfoTracking",
                    t: "song",
                    key: __data[n.pe].curMp3Item.key,
                    mineKey: NCTInfo.mineKey
                };
                var g = "repeat_one";
                if (__data[n.pe].peConfig.repeatStatus == "no") {
                    g = "not_repeat"
                }
                var h = __data[n.pe].curQuality;
                var i = document.getElementById("mp3" + n.pe).duration;
                var j = typeof (idDownloadTracking) != "undefined" && window.location.href.indexOf("/playlist/") != -1 ? idDownloadTracking : "null";
                $.post(NCTInfo.ROOT_URL + "ajax/playlist", f, function (a) {
                    trackingSmarty.mp3_player_play_next(a.data.id_tracking, j, g, "null", "null", i, h, b)
                }, "json")
            } catch (e) {
            }
        })
    }
    ;
    this.setEventRandomControl = function () {
        var a = this;
        var b = putils.getCookie("player_random");
        if (typeof b != "undefined" && b == "1") {
            $("#randomButton" + this.pe).addClass("true");
            __data[a.pe].peConfig.randomListPlayer = 1
        } else {
            __data[a.pe].peConfig.randomListPlayer = 0
        }
        if (__data[a.pe].mp3.length < 3) {
            __data[a.pe].peConfig.randomListPlayer = 0
        }
        $("#randomButton" + a.pe).click(function () {
            if ($(this).hasClass("true")) {
                $("#randomButton" + a.pe).removeClass("true");
                if (__data[a.pe].mp3.length >= 3) {
                    __data[a.pe].peConfig.randomListPlayer = 0;
                    putils.setCookie("player_random", "0", 7)
                }
            } else {
                $("#randomButton" + a.pe).addClass("true");
                if (__data[a.pe].mp3.length >= 3) {
                    __data[a.pe].peConfig.randomListPlayer = 1;
                    putils.setCookie("player_random", "1", 7)
                }
            }
        })
    }
    ;
    this.setEventRepatControl = function () {
        var j = this;
        $("#repeatButton" + this.pe).click(function () {
            var b = 0;
            try {
                var c = {
                    action: "getInfoTracking",
                    t: "song",
                    key: __data[j.pe].curMp3Item.key,
                    mineKey: NCTInfo.mineKey
                };
                $.post(NCTInfo.ROOT_URL + "ajax/playlist", c, function (a) {
                    b = a.data.id_tracking
                }, "json")
            } catch (e) {
            }
            if ($(this).hasClass("one")) {
                $("#repeatButton" + j.pe).removeClass("one");
                $("#repeatTooltip" + j.pe).html(__language.noRepeat);
                __data[j.pe].peConfig.repeatStatus = "no"
            } else {
                $("#repeatButton" + j.pe).addClass("one");
                $("#repeatTooltip" + j.pe).html(__language.repeatOne);
                __data[j.pe].peConfig.repeatStatus = "one"
            }
            try {
                var d = {
                    action: "getInfoTracking",
                    t: "song",
                    key: __data[j.pe].curMp3Item.key,
                    mineKey: NCTInfo.mineKey
                };
                var f = "repeat_one";
                if (__data[j.pe].peConfig.repeatStatus == "no") {
                    f = "not_repeat"
                }
                var g = __data[j.pe].curQuality;
                var h = document.getElementById("mp3" + j.pe).duration;
                var i = typeof (idDownloadTracking) != "undefined" && window.location.href.indexOf("/playlist/") != -1 ? idDownloadTracking : "null";
                $.post(NCTInfo.ROOT_URL + "ajax/playlist", d, function (a) {
                    trackingSmarty.mp3_player_repeat(a.data.id_tracking, i, f, "null", f, h, g, b)
                }, "json")
            } catch (e) {
            }
        })
    }
    ;
    this.updatetimeLyric = function () {
        this.lyric.updateTime(this.streamingMp3.getCurrentTime())
    }
    ;
    this.updateTimeCounter = function () {
        $("#utCurrentTime" + this.pe).html(putils.formatTime(this.streamingMp3.getCurrentTime()))
    }
    ;
    this.updateTotalTimeCounter = function () {
        $("#timeCounter" + this.pe).addClass("complete");
        $("#utTotalTime" + this.pe).html(putils.formatTime(this.streamingMp3.getTotalTime()))
    }
    ;
    this.setEventLogoButton = function () {
        var a = this;
        if (window.self !== window.top) {
            $("#logo" + this.pe + " a").attr("target", __data[this.pe].peConfig.logoClickTarget).attr("href", __data[this.pe].curMp3Item.info).click(function () {
                $("#playButton" + a.pe).click()
            })
        } else {
            $("#logo" + this.pe + " a").attr("target", __data[this.pe].peConfig.logoClickTarget).attr("href", ('https:' == document.location.protocol ? 'https://' : 'http://') + "www.nhaccuatui.com")
        }
        if (window.location.href.indexOf("/playlist/") != -1 || window.location.href.indexOf("/playlist-hero/") != -1 || window.location.href.indexOf("/bai-hat/") != -1 || window.location.href.indexOf("/chu-de/") != -1 || window.location.href.indexOf("/samsungfridayhits") != -1) {
        } else {
            $("#logo" + this.pe).addClass("showLogo");
            $("#switchQuality" + this.pe).addClass("hide")
        }
    }
    ;
    this.setEventVolumeButton = function () {
        var b = this;
        if (putils.isMobileDevice()) {
            $("#volumeControl" + this.pe).addClass("touch")
        } else {
            try {
                __data[this.pe].volume = __data[this.pe].peConfig.volumeDefault
            } catch (e) {
                __data[this.pe].peConfig.volumeDefault = 0.8;
                __data[this.pe].volume = __data[this.pe].peConfig.volumeDefault
            }
            $("#volumeCurrentInside" + this.pe).removeClass("v1").removeClass("v2").addClass("v3");
            $("#mp3" + b.pe).bind("playMp3", function () {
                var a = putils.getCookie("volumeMute");
                if (typeof a != "undefined" && a == "1") {
                    __data[b.pe].mute = true;
                    $("#volume" + b.pe).parent().addClass("mute");
                    $("#volumeCurrent" + b.pe).addClass("hide");
                    b.streamingMp3.mute()
                }
            });
            $("#volume" + this.pe).click(function () {
                if (__data[b.pe].mute) {
                    __data[b.pe].mute = false;
                    $(this).parent().removeClass("mute");
                    $("#volumeCurrent" + b.pe).removeClass("hide");
                    b.streamingMp3.unMute();
                    putils.setCookie("volumeMute", "0", 7)
                } else {
                    __data[b.pe].mute = true;
                    $(this).parent().addClass("mute");
                    $("#volumeCurrent" + b.pe).addClass("hide");
                    b.streamingMp3.mute();
                    putils.setCookie("volumeMute", "1", 7)
                }
            })
        }
    }
    ;
    this.setEventVolumeSlider = function () {
        var a = this;
        $("#volumeSliderHolder" + this.pe).bind("mousedown", function (e) {
            __data[a.pe].startScrollVolume = true;
            $("#volumeSlider" + a.pe).addClass("show")
        });
        $(document).bind("mousemove", function (e) {
            if (__data[a.pe].startScrollVolume) {
                a.volumeScrollEvent(e.pageY)
            }
        }).bind("mouseup", function (e) {
            __data[a.pe].startScrollVolume = false;
            $("#volumeSlider" + a.pe).removeClass("show")
        });
        $("#volumeSliderClick" + this.pe).click(function (e) {
            a.volumeScrollEvent(e.pageY)
        });
        var b = putils.getCookie("volume");
        var c = putils.getCookie("volumeMute");
        if (typeof c != 'undefined' && c == "1") {
        } else if (typeof b != 'undefined' && b != "") {
            this.renderVolumeScroll(b);
            this.streamingMp3.setVolume(b / 100)
        } else {
        }
    }
    ;
    this.volumeScrollEvent = function (y) {
        var a = parseInt((85 + $("#volumeSlider" + this.pe).offset().top - y + 13) / 85 * 100);
        if (a > 0 && a <= 100) {
            this.renderVolumeScroll(a);
            putils.setCookie("volume", a, 7);
            this.streamingMp3.setVolume(a / 100);
            __data[this.pe].mute = false;
            putils.setCookie("volumeMute", "0", 7);
            $("#volumeControl" + this.pe).removeClass("mute");
            $("#volumeCurrent" + this.pe).removeClass("hide")
        } else if (a <= 0) {
            this.renderVolumeScroll(0);
            this.streamingMp3.mute();
            __data[this.pe].mute = true;
            putils.setCookie("volume", "0", 7);
            putils.setCookie("volumeMute", "1", 7);
            $("#volumeControl" + this.pe).addClass("mute");
            $("#volumeCurrent" + this.pe).addClass("hide")
        }
    }
    ;
    this.renderVolumeScroll = function (a) {
        document.getElementById("volumeSliderHolder" + this.pe).style.bottom = a + "%";
        document.getElementById("volumeSliderCurrent" + this.pe).style.height = a + "%";
        if (a > 70) {
            $("#volumeCurrentInside" + this.pe).removeClass("v1").removeClass("v2").addClass("v3")
        } else if (a > 30) {
            $("#volumeCurrentInside" + this.pe).removeClass("v1").removeClass("v3").addClass("v2")
        } else if (a > 5) {
            $("#volumeCurrentInside" + this.pe).removeClass("v2").removeClass("v3").addClass("v1")
        } else {
            $("#volumeCurrentInside" + this.pe).removeClass("v2").removeClass("v3").removeClass("v1")
        }
    }
    ;
    this.setEventNextButtonAutoplay = function () {
        var a = this;
        $("#nextAutoPlayButton" + a.pe).click(function () {
            if (typeof autoplay != "undefined" && typeof autoplay.run != "undefined") {
                autoplay.trackingAutoplay = false;
                console.log(autoplay.trackingAutoplay);
                autoplay.run()
            }
        })
    }
    ;
    this.getArrayPlaylist = function () {
        var c = this.pe;
        if (__data[this.pe].arrayPlaylistRandomed.length > 0) {
            __data[this.pe].arrayPlaylistRandomed.forEach(function (a) {
                __data[c].arrayPlaylist.push(a)
            })
        } else {
            __data[this.pe].arrayPlaylist = [];
            for (var i = 0; i <= this.streamingMp3.listMp3.length - 1; i++) {
                if (__data[this.pe].curMp3Item.curPlayIndex != i) {
                    __data[this.pe].arrayPlaylist.push(i)
                }
            }
            __data[this.pe].arrayPlaylist.sort(function (a, b) {
                return 0.5 - Math.random()
            });
            __data[this.pe].arrayPlaylistRandomed = [];
            __data[this.pe].arrayPlaylistRandomed.push(__data[this.pe].curMp3Item.curPlayIndex);
            __data[this.pe].arrayPlaylist.forEach(function (a) {
                __data[c].arrayPlaylistRandomed.push(a)
            })
        }
    }
};
var __karaoke = function () {
    this.pe = "";
    this.parseLyric = null;
    this.streamingMp3 = null;
    this.load = function (a) {
        this.pe = a;
        __data[this.pe].peConfig.lyricTempStatus = true;
        this.mainFunction()
    }
    ;
    this.mainFunction = function () {
    }
    ;
    this.updateActiveIndex = function (a) {
        try {
            if (__data[this.pe].peConfig.lyricTempStatus == true) {
                var b = a * this.streamingMp3.getTotalTime() / 100;
                var c = __data[this.pe].curMp3Item.listLyric;
                for (activeLineIndex = 0; activeLineIndex < c.length; activeLineIndex++) {
                    if (activeLineIndex == 0 && b < c[activeLineIndex].start) {
                        __data[this.pe].curMp3Item.activeLineIndex = activeLineIndex;
                        $("#mp3Kara2" + this.pe).html("");
                        $("#mp3Kara1" + this.pe).html("");
                        break
                    } else {
                        if ((b >= c[activeLineIndex].start) && (b <= parseFloat(c[activeLineIndex].start) + parseFloat(c[activeLineIndex].duration) + 0.5)) {
                            __data[this.pe].curMp3Item.activeLineIndex = activeLineIndex;
                            if (c[activeLineIndex].pos == 1) {
                                $("#mp3Kara2" + this.pe).html("")
                            } else {
                                $("#mp3Kara1" + this.pe).html("")
                            }
                            this.renderLyric(c[activeLineIndex]);
                            this.renderLyric(c[activeLineIndex + 1]);
                            this.postionLyric(b, c[activeLineIndex]);
                            break
                        }
                    }
                }
            }
        } catch (e) {
        }
    }
    ;
    this.updateTime = function () {
        try {
            if (__data[this.pe].peConfig.lyricTempStatus) {
                if (typeof __data[this.pe].curMp3Item.listLyric != "undefined" && __data[this.pe].curMp3Item.listLyric != null) {
                    var a = this.streamingMp3.getCurrentTime();
                    var b = __data[this.pe].curMp3Item.listLyric;
                    try {
                        var c = __data[this.pe].curMp3Item.activeLineIndex;
                        if (c == b.length - 1) {
                            b[b.length - 1].duration = this.streamingMp3.getTotalTime() - b[b.length - 1].start - 0.5
                        }
                        if ((a >= b[c].start) && (a <= parseFloat(b[c].start) + parseFloat(b[c].duration) + 0.2)) {
                            if (c == 0) {
                                this.renderLyric(b[0])
                            }
                            this.postionLyric(a, b[c]);
                            if (c < b.length - 1) {
                                this.postionLyric(a, b[c + 1])
                            }
                            if (__data[this.pe].curMp3Item.showNextLine && (c < (b.length - 1))) {
                                this.renderLyric(b[c + 1]);
                                __data[this.pe].curMp3Item.showNextLine = false
                            }
                        } else if (a > b[c].start + b[c].duration) {
                            if (c < (b.length - 1)) {
                                ++c;
                                __data[this.pe].curMp3Item.activeLineIndex = c;
                                __data[this.pe].curMp3Item.showNextLine = true
                            } else {
                            }
                        }
                        if (c + 1 < b.length) {
                            if (a > b[c + 1].start - 4 && b[c].duration > 5 && $.trim(b[c].content) == "") {
                                if (a < b[c + 1].start - 3) {
                                    if (b[c].pos == 1) {
                                        document.getElementById("mp3Kara1" + this.pe).innerHTML = '3<div id="mp3KaraRun1' + this.pe + '" class="run" style="width:0%;"></div>'
                                    } else {
                                        document.getElementById("mp3Kara2" + this.pe).innerHTML = '3<div id="mp3KaraRun2' + this.pe + '" class="run" style="width:0%;"></div>'
                                    }
                                } else if (a < b[c + 1].start - 2) {
                                    if (b[c].pos == 1) {
                                        document.getElementById("mp3Kara1" + this.pe).innerHTML = '2<div id="mp3KaraRun1' + this.pe + '" class="run" style="width:0%;"></div>'
                                    } else {
                                        document.getElementById("mp3Kara2" + this.pe).innerHTML = '2<div id="mp3KaraRun2' + this.pe + '" class="run" style="width:0%;"></div>'
                                    }
                                } else if (a < b[c + 1].start - 0.5) {
                                    if (b[c].pos == 1) {
                                        document.getElementById("mp3Kara1" + this.pe).innerHTML = '1<div id="mp3KaraRun1' + this.pe + '" class="run" style="width:0%;"></div>'
                                    } else {
                                        document.getElementById("mp3Kara2" + this.pe).innerHTML = '1<div id="mp3KaraRun2' + this.pe + '" class="run" style="width:0%;"></div>'
                                    }
                                } else {
                                    if (b[c].pos == 1) {
                                        document.getElementById("mp3Kara1" + this.pe).innerHTML = ''
                                    } else {
                                        document.getElementById("mp3Kara2" + this.pe).innerHTML = ''
                                    }
                                }
                            }
                        }
                    } catch (e) {
                    }
                } else {
                    document.getElementById("mp3Kara2" + this.pe).innerHTML = '<span style="font-size: 16px;color: #ccc; opacity: 0.5; font-weight: 600;">(Chưa có lời karaoke)</span>';
                    document.getElementById("mp3Kara1" + this.pe).innerHTML = ''
                }
            } else {
                document.getElementById("mp3Kara2" + this.pe).innerHTML = '';
                document.getElementById("mp3Kara1" + this.pe).innerHTML = ''
            }
        } catch (e) {
            if (__data[this.pe].mp3.length == 0) {
                document.getElementById("mp3Kara2" + this.pe).innerHTML = '<span style="font-size: 16px;color: #ccc; opacity: 0.5; font-weight: 600;">Chưa có bài hát nào</span>'
            }
        }
    }
    ;
    this.renderLyric = function (a) {
        if (typeof a != "undefined" && typeof a.id != "undefined" && __data[this.pe].curMp3Item.activeLineIndex != a.id || __data[this.pe].curMp3Item.activeLineIndex == 0) {
            if (a.pos == 1) {
                document.getElementById("mp3Kara1" + this.pe).innerHTML = a.content + '<div id="mp3KaraRun1' + this.pe + '" class="run" style="width:0%;">' + a.content + '</div>'
            } else {
                document.getElementById("mp3Kara2" + this.pe).innerHTML = a.content + '<div id="mp3KaraRun2' + this.pe + '" class="run" style="width:0%;">' + a.content + '</div>'
            }
        }
    }
    ;
    this.hideLyric = function (a) {
        if (a.pos == 1) {
            document.getElementById("mp3Kara1" + this.pe).innerHTML = ""
        } else {
            document.getElementById("mp3Kara2" + this.pe).innerHTML = ""
        }
    }
    ;
    this.postionLyric = function (a, b) {
        try {
            if (b.pos == 1) {
                document.getElementById("mp3KaraRun1" + this.pe).style.width = ((a - b.start) / b.duration * 100) + "%"
            } else {
                document.getElementById("mp3KaraRun2" + this.pe).style.width = ((a - b.start) / b.duration * 100) + "%"
            }
        } catch (e) {
        }
    }
};
var __mainScreenMp3 = function () {
    this.pe = "";
    this.item = {};
    this.ads = new __parseXMLAds();
    this.load = function (a) {
        __debug.log("MainScreen.load", a);
        this.pe = a;
        this.mainFunction();
        if (__data[a].mp3[__data[this.pe].peConfig.curPlayIndex] != undefined && __data[a].mp3[__data[this.pe].peConfig.curPlayIndex] != null) {
            this.item = __data[a].mp3[__data[this.pe].peConfig.curPlayIndex]
        }
        document.getElementById("mp3" + a).oncontextmenu = function () {
            return false
        }
    }
    ;
    this.mainFunction = function () {
        this.loadAds();
        var a = this;
        $("#mainScreen" + this.pe).bind("resetAds", function () {
            a.loadAds()
        })
    }
    ;
    this.loadAds = function () {
        if (__data[this.pe].adsMp3.open) {
            console.log(__data[this.pe].adsMp3.open);
            this.ads.load(this.pe);
            this.ads.parse(this)
        }
    }
    ;
    this.xmlAdsParseComplete = function () {
        if (putils.getQueryVariable(window.location.href.toString(), "debug") == "true") {
            console.log(__data[this.pe].adsMp3.iframe)
        }
        if (typeof __data[this.pe].adsMp3.iframe != 'undefined' && __data[this.pe].adsMp3.iframe != '') {
            if (typeof __data[this.pe].adsMp3.linkClick != 'undefined' && __data[this.pe].adsMp3.linkClick != '') {
                __data[this.pe].adsMp3.iframe += "?click_url=" + encodeURIComponent(__data[this.pe].adsMp3.linkClick)
            }
            document.getElementById("coverImage" + this.pe).innerHTML = '<iframe scrolling="no" src="' + __data[this.pe].adsMp3.iframe + '" width="300" height="250" border="0" style="border:none;"></iframe>'
        } else if (typeof __data[this.pe].adsMp3.linkClick != 'undefined' && __data[this.pe].adsMp3.linkClick != '') {
            document.getElementById("coverImage" + this.pe).innerHTML = '<a href="' + __data[this.pe].adsMp3.linkClick + '" target="_blank"><img src="' + __data[this.pe].adsMp3.fallback + '" width="300" height="250"/></a>'
        } else if (putils.supportFlash() && !putils.isFirefox()) {
            if (typeof __data[this.pe].adsMp3.linkClick != 'undefined' && __data[this.pe].adsMp3.linkClick != '') {
                __data[this.pe].adsMp3.file += "&clickTAG=" + encodeURIComponent(__data[this.pe].adsMp3.linkClick)
            }
            document.getElementById("coverImage" + this.pe).innerHTML = '<embed id="mediaFlashPlayerAdv" bgcolor="#000000" allownetworking="all" quality="high" wmode="transparent" allowscriptaccess="always" allowfullscreen="true" width="300" height="250" style="height: 250px !important;" src="' + __data[this.pe].adsMp3.file + '"/>'
        }
        if (putils.getQueryVariable(__data[this.pe].adsMp3.file, "view") == 'yes') {
            var a = ('https:' == document.location.protocol ? 'https://' : 'http://') + "www.nhaccuatui.com/viewqc/" + putils.getQueryVariable(__data[this.pe].adsMp3.file, "bid") + "/" + putils.getQueryVariable(__data[this.pe].adsMp3.file, "skey");
            try {
                $.get(a, {}, function () {
                })
            } catch (e) {
            }
        }
    }
};
var __switchQuality = function () {
    this.pe = "";
    this.streamingMp3 = null;
    this.load = function (a) {
        __debug.log("SwitchQuality.load", a);
        this.pe = a;
        this.mainFunction();
        this.reset()
    }
    ;
    this.mainFunction = function () {
        var a = this;
        if (putils.isMobileDevice()) {
            $("#switchQuality" + this.pe).addClass("hide")
        } else {
            $("#mp3" + this.pe).bind("ended", function () {
                a.reset()
            });
            $("#switchQuality" + this.pe).bind("resetSwitch", function () {
                a.reset()
            });
            $("#SwitchQualityDefault" + this.pe).click(function () {
                $("#SwitchQualityDefault" + a.pe).addClass("active");
                $("#SwitchQualityHigh" + a.pe).removeClass("active");
                $("#SwitchQualityLow" + a.pe).removeClass("active");
                $("#switchQualityText" + a.pe).removeClass("hd");
                $("#txtQLT" + a.pe).html("128kbps");
                a.switch("default")
            });
            $("#SwitchQualityHigh" + this.pe).click(function () {
                $("#SwitchQualityDefault" + a.pe).removeClass("active");
                $("#SwitchQualityHigh" + a.pe).addClass("active");
                $("#SwitchQualityLow" + a.pe).removeClass("active");
                $("#switchQualityText" + a.pe).addClass("hd");
                $("#txtQLT" + a.pe).html("320kbps");
                a.switch("high")
            });
            $("#SwitchQualityPU" + this.pe).click(function () {
                try {
                    putils.setCookie("qualityPlayerMp3", "high", 7);
                    NCTAdv.annouceOffAdv("switchQuality")
                } catch (e) {
                    console.log("OffAdvNotiError")
                }
            })
        }
    }
    ;
    this.reset = function () {
        var a = __data[this.pe].curMp3Item;
        var b = 1;
        if (!putils.isMobileDevice()) {
            if (typeof a.highquality != "undefined" && a.highquality != "") {
                b++;
                $("#SwitchQualityHigh" + this.pe).removeClass("hide");
                $("#SwitchQualityPU" + this.pe).addClass("hide")
            } else {
                try {
                    if (a.hasHQ == "true") {
                        b++;
                        $("#SwitchQualityPU" + this.pe).removeClass("hide")
                    } else {
                        $("#SwitchQualityPU" + this.pe).addClass("hide")
                    }
                } catch (e) {
                    $("#SwitchQualityPU" + this.pe).addClass("hide")
                }
                $("#SwitchQualityHigh" + this.pe).addClass("hide")
            }
            if (b == 1) {
                $("#boxSwitchQuality" + this.pe).addClass("hide");
                $("#SwitchQualityText1" + this.pe).addClass("hide");
                $("#SwitchQualityHigh" + this.pe).addClass("hide");
                $("#txtQLT" + this.pe).html("128kbps");
                $("#switchQualityText" + this.pe).css("cursor", "default")
            } else {
                $("#boxSwitchQuality" + this.pe).removeClass("hide");
                $("#SwitchQualityDefault" + this.pe).removeClass("hide");
                $("#switchQualityText" + this.pe).css("cursor", "pointer")
            }
            $("#SwitchQualityDefault" + this.pe).removeClass("active");
            $("#SwitchQualityHigh" + this.pe).removeClass("active");
            $("#SwitchQualityLow" + this.pe).removeClass("active");
            $("#switchQualityText" + this.pe).removeClass("hd");
            if (__data[this.pe].curQuality == "default") {
                $("#SwitchQualityDefault" + this.pe).addClass("active");
                $("#txtQLT" + this.pe).html("128kbps")
            } else if (__data[this.pe].curQuality == "high") {
                $("#SwitchQualityHigh" + this.pe).addClass("active");
                $("#switchQualityText" + this.pe).addClass("hd");
                $("#txtQLT" + this.pe).html("320kbps")
            }
        }
    }
    ;
    this.switch = function (a) {
        if (__data[this.pe].curQuality != a) {
            var b = __data[this.pe].curMp3Item.played;
            this.streamingMp3.quality = a;
            putils.setCookie("qualityPlayerMp3", a, 7);
            __data[this.pe].curQuality = a;
            __data[this.pe].curMp3Item.reloadTime = this.streamingMp3.getCurrentTime();
            this.streamingMp3.renSource(__data[this.pe].curMp3Item);
            this.streamingMp3.loadStream();
            if (b) {
                __data[this.pe].curMp3Item.played = true;
                this.streamingMp3.play()
            }
        }
    }
    ;
    this.detectSpeed = function () {
        var h = this;
        $(document).ready(function () {
            var d = __data[h.pe].peConfig.testSpeedStatic + "?n=" + Math.random();
            var e, endTime;
            var f = __data[h.pe].peConfig.testSpeedSize;
            var g = new Image();
            g.onload = function () {
                endTime = (new Date()).getTime();
                showResults()
            }
            ;
            e = (new Date()).getTime();
            g.src = d;

            function showResults() {
                var a = (endTime - e) / 5000;
                var b = (f / a).toFixed(2);
                var c = (b / 1024).toFixed(2);
                console.log("Your connection speed is: \n" + a + "\n" + f + "\n" + b + " kbs\n" + c + " Mbs\n")
            }
        })
    }
};
var __shortKey = function () {
    this.pe = "";
    this.peConfig = {};
    this.mainScreen;
    this.controlbar;
    this.streamingMp3;
    this.load = function (b) {
        __debug.log("NCTPlayerMp3.load", b);
        this.pe = b;
        this.peConfig = __data[b].peConfig;
        var c = this;
        var d = false;
        var f = true;
        $(document).click(function () {
            if ($("#" + b).is(":hover")) {
                d = true;
                f = true
            } else {
                d = false;
                f = false
            }
            if (event.which == 70) {
                f = true
            }
            if (event.which == 77) {
                f = true
            }
        });
        $(document).on('mousewheel', function (e) {
            if ($('#volumeControl' + b).is(":hover")) {
                if (e.originalEvent.wheelDelta > 0) {
                    c.setVolume(5)
                } else {
                    c.setVolume(-5)
                }
                return false
            }
        });
        window.addEventListener("keydown", function (e) {
            if (d) {
                if ([32, 35, 36].indexOf(e.keyCode) > -1) {
                    e.preventDefault()
                }
            }
        }, false);
        var g = this.streamingMp3;
        $(document).keydown(function (a) {
            if (!$('input').is(":focus") && !$('textarea').is(":focus")) {
                if ((a.which == 75 || a.which == 32) && f == true) {
                    a.preventDefault();
                    if (__data[b].curMp3Item.played) {
                        $("#mp3" + b).trigger("pauseMp3")
                    } else {
                        $("#mp3" + b).trigger("playMp3")
                    }
                } else if (a.which == 38 && f == true) {
                    a.preventDefault();
                    c.setVolume(5)
                } else if (a.which == 40 && f == true) {
                    a.preventDefault();
                    c.setVolume(-5)
                } else if (a.which == 78 && a.shiftKey) {
                    if (!$("#nextButton" + b).hasClass("hide")) {
                        a.preventDefault();
                        $("#nextButton" + b).click();
                        $('#nextAutoPlayButton' + b).click()
                    }
                } else if (a.which == 80 && a.shiftKey) {
                    if (!$("#prevButton" + b).hasClass("hide")) {
                        a.preventDefault();
                        $("#prevButton" + b).click()
                    }
                } else if (a.which == 77 && !a.ctrlKey) {
                    a.preventDefault();
                    $("#volume" + b).click()
                } else if ((a.which == 48 || a.which == 36) && f == true) {
                    a.preventDefault();
                    c.streamingMp3.seekSecond(1)
                } else if (a.which == 35 && f == true) {
                    a.preventDefault();
                    c.streamingMp3.seek(99)
                }
            }
        })
    }
    ;
    this.setVolume = function (a) {
        var b = putils.getCookie("volume");
        if (b == null || b == "") {
            b = 80;
            putils.setCookie("volume", b, 7)
        }
        var c = parseInt(b) + parseInt(a);
        if (c > 100)
            c = 100;
        if (c < 0)
            c = 0;
        if (c > 0 && c <= 100) {
            this.renderVolumeScroll(c);
            putils.setCookie("volume", c, 7);
            this.setVolumeLink(c / 100);
            __data[this.pe].mute = false;
            putils.setCookie("volumeMute", "0", 7);
            $("#volumeControl" + this.pe).removeClass("mute");
            $("#volumeCurrent" + this.pe).removeClass("hide")
        } else if (c <= 0) {
            this.renderVolumeScroll(0);
            this.mute();
            __data[this.pe].mute = true;
            putils.setCookie("volume", "0", 7);
            putils.setCookie("volumeMute", "1", 7);
            $("#volumeControl" + this.pe).addClass("mute");
            $("#volumeCurrent" + this.pe).addClass("hide")
        }
        $('#volumeSlider' + this.pe).addClass("show");
        var d = this.pe;
        if (typeof __t == 'undefined')
            __t = 0;
        clearTimeout(__t);
        __t = setTimeout(function () {
            $('#volumeSlider' + d).removeClass('show')
        }, 3000)
    }
    ;
    this.mute = function () {
        if (__data[this.pe].peConfig.flashEmbed) {
            var a = this.pe;
            var b = function () {
                try {
                    flashMovie("mediaFlashPlayer" + a).volume(0)
                } catch (e) {
                    setTimeout(function () {
                        b()
                    }, 1000)
                }
            };
            b()
        } else {
            document.getElementById("mp3" + this.pe).volume = 0
        }
    }
    ;
    this.unMute = function () {
        if (__data[this.pe].peConfig.flashEmbed) {
            try {
                flashMovie("mediaFlashPlayer" + this.pe).volume(__data[this.pe].volume)
            } catch (e) {
                var a = this.pe;
                setTimeout(function () {
                    flashMovie("mediaFlashPlayer" + a).volume(__data[a].volume)
                }, 1000)
            }
        } else {
            document.getElementById("mp3" + this.pe).volume = __data[this.pe].volume
        }
    }
    ;
    this.setVolumeLink = function (a) {
        if (!isNaN(a)) {
            __data[this.pe].volume = a;
            if (__data[this.pe].peConfig.flashEmbed) {
                var b = this.pe;
                var c = function () {
                    try {
                        flashMovie("mediaFlashPlayer" + b).volume(a)
                    } catch (e) {
                        setTimeout(function () {
                            c()
                        }, 1000)
                    }
                };
                c()
            }
            document.getElementById("mp3" + this.pe).volume = a
        }
    }
    ;
    this.renderVolumeScroll = function (a) {
        document.getElementById("volumeSliderHolder" + this.pe).style.bottom = a + "%";
        document.getElementById("volumeSliderCurrent" + this.pe).style.height = a + "%";
        if (a > 70) {
            $("#volumeCurrentInside" + this.pe).removeClass("v1").removeClass("v2").addClass("v3")
        } else if (a > 30) {
            $("#volumeCurrentInside" + this.pe).removeClass("v1").removeClass("v3").addClass("v2")
        } else if (a > 5) {
            $("#volumeCurrentInside" + this.pe).removeClass("v2").removeClass("v3").addClass("v1")
        } else {
            $("#volumeCurrentInside" + this.pe).removeClass("v2").removeClass("v3").removeClass("v1")
        }
    }
};
var utf8char = [];
utf8char['10'] = '';
utf8char['13'] = '\n';
utf8char['32'] = ' ';
utf8char['33'] = '!';
utf8char['34'] = '"';
utf8char['35'] = '#';
utf8char['36'] = '$';
utf8char['37'] = '%';
utf8char['38'] = '&';
utf8char['39'] = '\'';
utf8char['40'] = '(';
utf8char['41'] = ')';
utf8char['42'] = '*';
utf8char['43'] = '+';
utf8char['44'] = ',';
utf8char['45'] = '-';
utf8char['46'] = '.';
utf8char['47'] = '/';
utf8char['48'] = '0';
utf8char['49'] = '1';
utf8char['50'] = '2';
utf8char['51'] = '3';
utf8char['52'] = '4';
utf8char['53'] = '5';
utf8char['54'] = '6';
utf8char['55'] = '7';
utf8char['56'] = '8';
utf8char['57'] = '9';
utf8char['58'] = ':';
utf8char['59'] = ';';
utf8char['60'] = '<';
utf8char['61'] = '=';
utf8char['62'] = '>';
utf8char['63'] = '?';
utf8char['64'] = '@';
utf8char['65'] = 'A';
utf8char['66'] = 'B';
utf8char['67'] = 'C';
utf8char['68'] = 'D';
utf8char['69'] = 'E';
utf8char['70'] = 'F';
utf8char['71'] = 'G';
utf8char['72'] = 'H';
utf8char['73'] = 'I';
utf8char['74'] = 'J';
utf8char['75'] = 'K';
utf8char['76'] = 'L';
utf8char['77'] = 'M';
utf8char['78'] = 'N';
utf8char['79'] = 'O';
utf8char['80'] = 'P';
utf8char['81'] = 'Q';
utf8char['82'] = 'R';
utf8char['83'] = 'S';
utf8char['84'] = 'T';
utf8char['85'] = 'U';
utf8char['86'] = 'V';
utf8char['87'] = 'W';
utf8char['88'] = 'X';
utf8char['89'] = 'Y';
utf8char['90'] = 'Z';
utf8char['91'] = '[';
utf8char['92'] = '\\';
utf8char['93'] = ']';
utf8char['94'] = '^';
utf8char['95'] = '_';
utf8char['96'] = '`';
utf8char['97'] = 'a';
utf8char['98'] = 'b';
utf8char['99'] = 'c';
utf8char['100'] = 'd';
utf8char['101'] = 'e';
utf8char['102'] = 'f';
utf8char['103'] = 'g';
utf8char['104'] = 'h';
utf8char['105'] = 'i';
utf8char['106'] = 'j';
utf8char['107'] = 'k';
utf8char['108'] = 'l';
utf8char['109'] = 'm';
utf8char['110'] = 'n';
utf8char['111'] = 'o';
utf8char['112'] = 'p';
utf8char['113'] = 'q';
utf8char['114'] = 'r';
utf8char['115'] = 's';
utf8char['116'] = 't';
utf8char['117'] = 'u';
utf8char['118'] = 'v';
utf8char['119'] = 'w';
utf8char['120'] = 'x';
utf8char['121'] = 'y';
utf8char['122'] = 'z';
utf8char['123'] = '{';
utf8char['124'] = '|';
utf8char['125'] = '}';
utf8char['126'] = '~';
utf8char['127'] = '';
utf8char['194 161'] = '¡';
utf8char['194 162'] = '¢';
utf8char['194 163'] = '£';
utf8char['194 164'] = '¤';
utf8char['194 165'] = '¥';
utf8char['194 166'] = '¦';
utf8char['194 167'] = '§';
utf8char['194 168'] = '¨';
utf8char['194 169'] = '©';
utf8char['194 170'] = 'ª';
utf8char['194 171'] = '«';
utf8char['194 172'] = '¬';
utf8char['194 173'] = '';
utf8char['194 174'] = '®';
utf8char['194 175'] = '¯';
utf8char['194 176'] = '°';
utf8char['194 177'] = '±';
utf8char['194 178'] = '²';
utf8char['194 179'] = '³';
utf8char['194 180'] = '´';
utf8char['194 181'] = 'µ';
utf8char['194 182'] = '¶';
utf8char['194 183'] = '·';
utf8char['194 184'] = '¸';
utf8char['194 185'] = '¹';
utf8char['194 186'] = 'º';
utf8char['194 187'] = '»';
utf8char['194 188'] = '¼';
utf8char['194 189'] = '½';
utf8char['194 190'] = '¾';
utf8char['194 191'] = '¿';
utf8char['195 128'] = 'À';
utf8char['195 129'] = 'Á';
utf8char['195 130'] = 'Â';
utf8char['195 131'] = 'Ã';
utf8char['195 132'] = 'Ä';
utf8char['195 133'] = 'Å';
utf8char['195 134'] = 'Æ';
utf8char['195 135'] = 'Ç';
utf8char['195 136'] = 'È';
utf8char['195 137'] = 'É';
utf8char['195 138'] = 'Ê';
utf8char['195 139'] = 'Ë';
utf8char['195 140'] = 'Ì';
utf8char['195 141'] = 'Í';
utf8char['195 142'] = 'Î';
utf8char['195 143'] = 'Ï';
utf8char['195 144'] = 'Ð';
utf8char['195 145'] = 'Ñ';
utf8char['195 146'] = 'Ò';
utf8char['195 147'] = 'Ó';
utf8char['195 148'] = 'Ô';
utf8char['195 149'] = 'Õ';
utf8char['195 150'] = 'Ö';
utf8char['195 151'] = '×';
utf8char['195 152'] = 'Ø';
utf8char['195 153'] = 'Ù';
utf8char['195 154'] = 'Ú';
utf8char['195 155'] = 'Û';
utf8char['195 156'] = 'Ü';
utf8char['195 157'] = 'Ý';
utf8char['195 158'] = 'Þ';
utf8char['195 159'] = 'ß';
utf8char['195 160'] = 'à';
utf8char['195 161'] = 'á';
utf8char['195 162'] = 'â';
utf8char['195 163'] = 'ã';
utf8char['195 164'] = 'ä';
utf8char['195 165'] = 'å';
utf8char['195 166'] = 'æ';
utf8char['195 167'] = 'ç';
utf8char['195 168'] = 'è';
utf8char['195 169'] = 'é';
utf8char['195 170'] = 'ê';
utf8char['195 171'] = 'ë';
utf8char['195 172'] = 'ì';
utf8char['195 173'] = 'í';
utf8char['195 174'] = 'î';
utf8char['195 175'] = 'ï';
utf8char['195 176'] = 'ð';
utf8char['195 177'] = 'ñ';
utf8char['195 178'] = 'ò';
utf8char['195 179'] = 'ó';
utf8char['195 180'] = 'ô';
utf8char['195 181'] = 'õ';
utf8char['195 182'] = 'ö';
utf8char['195 183'] = '÷';
utf8char['195 184'] = 'ø';
utf8char['195 185'] = 'ù';
utf8char['195 186'] = 'ú';
utf8char['195 187'] = 'û';
utf8char['195 188'] = 'ü';
utf8char['195 189'] = 'ý';
utf8char['195 190'] = 'þ';
utf8char['195 191'] = 'ÿ';
utf8char['196 128'] = 'Ā';
utf8char['196 129'] = 'ā';
utf8char['196 130'] = 'Ă';
utf8char['196 131'] = 'ă';
utf8char['196 132'] = 'Ą';
utf8char['196 133'] = 'ą';
utf8char['196 134'] = 'Ć';
utf8char['196 135'] = 'ć';
utf8char['196 136'] = 'Ĉ';
utf8char['196 137'] = 'ĉ';
utf8char['196 138'] = 'Ċ';
utf8char['196 139'] = 'ċ';
utf8char['196 140'] = 'Č';
utf8char['196 141'] = 'č';
utf8char['196 142'] = 'Ď';
utf8char['196 143'] = 'ď';
utf8char['196 144'] = 'Đ';
utf8char['196 145'] = 'đ';
utf8char['196 146'] = 'Ē';
utf8char['196 147'] = 'ē';
utf8char['196 148'] = 'Ĕ';
utf8char['196 149'] = 'ĕ';
utf8char['196 150'] = 'Ė';
utf8char['196 151'] = 'ė';
utf8char['196 152'] = 'Ę';
utf8char['196 153'] = 'ę';
utf8char['196 154'] = 'Ě';
utf8char['196 155'] = 'ě';
utf8char['196 156'] = 'Ĝ';
utf8char['196 157'] = 'ĝ';
utf8char['196 158'] = 'Ğ';
utf8char['196 159'] = 'ğ';
utf8char['196 160'] = 'Ġ';
utf8char['196 161'] = 'ġ';
utf8char['196 162'] = 'Ģ';
utf8char['196 163'] = 'ģ';
utf8char['196 164'] = 'Ĥ';
utf8char['196 165'] = 'ĥ';
utf8char['196 166'] = 'Ħ';
utf8char['196 167'] = 'ħ';
utf8char['196 168'] = 'Ĩ';
utf8char['196 169'] = 'ĩ';
utf8char['196 170'] = 'Ī';
utf8char['196 171'] = 'ī';
utf8char['196 172'] = 'Ĭ';
utf8char['196 173'] = 'ĭ';
utf8char['196 174'] = 'Į';
utf8char['196 175'] = 'į';
utf8char['196 176'] = 'İ';
utf8char['196 177'] = 'ı';
utf8char['196 178'] = 'Ĳ';
utf8char['196 179'] = 'ĳ';
utf8char['196 180'] = 'Ĵ';
utf8char['196 181'] = 'ĵ';
utf8char['196 182'] = 'Ķ';
utf8char['196 183'] = 'ķ';
utf8char['196 184'] = 'ĸ';
utf8char['196 185'] = 'Ĺ';
utf8char['196 186'] = 'ĺ';
utf8char['196 187'] = 'Ļ';
utf8char['196 188'] = 'ļ';
utf8char['196 189'] = 'Ľ';
utf8char['196 190'] = 'ľ';
utf8char['196 191'] = 'Ŀ';
utf8char['197 128'] = 'ŀ';
utf8char['197 129'] = 'Ł';
utf8char['197 130'] = 'ł';
utf8char['197 131'] = 'Ń';
utf8char['197 132'] = 'ń';
utf8char['197 133'] = 'Ņ';
utf8char['197 134'] = 'ņ';
utf8char['197 135'] = 'Ň';
utf8char['197 136'] = 'ň';
utf8char['197 137'] = 'ŉ';
utf8char['197 138'] = 'Ŋ';
utf8char['197 139'] = 'ŋ';
utf8char['197 140'] = 'Ō';
utf8char['197 141'] = 'ō';
utf8char['197 142'] = 'Ŏ';
utf8char['197 143'] = 'ŏ';
utf8char['197 144'] = 'Ő';
utf8char['197 145'] = 'ő';
utf8char['197 146'] = 'Œ';
utf8char['197 147'] = 'œ';
utf8char['197 148'] = 'Ŕ';
utf8char['197 149'] = 'ŕ';
utf8char['197 150'] = 'Ŗ';
utf8char['197 151'] = 'ŗ';
utf8char['197 152'] = 'Ř';
utf8char['197 153'] = 'ř';
utf8char['197 154'] = 'Ś';
utf8char['197 155'] = 'ś';
utf8char['197 156'] = 'Ŝ';
utf8char['197 157'] = 'ŝ';
utf8char['197 158'] = 'Ş';
utf8char['197 159'] = 'ş';
utf8char['197 160'] = 'Š';
utf8char['197 161'] = 'š';
utf8char['197 162'] = 'Ţ';
utf8char['197 163'] = 'ţ';
utf8char['197 164'] = 'Ť';
utf8char['197 165'] = 'ť';
utf8char['197 166'] = 'Ŧ';
utf8char['197 167'] = 'ŧ';
utf8char['197 168'] = 'Ũ';
utf8char['197 169'] = 'ũ';
utf8char['197 170'] = 'Ū';
utf8char['197 171'] = 'ū';
utf8char['197 172'] = 'Ŭ';
utf8char['197 173'] = 'ŭ';
utf8char['197 174'] = 'Ů';
utf8char['197 175'] = 'ů';
utf8char['197 176'] = 'Ű';
utf8char['197 177'] = 'ű';
utf8char['197 178'] = 'Ų';
utf8char['197 179'] = 'ų';
utf8char['197 180'] = 'Ŵ';
utf8char['197 181'] = 'ŵ';
utf8char['197 182'] = 'Ŷ';
utf8char['197 183'] = 'ŷ';
utf8char['197 184'] = 'Ÿ';
utf8char['197 185'] = 'Ź';
utf8char['197 186'] = 'ź';
utf8char['197 187'] = 'Ż';
utf8char['197 188'] = 'ż';
utf8char['197 189'] = 'Ž';
utf8char['197 190'] = 'ž';
utf8char['197 191'] = 'ſ';
utf8char['198 128'] = 'ƀ';
utf8char['198 129'] = 'Ɓ';
utf8char['198 130'] = 'Ƃ';
utf8char['198 131'] = 'ƃ';
utf8char['198 132'] = 'Ƅ';
utf8char['198 133'] = 'ƅ';
utf8char['198 134'] = 'Ɔ';
utf8char['198 135'] = 'Ƈ';
utf8char['198 136'] = 'ƈ';
utf8char['198 137'] = 'Ɖ';
utf8char['198 138'] = 'Ɗ';
utf8char['198 139'] = 'Ƌ';
utf8char['198 140'] = 'ƌ';
utf8char['198 141'] = 'ƍ';
utf8char['198 142'] = 'Ǝ';
utf8char['198 143'] = 'Ə';
utf8char['198 144'] = 'Ɛ';
utf8char['198 145'] = 'Ƒ';
utf8char['198 146'] = 'ƒ';
utf8char['198 147'] = 'Ɠ';
utf8char['198 148'] = 'Ɣ';
utf8char['198 149'] = 'ƕ';
utf8char['198 150'] = 'Ɩ';
utf8char['198 151'] = 'Ɨ';
utf8char['198 152'] = 'Ƙ';
utf8char['198 153'] = 'ƙ';
utf8char['198 154'] = 'ƚ';
utf8char['198 155'] = 'ƛ';
utf8char['198 156'] = 'Ɯ';
utf8char['198 157'] = 'Ɲ';
utf8char['198 158'] = 'ƞ';
utf8char['198 159'] = 'Ɵ';
utf8char['198 160'] = 'Ơ';
utf8char['198 161'] = 'ơ';
utf8char['198 162'] = 'Ƣ';
utf8char['198 163'] = 'ƣ';
utf8char['198 164'] = 'Ƥ';
utf8char['198 165'] = 'ƥ';
utf8char['198 166'] = 'Ʀ';
utf8char['198 167'] = 'Ƨ';
utf8char['198 168'] = 'ƨ';
utf8char['198 169'] = 'Ʃ';
utf8char['198 170'] = 'ƪ';
utf8char['198 171'] = 'ƫ';
utf8char['198 172'] = 'Ƭ';
utf8char['198 173'] = 'ƭ';
utf8char['198 174'] = 'Ʈ';
utf8char['198 175'] = 'Ư';
utf8char['198 176'] = 'ư';
utf8char['198 177'] = 'Ʊ';
utf8char['198 178'] = 'Ʋ';
utf8char['198 179'] = 'Ƴ';
utf8char['198 180'] = 'ƴ';
utf8char['198 181'] = 'Ƶ';
utf8char['198 182'] = 'ƶ';
utf8char['198 183'] = 'Ʒ';
utf8char['198 184'] = 'Ƹ';
utf8char['198 185'] = 'ƹ';
utf8char['198 186'] = 'ƺ';
utf8char['198 187'] = 'ƻ';
utf8char['198 188'] = 'Ƽ';
utf8char['198 189'] = 'ƽ';
utf8char['198 190'] = 'ƾ';
utf8char['198 191'] = 'ƿ';
utf8char['199 128'] = 'ǀ';
utf8char['199 129'] = 'ǁ';
utf8char['199 130'] = 'ǂ';
utf8char['199 131'] = 'ǃ';
utf8char['199 132'] = 'Ǆ';
utf8char['199 133'] = 'ǅ';
utf8char['199 134'] = 'ǆ';
utf8char['199 135'] = 'Ǉ';
utf8char['199 136'] = 'ǈ';
utf8char['199 137'] = 'ǉ';
utf8char['199 138'] = 'Ǌ';
utf8char['199 139'] = 'ǋ';
utf8char['199 140'] = 'ǌ';
utf8char['199 141'] = 'Ǎ';
utf8char['199 142'] = 'ǎ';
utf8char['199 143'] = 'Ǐ';
utf8char['199 144'] = 'ǐ';
utf8char['199 145'] = 'Ǒ';
utf8char['199 146'] = 'ǒ';
utf8char['199 147'] = 'Ǔ';
utf8char['199 148'] = 'ǔ';
utf8char['199 149'] = 'Ǖ';
utf8char['199 150'] = 'ǖ';
utf8char['199 151'] = 'Ǘ';
utf8char['199 152'] = 'ǘ';
utf8char['199 153'] = 'Ǚ';
utf8char['199 154'] = 'ǚ';
utf8char['199 155'] = 'Ǜ';
utf8char['199 156'] = 'ǜ';
utf8char['199 157'] = 'ǝ';
utf8char['199 158'] = 'Ǟ';
utf8char['199 159'] = 'ǟ';
utf8char['199 160'] = 'Ǡ';
utf8char['199 161'] = 'ǡ';
utf8char['199 162'] = 'Ǣ';
utf8char['199 163'] = 'ǣ';
utf8char['199 164'] = 'Ǥ';
utf8char['199 165'] = 'ǥ';
utf8char['199 166'] = 'Ǧ';
utf8char['199 167'] = 'ǧ';
utf8char['199 168'] = 'Ǩ';
utf8char['199 169'] = 'ǩ';
utf8char['199 170'] = 'Ǫ';
utf8char['199 171'] = 'ǫ';
utf8char['199 172'] = 'Ǭ';
utf8char['199 173'] = 'ǭ';
utf8char['199 174'] = 'Ǯ';
utf8char['199 175'] = 'ǯ';
utf8char['199 176'] = 'ǰ';
utf8char['199 177'] = 'Ǳ';
utf8char['199 178'] = 'ǲ';
utf8char['199 179'] = 'ǳ';
utf8char['199 180'] = 'Ǵ';
utf8char['199 181'] = 'ǵ';
utf8char['199 182'] = 'Ƕ';
utf8char['199 183'] = 'Ƿ';
utf8char['199 184'] = 'Ǹ';
utf8char['199 185'] = 'ǹ';
utf8char['199 186'] = 'Ǻ';
utf8char['199 187'] = 'ǻ';
utf8char['199 188'] = 'Ǽ';
utf8char['199 189'] = 'ǽ';
utf8char['199 190'] = 'Ǿ';
utf8char['199 191'] = 'ǿ';
utf8char['200 128'] = 'Ȁ';
utf8char['200 129'] = 'ȁ';
utf8char['200 130'] = 'Ȃ';
utf8char['200 131'] = 'ȃ';
utf8char['200 132'] = 'Ȅ';
utf8char['200 133'] = 'ȅ';
utf8char['200 134'] = 'Ȇ';
utf8char['200 135'] = 'ȇ';
utf8char['200 136'] = 'Ȉ';
utf8char['200 137'] = 'ȉ';
utf8char['200 138'] = 'Ȋ';
utf8char['200 139'] = 'ȋ';
utf8char['200 140'] = 'Ȍ';
utf8char['200 141'] = 'ȍ';
utf8char['200 142'] = 'Ȏ';
utf8char['200 143'] = 'ȏ';
utf8char['200 144'] = 'Ȑ';
utf8char['200 145'] = 'ȑ';
utf8char['200 146'] = 'Ȓ';
utf8char['200 147'] = 'ȓ';
utf8char['200 148'] = 'Ȕ';
utf8char['200 149'] = 'ȕ';
utf8char['200 150'] = 'Ȗ';
utf8char['200 151'] = 'ȗ';
utf8char['200 152'] = 'Ș';
utf8char['200 153'] = 'ș';
utf8char['200 154'] = 'Ț';
utf8char['200 155'] = 'ț';
utf8char['200 156'] = 'Ȝ';
utf8char['200 157'] = 'ȝ';
utf8char['200 158'] = 'Ȟ';
utf8char['200 159'] = 'ȟ';
utf8char['200 160'] = 'Ƞ';
utf8char['200 161'] = 'ȡ';
utf8char['200 162'] = 'Ȣ';
utf8char['200 163'] = 'ȣ';
utf8char['200 164'] = 'Ȥ';
utf8char['200 165'] = 'ȥ';
utf8char['200 166'] = 'Ȧ';
utf8char['200 167'] = 'ȧ';
utf8char['200 168'] = 'Ȩ';
utf8char['200 169'] = 'ȩ';
utf8char['200 170'] = 'Ȫ';
utf8char['200 171'] = 'ȫ';
utf8char['200 172'] = 'Ȭ';
utf8char['200 173'] = 'ȭ';
utf8char['200 174'] = 'Ȯ';
utf8char['200 175'] = 'ȯ';
utf8char['200 176'] = 'Ȱ';
utf8char['200 177'] = 'ȱ';
utf8char['200 178'] = 'Ȳ';
utf8char['200 179'] = 'ȳ';
utf8char['200 180'] = 'ȴ';
utf8char['200 181'] = 'ȵ';
utf8char['200 182'] = 'ȶ';
utf8char['200 183'] = 'ȷ';
utf8char['200 184'] = 'ȸ';
utf8char['200 185'] = 'ȹ';
utf8char['200 186'] = 'Ⱥ';
utf8char['200 187'] = 'Ȼ';
utf8char['200 188'] = 'ȼ';
utf8char['200 189'] = 'Ƚ';
utf8char['200 190'] = 'Ⱦ';
utf8char['200 191'] = 'ȿ';
utf8char['201 128'] = 'ɀ';
utf8char['201 129'] = 'Ɂ';
utf8char['201 130'] = 'ɂ';
utf8char['201 131'] = 'Ƀ';
utf8char['201 132'] = 'Ʉ';
utf8char['201 133'] = 'Ʌ';
utf8char['201 134'] = 'Ɇ';
utf8char['201 135'] = 'ɇ';
utf8char['201 136'] = 'Ɉ';
utf8char['201 137'] = 'ɉ';
utf8char['201 138'] = 'Ɋ';
utf8char['201 139'] = 'ɋ';
utf8char['201 140'] = 'Ɍ';
utf8char['201 141'] = 'ɍ';
utf8char['201 142'] = 'Ɏ';
utf8char['201 143'] = 'ɏ';
utf8char['201 144'] = 'ɐ';
utf8char['201 145'] = 'ɑ';
utf8char['201 146'] = 'ɒ';
utf8char['201 147'] = 'ɓ';
utf8char['201 148'] = 'ɔ';
utf8char['201 149'] = 'ɕ';
utf8char['201 150'] = 'ɖ';
utf8char['201 151'] = 'ɗ';
utf8char['201 152'] = 'ɘ';
utf8char['201 153'] = 'ə';
utf8char['201 154'] = 'ɚ';
utf8char['201 155'] = 'ɛ';
utf8char['201 156'] = 'ɜ';
utf8char['201 157'] = 'ɝ';
utf8char['201 158'] = 'ɞ';
utf8char['201 159'] = 'ɟ';
utf8char['201 160'] = 'ɠ';
utf8char['201 161'] = 'ɡ';
utf8char['201 162'] = 'ɢ';
utf8char['201 163'] = 'ɣ';
utf8char['201 164'] = 'ɤ';
utf8char['201 165'] = 'ɥ';
utf8char['201 166'] = 'ɦ';
utf8char['201 167'] = 'ɧ';
utf8char['201 168'] = 'ɨ';
utf8char['201 169'] = 'ɩ';
utf8char['201 170'] = 'ɪ';
utf8char['201 171'] = 'ɫ';
utf8char['201 172'] = 'ɬ';
utf8char['201 173'] = 'ɭ';
utf8char['201 174'] = 'ɮ';
utf8char['201 175'] = 'ɯ';
utf8char['201 176'] = 'ɰ';
utf8char['201 177'] = 'ɱ';
utf8char['201 178'] = 'ɲ';
utf8char['201 179'] = 'ɳ';
utf8char['201 180'] = 'ɴ';
utf8char['201 181'] = 'ɵ';
utf8char['201 182'] = 'ɶ';
utf8char['201 183'] = 'ɷ';
utf8char['201 184'] = 'ɸ';
utf8char['201 185'] = 'ɹ';
utf8char['201 186'] = 'ɺ';
utf8char['201 187'] = 'ɻ';
utf8char['201 188'] = 'ɼ';
utf8char['201 189'] = 'ɽ';
utf8char['201 190'] = 'ɾ';
utf8char['201 191'] = 'ɿ';
utf8char['202 128'] = 'ʀ';
utf8char['202 129'] = 'ʁ';
utf8char['202 130'] = 'ʂ';
utf8char['202 131'] = 'ʃ';
utf8char['202 132'] = 'ʄ';
utf8char['202 133'] = 'ʅ';
utf8char['202 134'] = 'ʆ';
utf8char['202 135'] = 'ʇ';
utf8char['202 136'] = 'ʈ';
utf8char['202 137'] = 'ʉ';
utf8char['202 138'] = 'ʊ';
utf8char['202 139'] = 'ʋ';
utf8char['202 140'] = 'ʌ';
utf8char['202 141'] = 'ʍ';
utf8char['202 142'] = 'ʎ';
utf8char['202 143'] = 'ʏ';
utf8char['202 144'] = 'ʐ';
utf8char['202 145'] = 'ʑ';
utf8char['202 146'] = 'ʒ';
utf8char['202 147'] = 'ʓ';
utf8char['202 148'] = 'ʔ';
utf8char['202 149'] = 'ʕ';
utf8char['202 150'] = 'ʖ';
utf8char['202 151'] = 'ʗ';
utf8char['202 152'] = 'ʘ';
utf8char['202 153'] = 'ʙ';
utf8char['202 154'] = 'ʚ';
utf8char['202 155'] = 'ʛ';
utf8char['202 156'] = 'ʜ';
utf8char['202 157'] = 'ʝ';
utf8char['202 158'] = 'ʞ';
utf8char['202 159'] = 'ʟ';
utf8char['202 160'] = 'ʠ';
utf8char['202 161'] = 'ʡ';
utf8char['202 162'] = 'ʢ';
utf8char['202 163'] = 'ʣ';
utf8char['202 164'] = 'ʤ';
utf8char['202 165'] = 'ʥ';
utf8char['202 166'] = 'ʦ';
utf8char['202 167'] = 'ʧ';
utf8char['202 168'] = 'ʨ';
utf8char['202 169'] = 'ʩ';
utf8char['202 170'] = 'ʪ';
utf8char['202 171'] = 'ʫ';
utf8char['202 172'] = 'ʬ';
utf8char['202 173'] = 'ʭ';
utf8char['202 174'] = 'ʮ';
utf8char['202 175'] = 'ʯ';
utf8char['202 176'] = 'ʰ';
utf8char['202 177'] = 'ʱ';
utf8char['202 178'] = 'ʲ';
utf8char['202 179'] = 'ʳ';
utf8char['202 180'] = 'ʴ';
utf8char['202 181'] = 'ʵ';
utf8char['202 182'] = 'ʶ';
utf8char['202 183'] = 'ʷ';
utf8char['202 184'] = 'ʸ';
utf8char['202 185'] = 'ʹ';
utf8char['202 186'] = 'ʺ';
utf8char['202 187'] = 'ʻ';
utf8char['202 188'] = 'ʼ';
utf8char['202 189'] = 'ʽ';
utf8char['202 190'] = 'ʾ';
utf8char['202 191'] = 'ʿ';
utf8char['203 128'] = 'ˀ';
utf8char['203 129'] = 'ˁ';
utf8char['203 130'] = '˂';
utf8char['203 131'] = '˃';
utf8char['203 132'] = '˄';
utf8char['203 133'] = '˅';
utf8char['203 134'] = 'ˆ';
utf8char['203 135'] = 'ˇ';
utf8char['225 184 128'] = 'Ḁ';
utf8char['225 184 129'] = 'ḁ';
utf8char['225 184 130'] = 'Ḃ';
utf8char['225 184 131'] = 'ḃ';
utf8char['225 184 132'] = 'Ḅ';
utf8char['225 184 133'] = 'ḅ';
utf8char['225 184 134'] = 'Ḇ';
utf8char['225 184 135'] = 'ḇ';
utf8char['225 184 136'] = 'Ḉ';
utf8char['225 184 137'] = 'ḉ';
utf8char['225 184 138'] = 'Ḋ';
utf8char['225 184 139'] = 'ḋ';
utf8char['225 184 140'] = 'Ḍ';
utf8char['225 184 141'] = 'ḍ';
utf8char['225 184 142'] = 'Ḏ';
utf8char['225 184 143'] = 'ḏ';
utf8char['225 184 144'] = 'Ḑ';
utf8char['225 184 145'] = 'ḑ';
utf8char['225 184 146'] = 'Ḓ';
utf8char['225 184 147'] = 'ḓ';
utf8char['225 184 148'] = 'Ḕ';
utf8char['225 184 149'] = 'ḕ';
utf8char['225 184 150'] = 'Ḗ';
utf8char['225 184 151'] = 'ḗ';
utf8char['225 184 152'] = 'Ḙ';
utf8char['225 184 153'] = 'ḙ';
utf8char['225 184 154'] = 'Ḛ';
utf8char['225 184 155'] = 'ḛ';
utf8char['225 184 156'] = 'Ḝ';
utf8char['225 184 157'] = 'ḝ';
utf8char['225 184 158'] = 'Ḟ';
utf8char['225 184 159'] = 'ḟ';
utf8char['225 184 160'] = 'Ḡ';
utf8char['225 184 161'] = 'ḡ';
utf8char['225 184 162'] = 'Ḣ';
utf8char['225 184 163'] = 'ḣ';
utf8char['225 184 164'] = 'Ḥ';
utf8char['225 184 165'] = 'ḥ';
utf8char['225 184 166'] = 'Ḧ';
utf8char['225 184 167'] = 'ḧ';
utf8char['225 184 168'] = 'Ḩ';
utf8char['225 184 169'] = 'ḩ';
utf8char['225 184 170'] = 'Ḫ';
utf8char['225 184 171'] = 'ḫ';
utf8char['225 184 172'] = 'Ḭ';
utf8char['225 184 173'] = 'ḭ';
utf8char['225 184 174'] = 'Ḯ';
utf8char['225 184 175'] = 'ḯ';
utf8char['225 184 176'] = 'Ḱ';
utf8char['225 184 177'] = 'ḱ';
utf8char['225 184 178'] = 'Ḳ';
utf8char['225 184 179'] = 'ḳ';
utf8char['225 184 180'] = 'Ḵ';
utf8char['225 184 181'] = 'ḵ';
utf8char['225 184 182'] = 'Ḷ';
utf8char['225 184 183'] = 'ḷ';
utf8char['225 184 184'] = 'Ḹ';
utf8char['225 184 185'] = 'ḹ';
utf8char['225 184 186'] = 'Ḻ';
utf8char['225 184 187'] = 'ḻ';
utf8char['225 184 188'] = 'Ḽ';
utf8char['225 184 189'] = 'ḽ';
utf8char['225 184 190'] = 'Ḿ';
utf8char['225 184 191'] = 'ḿ';
utf8char['225 185 128'] = 'Ṁ';
utf8char['225 185 129'] = 'ṁ';
utf8char['225 185 130'] = 'Ṃ';
utf8char['225 185 131'] = 'ṃ';
utf8char['225 185 132'] = 'Ṅ';
utf8char['225 185 133'] = 'ṅ';
utf8char['225 185 134'] = 'Ṇ';
utf8char['225 185 135'] = 'ṇ';
utf8char['225 185 136'] = 'Ṉ';
utf8char['225 185 137'] = 'ṉ';
utf8char['225 185 138'] = 'Ṋ';
utf8char['225 185 139'] = 'ṋ';
utf8char['225 185 140'] = 'Ṍ';
utf8char['225 185 141'] = 'ṍ';
utf8char['225 185 142'] = 'Ṏ';
utf8char['225 185 143'] = 'ṏ';
utf8char['225 185 144'] = 'Ṑ';
utf8char['225 185 145'] = 'ṑ';
utf8char['225 185 146'] = 'Ṓ';
utf8char['225 185 147'] = 'ṓ';
utf8char['225 185 148'] = 'Ṕ';
utf8char['225 185 149'] = 'ṕ';
utf8char['225 185 150'] = 'Ṗ';
utf8char['225 185 151'] = 'ṗ';
utf8char['225 185 152'] = 'Ṙ';
utf8char['225 185 153'] = 'ṙ';
utf8char['225 185 154'] = 'Ṛ';
utf8char['225 185 155'] = 'ṛ';
utf8char['225 185 156'] = 'Ṝ';
utf8char['225 185 157'] = 'ṝ';
utf8char['225 185 158'] = 'Ṟ';
utf8char['225 185 159'] = 'ṟ';
utf8char['225 185 160'] = 'Ṡ';
utf8char['225 185 161'] = 'ṡ';
utf8char['225 185 162'] = 'Ṣ';
utf8char['225 185 163'] = 'ṣ';
utf8char['225 185 164'] = 'Ṥ';
utf8char['225 185 165'] = 'ṥ';
utf8char['225 185 166'] = 'Ṧ';
utf8char['225 185 167'] = 'ṧ';
utf8char['225 185 168'] = 'Ṩ';
utf8char['225 185 169'] = 'ṩ';
utf8char['225 185 170'] = 'Ṫ';
utf8char['225 185 171'] = 'ṫ';
utf8char['225 185 172'] = 'Ṭ';
utf8char['225 185 173'] = 'ṭ';
utf8char['225 185 174'] = 'Ṯ';
utf8char['225 185 175'] = 'ṯ';
utf8char['225 185 176'] = 'Ṱ';
utf8char['225 185 177'] = 'ṱ';
utf8char['225 185 178'] = 'Ṳ';
utf8char['225 185 179'] = 'ṳ';
utf8char['225 185 180'] = 'Ṵ';
utf8char['225 185 181'] = 'ṵ';
utf8char['225 185 182'] = 'Ṷ';
utf8char['225 185 183'] = 'ṷ';
utf8char['225 185 184'] = 'Ṹ';
utf8char['225 185 185'] = 'ṹ';
utf8char['225 185 186'] = 'Ṻ';
utf8char['225 185 187'] = 'ṻ';
utf8char['225 185 188'] = 'Ṽ';
utf8char['225 185 189'] = 'ṽ';
utf8char['225 185 190'] = 'Ṿ';
utf8char['225 185 191'] = 'ṿ';
utf8char['225 186 128'] = 'Ẁ';
utf8char['225 186 129'] = 'ẁ';
utf8char['225 186 130'] = 'Ẃ';
utf8char['225 186 131'] = 'ẃ';
utf8char['225 186 132'] = 'Ẅ';
utf8char['225 186 133'] = 'ẅ';
utf8char['225 186 134'] = 'Ẇ';
utf8char['225 186 135'] = 'ẇ';
utf8char['225 186 136'] = 'Ẉ';
utf8char['225 186 137'] = 'ẉ';
utf8char['225 186 138'] = 'Ẋ';
utf8char['225 186 139'] = 'ẋ';
utf8char['225 186 140'] = 'Ẍ';
utf8char['225 186 141'] = 'ẍ';
utf8char['225 186 142'] = 'Ẏ';
utf8char['225 186 143'] = 'ẏ';
utf8char['225 186 144'] = 'Ẑ';
utf8char['225 186 145'] = 'ẑ';
utf8char['225 186 146'] = 'Ẓ';
utf8char['225 186 147'] = 'ẓ';
utf8char['225 186 148'] = 'Ẕ';
utf8char['225 186 149'] = 'ẕ';
utf8char['225 186 150'] = 'ẖ';
utf8char['225 186 151'] = 'ẗ';
utf8char['225 186 152'] = 'ẘ';
utf8char['225 186 153'] = 'ẙ';
utf8char['225 186 154'] = 'ẚ';
utf8char['225 186 155'] = 'ẛ';
utf8char['225 186 156'] = 'ẜ';
utf8char['225 186 157'] = 'ẝ';
utf8char['225 186 158'] = 'ẞ';
utf8char['225 186 159'] = 'ẟ';
utf8char['225 186 160'] = 'Ạ';
utf8char['225 186 161'] = 'ạ';
utf8char['225 186 162'] = 'Ả';
utf8char['225 186 163'] = 'ả';
utf8char['225 186 164'] = 'Ấ';
utf8char['225 186 165'] = 'ấ';
utf8char['225 186 166'] = 'Ầ';
utf8char['225 186 167'] = 'ầ';
utf8char['225 186 168'] = 'Ẩ';
utf8char['225 186 169'] = 'ẩ';
utf8char['225 186 170'] = 'Ẫ';
utf8char['225 186 171'] = 'ẫ';
utf8char['225 186 172'] = 'Ậ';
utf8char['225 186 173'] = 'ậ';
utf8char['225 186 174'] = 'Ắ';
utf8char['225 186 175'] = 'ắ';
utf8char['225 186 176'] = 'Ằ';
utf8char['225 186 177'] = 'ằ';
utf8char['225 186 178'] = 'Ẳ';
utf8char['225 186 179'] = 'ẳ';
utf8char['225 186 180'] = 'Ẵ';
utf8char['225 186 181'] = 'ẵ';
utf8char['225 186 182'] = 'Ặ';
utf8char['225 186 183'] = 'ặ';
utf8char['225 186 184'] = 'Ẹ';
utf8char['225 186 185'] = 'ẹ';
utf8char['225 186 186'] = 'Ẻ';
utf8char['225 186 187'] = 'ẻ';
utf8char['225 186 188'] = 'Ẽ';
utf8char['225 186 189'] = 'ẽ';
utf8char['225 186 190'] = 'Ế';
utf8char['225 186 191'] = 'ế';
utf8char['225 187 128'] = 'Ề';
utf8char['225 187 129'] = 'ề';
utf8char['225 187 130'] = 'Ể';
utf8char['225 187 131'] = 'ể';
utf8char['225 187 132'] = 'Ễ';
utf8char['225 187 133'] = 'ễ';
utf8char['225 187 134'] = 'Ệ';
utf8char['225 187 135'] = 'ệ';
utf8char['225 187 136'] = 'Ỉ';
utf8char['225 187 137'] = 'ỉ';
utf8char['225 187 138'] = 'Ị';
utf8char['225 187 139'] = 'ị';
utf8char['225 187 140'] = 'Ọ';
utf8char['225 187 141'] = 'ọ';
utf8char['225 187 142'] = 'Ỏ';
utf8char['225 187 143'] = 'ỏ';
utf8char['225 187 144'] = 'Ố';
utf8char['225 187 145'] = 'ố';
utf8char['225 187 146'] = 'Ồ';
utf8char['225 187 147'] = 'ồ';
utf8char['225 187 148'] = 'Ổ';
utf8char['225 187 149'] = 'ổ';
utf8char['225 187 150'] = 'Ỗ';
utf8char['225 187 151'] = 'ỗ';
utf8char['225 187 152'] = 'Ộ';
utf8char['225 187 153'] = 'ộ';
utf8char['225 187 154'] = 'Ớ';
utf8char['225 187 155'] = 'ớ';
utf8char['225 187 156'] = 'Ờ';
utf8char['225 187 157'] = 'ờ';
utf8char['225 187 158'] = 'Ở';
utf8char['225 187 159'] = 'ở';
utf8char['225 187 160'] = 'Ỡ';
utf8char['225 187 161'] = 'ỡ';
utf8char['225 187 162'] = 'Ợ';
utf8char['225 187 163'] = 'ợ';
utf8char['225 187 164'] = 'Ụ';
utf8char['225 187 165'] = 'ụ';
utf8char['225 187 166'] = 'Ủ';
utf8char['225 187 167'] = 'ủ';
utf8char['225 187 168'] = 'Ứ';
utf8char['225 187 169'] = 'ứ';
utf8char['225 187 170'] = 'Ừ';
utf8char['225 187 171'] = 'ừ';
utf8char['225 187 172'] = 'Ử';
utf8char['225 187 173'] = 'ử';
utf8char['225 187 174'] = 'Ữ';
utf8char['225 187 175'] = 'ữ';
utf8char['225 187 176'] = 'Ự';
utf8char['225 187 177'] = 'ự';
utf8char['225 187 178'] = 'Ỳ';
utf8char['225 187 179'] = 'ỳ';
utf8char['225 187 180'] = 'Ỵ';
utf8char['225 187 181'] = 'ỵ';
utf8char['225 187 182'] = 'Ỷ';
utf8char['225 187 183'] = 'ỷ';
utf8char['225 187 184'] = 'Ỹ';
utf8char['225 187 185'] = 'ỹ';
utf8char['225 187 186'] = 'Ỻ';
utf8char['225 187 187'] = 'ỻ';
utf8char['225 187 188'] = 'Ỽ';
utf8char['225 187 189'] = 'ỽ';
utf8char['225 187 190'] = 'Ỿ';
utf8char['225 187 191'] = 'ỿ';
