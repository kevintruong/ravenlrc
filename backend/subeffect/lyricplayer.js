if ("undefined" === typeof lt)
    var lt = {};
lt.Lyrics = function() {
    this.yt_video_id = this.level = this.lang = this.genre = this.album = this.artist = this.title = null;
    this.offset = this.duration = this.end = this.start = 0;
    this.lines = []
}
;
lt.Lyrics.WORD_SEPARATORS = ' ,.:;()[]{}\u00bf?\u00a1!"\\//\u2026';
lt.Lyrics.BREAK_CHARS = ["(", ")"];
lt.Lyrics.parseTime = function(a) {
    var b = null;
    if (0 < (a = $.trim(a)).length) {
        var c = /(\d{1,2}):(\d{1,2})(\.(\d{1,2}))?/.exec(a);
        c ? (b = 6E4 * parseInt(c[1], 10) + parseInt(1E3 * c[2], 10),
        3 < c.length && void 0 !== c[4] && (b += 10 * parseInt(c[4], 10))) : (a = parseInt(1E3 * parseFloat(a), 10),
        isNaN(a) || (b = a))
    }
    return b
}
;
lt.Lyrics.formatTime = function(a, b) {
    if (b) {
        var c = Math.abs(parseInt(a / 1E3, 10))
          , d = Math.abs(parseInt(a % 1E3 / 10, 10));
        return (0 > a ? "-" : "+") + c + "." + (10 > d ? "0" + d : d) + "s"
    }
    0 > a && (a = 0);
    var e = parseInt(a / 6E4, 10)
      , c = parseInt(a % 6E4 / 1E3, 10)
      , d = parseInt(a % 6E4 % 1E3 / 10, 10);
    return (10 > e ? "0" + e : e) + ":" + (10 > c ? "0" + c : c) + "." + (10 > d ? "0" + d : d)
}
;
lt.Lyrics.isAlpha = function(a) {
    return -1 !== LATIN_ALPHABET_EX.indexOf(a)
}
;
lt.Lyrics.isAlphaNum = function(a) {
    return -1 !== LATIN_ALPHABET_EX.indexOf(a) || -1 !== DIGITS.indexOf(a)
}
;
lt.Lyrics.isSeparator = function(a) {
    return -1 !== lt.Lyrics.WORD_SEPARATORS.indexOf(a)
}
;
lt.Lyrics.normalizeChar = function(a) {
    var b = NORMALIZE_CHARSET[0].indexOf(a);
    return -1 !== b ? NORMALIZE_CHARSET[1][b] : a
}
;
lt.Lyrics.normalize = function(a) {
    for (var b = "", c = 0, d, e; c < a.length; c++)
        e = a.charAt(c),
        d = NORMALIZE_CHARSET[0].indexOf(e),
        b += -1 !== d ? NORMALIZE_CHARSET[1][d] : e;
    return b
}
;
lt.Lyrics.prototype.append = function(a) {
    this.lines.push(a)
}
;
lt.Lyrics.prototype.insert = function(a) {
    if (void 0 === a.time || 0 === this.lines.length)
        this.lines.push(a);
    else {
        for (var b = 0, c = 0; c < this.lines.length; c++)
            if (void 0 !== this.lines[c].time) {
                if (a.time < this.lines[c].time)
                    break;
                b++
            }
        this.lines.splice(b, 0, a)
    }
}
;
lt.Lyrics.prototype.clear = function() {
    this.lines = []
}
;
lt.Lyrics.prototype.getLineTime = function(a) {
    return 0 <= a && a < this.lines.length && null != this.lines[a].time ? this.lines[a].time + this.offset : null
}
;
lt.Lyrics.prototype.getLineEndTime = function(a) {
    if (0 <= a && a < this.lines.length)
        for (a += 1; a < this.lines.length; a++)
            if (null != this.lines[a].time)
                return this.lines[a].time + this.offset;
    return null
}
;
lt.Lyrics.prototype.findLineByTime = function(a) {
    a -= this.offset;
    for (var b = -1, c = 0; c < this.lines.length; c++)
        if (null != this.lines[c].time) {
            if (this.lines[c].time > a)
                break;
            b = c
        }
    return b
}
;
lt.Lyrics.prototype.findLineProgress = function(a, b) {
    a -= this.offset;
    for (var c = -1, d = 0, e = -1, f = 0; f < this.lines.length; f++)
        if (void 0 !== this.lines[f].time) {
            if (this.lines[f].time > a) {
                e = this.lines[f].time - d;
                break
            }
            c = f;
            d = this.lines[f].time
        }
    if (-1 === c && -1 === e)
        return null;
    c = {
        line: c
    };
    -1 === e && (void 0 === b && (b = this.duration),
    null != this.end && 0 < this.end && (null == b || 0 === b || b > this.end) && (b = this.end),
    null != b && 0 < b && (e = b - (d + this.offset)));
    c.progress = -1 !== e ? (a - d) / e : -1;
    return c
}
;
lt.Lyrics.prototype.allWords = function(a) {
    return (new lt.Lyrics.GapIndex(this)).readWords()
}
;
lt.Lyrics.prototype.randomWords = function(a) {
    var b = new lt.Lyrics.GapIndex(this);
    if (0 < a) {
        var c = new lt.Lyrics.GapIndex(this), d = new lt.Lyrics.GapIndex(this), e;
        c.readWords();
        for (1 > a && (a = Math.round(c.size * a)); 0 < a; )
            0 === c.size && (e = c,
            c = d,
            d = e),
            e = c.random(!0),
            b.add(e),
            c.removeLine(e.line, d),
            c.removeText(e.text, !0, d),
            a--
    }
    return b
}
;
lt.Lyrics.prototype.countWords = function(a) {
    a = 0;
    for (var b = new lt.Lyrics.Reader(this); null !== b.nextWord(); )
        a++;
    return a
}
;
lt.Lyrics.Line = function(a, b) {
    this.time = a;
    this.text = b
}
;
lt.Lyrics.Reader = function(a, b) {
    this.lyrics = a;
    this.ci = this.li = 0;
    this.wi = -1;
    this.wc = 0;
    this.start = this.line = -1;
    this.gaps = this.text = null;
    null != b && (this.gaps = b.cursor(),
    this.gaps.next());
    this.breakOpen = !1
}
;
lt.Lyrics.Reader.END = 1;
lt.Lyrics.Reader.WORD = 2;
lt.Lyrics.Reader.TEXT = 3;
lt.Lyrics.Reader.EOL = 4;
lt.Lyrics.Reader.BREAK_OPEN = 5;
lt.Lyrics.Reader.BREAK_CLOSE = 6;
lt.Lyrics.Reader.GAP = 7;
lt.Lyrics.Reader.prototype.reset = function() {
    this.ci = this.li = 0;
    this.wi = -1;
    this.wc = 0;
    this.start = this.line = -1;
    this.text = null;
    this.breakOpen = !1;
    void 0 !== this.gaps && (this.gaps.reset(),
    this.gaps.next())
}
;
lt.Lyrics.Reader.prototype.next = function() {
    this.line = this.li;
    this.start = this.ci;
    this.text = "";
    if (this.li < this.lyrics.lines.length) {
        var a = this.lyrics.lines[this.li].text;
        if (this.ci < a.length) {
            var b = 0, c = 0, d;
            do {
                d = a.charAt(this.ci);
                if (this.breakOpen)
                    if (d === lt.Lyrics.BREAK_CHARS[1])
                        if (0 === b)
                            b = lt.Lyrics.Reader.BREAK_CLOSE,
                            this.breakOpen = !1;
                        else
                            break;
                    else
                        null != this.gaps && this.gaps.line === this.li && this.gaps.start === this.ci && (console.log("WARN: Gap inside a comment block. (" + this.gaps.text + ")"),
                        this.gaps.next()),
                        b = lt.Lyrics.Reader.TEXT;
                else if (d === lt.Lyrics.BREAK_CHARS[0])
                    if (0 === b)
                        b = lt.Lyrics.Reader.BREAK_OPEN,
                        this.breakOpen = !0;
                    else
                        break;
                else if (null != this.gaps) {
                    if (this.gaps.line === this.li && this.gaps.start === this.ci) {
                        var e = a.substr(this.ci, this.gaps.text.length);
                        if (this.gaps.text === e) {
                            if (0 === b)
                                return this.text = this.gaps.text,
                                this.ci += this.gaps.text.length,
                                this.gaps.next(),
                                lt.Lyrics.Reader.GAP;
                            break
                        } else
                            console.log("WARN: Gap text doesn't match (\"" + e + '" \x3c\x3e "' + this.gaps.text + '").'),
                            this.gaps.next()
                    }
                    b = lt.Lyrics.Reader.TEXT
                } else if (lt.Lyrics.isSeparator(d))
                    if (0 === b)
                        b = lt.Lyrics.Reader.TEXT;
                    else {
                        if (b != lt.Lyrics.Reader.TEXT)
                            break
                    }
                else if (lt.Lyrics.isAlphaNum(d) && c++,
                0 === b)
                    b = lt.Lyrics.Reader.WORD;
                else if (b != lt.Lyrics.Reader.WORD)
                    break;
                this.text += d;
                this.ci++;
                if (b === lt.Lyrics.Reader.BREAK_OPEN || b === lt.Lyrics.Reader.BREAK_CLOSE)
                    return b
            } while (this.ci < a.length);b === lt.Lyrics.Reader.WORD && (0 < c ? (this.wi++,
            this.wc++) : b = lt.Lyrics.Reader.TEXT);
            return b
        }
        this.li++;
        this.ci = this.wi = 0;
        return lt.Lyrics.Reader.EOL
    }
    return lt.Lyrics.Reader.END
}
;
lt.Lyrics.Reader.prototype.nextWord = function() {
    for (var a; (a = this.next()) !== lt.Lyrics.Reader.WORD && a !== lt.Lyrics.Reader.END; )
        ;
    return a === lt.Lyrics.Reader.WORD ? this.text : null
}
;
lt.Lyrics.GapIndex = function(a) {
    this.lyrics = a;
    this.lines = [];
    this.size = 0
}
;
lt.Lyrics.GapIndex.prototype.add = function(a, b, c) {
    var d, e;
    if (3 === arguments.length)
        d = a,
        e = {
            start: b,
            text: c
        };
    else if (2 === arguments.length && "object" === typeof b)
        d = a,
        e = b;
    else if (1 === arguments.length && "object" === typeof a)
        d = a.line,
        e = {
            start: a.start,
            text: a.text
        };
    else
        return;
    var f = this.findLineEntry(d);
    if (null == f)
        for (var f = {
            line: d,
            gaps: []
        }, g = 0; g < this.lines.length + 1; g++)
            if (g === this.lines.length) {
                this.lines.push(f);
                break
            } else if (d < this.lines[g].line) {
                this.lines.splice(g, 0, f);
                break
            }
    for (g = 0; g < f.gaps.length + 1; g++)
        if (g === f.gaps.length) {
            f.gaps.push(e);
            break
        } else if (e.start < f.gaps[g].start) {
            f.gaps.splice(g, 0, e);
            break
        }
    this.size++
}
;
lt.Lyrics.GapIndex.prototype.addLines = function(a) {
    for (var b = 0; b < a.length; b++)
        for (var c = 0; c < a[b].gaps.length; c++)
            this.add(a[b].line, a[b].gaps[c].start, a[b].gaps[c].text)
}
;
lt.Lyrics.GapIndex.prototype.remove = function(a, b) {
    var c = this.findLineEntry(a)
      , d = null;
    if (null != c)
        for (var e = 0; e < c.gaps.length; e++)
            if (c.gaps[e].start == b) {
                d = jQuery.extend({
                    line: c.line
                }, c.gaps[e]);
                c.gaps.splice(e, 1);
                this.size--;
                break
            }
    return d
}
;
lt.Lyrics.GapIndex.prototype.random = function(a) {
    var b = parseInt(Math.random() * this.size, 10), c, d;
    for (d = 0; d < this.lines.length; d++) {
        if (b < this.lines[d].gaps.length) {
            c = this.lines[d];
            break
        }
        b -= this.lines[d].gaps.length
    }
    d = $.extend({
        line: c.line
    }, c.gaps[b]);
    a && (c.gaps.splice(b, 1),
    this.size--);
    return d
}
;
lt.Lyrics.GapIndex.prototype.removeLine = function(a, b) {
    for (var c = null, d = -1, e = 0, f = 0; f < this.lines.length; f++)
        if (this.lines[f].line === a) {
            c = this.lines[d = f];
            break
        }
    null != c && (e = c.gaps.length,
    b instanceof lt.Lyrics.GapIndex && b.addLines([c]),
    this.lines.splice(d, 1),
    this.size -= e);
    return e
}
;
lt.Lyrics.GapIndex.prototype.removeText = function(a, b, c) {
    var d = 0;
    if (0 < this.size)
        for (a = RegExp(a, b ? "i" : ""),
        b = 0; b < this.lines.length; b++)
            for (var e = 0; e < this.lines[b].gaps.length; e++)
                this.lines[b].gaps[e].text.match(a) && (c instanceof lt.Lyrics.GapIndex && c.add(this.lines[b].line, this.lines[b].gaps[e].start, this.lines[b].gaps[e].text),
                this.lines[b].gaps.splice(e, 1),
                this.size--,
                d++);
    return d
}
;
lt.Lyrics.GapIndex.prototype.readWords = function() {
    this.clear();
    for (var a = new lt.Lyrics.Reader(this.lyrics); null != a.nextWord(); )
        this.add(a.line, a.start, a.text);
    return this
}
;
lt.Lyrics.GapIndex.prototype.clear = function() {
    this.lines = [];
    this.size = 0
}
;
lt.Lyrics.GapIndex.prototype.findLineEntry = function(a) {
    for (var b = 0; b < this.lines.length; b++)
        if (this.lines[b].line === a)
            return this.lines[b];
    return null
}
;
lt.Lyrics.GapIndex.prototype.cursor = function() {
    return new lt.Lyrics.GapIndex.Cursor(this)
}
;
lt.Lyrics.GapIndex.prototype.validate = function(a) {
    for (var b = [], c = this.lines.length - 1, d, e, f, g; 0 <= c; c--) {
        d = this.lines[c].line;
        e = 0 <= d && d < this.lyrics.lines.length ? this.lyrics.lines[d].text : null;
        for (var k = this.lines[c].gaps.length - 1; 0 <= k; k--)
            f = this.lines[c].gaps[k].start,
            g = this.lines[c].gaps[k].text,
            null !== e && 0 <= f && f + g.length <= e.length && g === e.substr(f, g.length) || (a && this.lines[c].gaps.splice(k, 1),
            b.unshift({
                line: d,
                start: f,
                text: g
            }));
        a && 0 === this.lines[c].gaps.length && this.lines.splice(c, 1)
    }
    return 0 === b.length ? null : b
}
;
lt.Lyrics.GapIndex.prototype.exportData = function() {
    for (var a = "", b = 0, c; b < this.lines.length; b++) {
        a += this.lines[b].line + ":";
        c = this.lines[b].gaps;
        for (var d = 0, e; d < c.length; d++) {
            e = c[d];
            0 < d && (a += "\t");
            a += e.start + "/";
            a += this.encodeText(e.text);
            if (e.options)
                for (var f = 0; f < e.options.length; f++)
                    a += "|" + this.encodeText(e.options[f]);
            e.hint && (a += "/" + this.encodeText(e.hint))
        }
        a += "\n"
    }
    return a
}
;
lt.Lyrics.GapIndex.prototype.importData = function(a) {
    this.clear();
    for (var b = 0, c = 0, d, e, f, g; b < a.length; )
        if (c = a.indexOf("\n", b),
        -1 === c ? (d = a.substring(b),
        b = a.length) : (d = a.substring(b, c),
        b = c + 1),
        g = /(\d+):(.+)/.exec(d)) {
            c = parseInt(g[1]);
            d = g[2].split("\t");
            for (var k = 0; k < d.length; k++)
                if (g = /(\d+)\/([^\/]+)(?:\/(.+))?/.exec(d[k])) {
                    e = {
                        start: parseInt(g[1])
                    };
                    f = g[2].split("|");
                    e.text = this.decodeText(f[0]);
                    if (1 < f.length)
                        for (e.options = f.slice(1),
                        f = 0; f < e.options.length; f++)
                            e.options[f] = this.decodeText(e.options[f]);
                    3 < g.length && g[3] && (e.hint = this.decodeText(g[3]));
                    this.add(c, e)
                }
        }
    return this
}
;
lt.Lyrics.GapIndex.prototype.encodeText = function(a) {
    var b = {
        "/": "\x26#47;",
        "|": "\x26#124;"
    };
    return a.replace(/[\/\|]/g, function(a) {
        return b[a]
    })
}
;
lt.Lyrics.GapIndex.prototype.decodeText = function(a) {
    var b = {
        "\x26#47;": "/",
        "\x26#124;": "|"
    };
    return a.replace(/(&#47;|&#124;)/g, function(a) {
        return b[a]
    })
}
;
lt.Lyrics.GapIndex.Cursor = function(a) {
    this.li = 0;
    this.gi = -1;
    this.gc = 0;
    this.start = this.line = -1;
    this.text = null;
    this.index = a
}
;
lt.Lyrics.GapIndex.Cursor.prototype.reset = function() {
    this.li = 0;
    this.gi = -1;
    this.gc = 0;
    this.start = this.line = -1;
    this.text = null
}
;
lt.Lyrics.GapIndex.Cursor.prototype.next = function() {
    for (; this.li < this.index.lines.length; ) {
        var a = this.index.lines[this.li];
        if (++this.gi < a.gaps.length)
            return this.line = a.line,
            this.start = a.gaps[this.gi].start,
            this.text = a.gaps[this.gi].text,
            this.gc++,
            !0;
        this.li++;
        this.start = this.line = this.gi = -1;
        this.text = null
    }
    return !1
}
;
lt.Lyrics.LRCParser = {};
lt.Lyrics.LRCParser.LINE_EXP = /\[(.*)\](.*)/;
lt.Lyrics.LRCParser.ATTR_EXP = /(.*):(.*)/;
lt.Lyrics.LRCParser.TIME_EXP = /(\d{1,2}):(\d{1,2})(\.(\d{1,2}))?/;
lt.Lyrics.LRCParser.parse = function(a, b) {
    for (var c = new lt.Lyrics, d = 0, e = 0; d < a.length; ) {
        var f, g = a.indexOf("\n", d);
        -1 === g ? (f = a.substring(d),
        d = a.length) : (f = a.substring(d, g),
        d = g + 1);
        f = $.trim(f);
        if (0 < f.length)
            if (g = lt.Lyrics.LRCParser.LINE_EXP.exec(f)) {
                f = $.trim(g[2]);
                for (var k = $.trim(g[1]).split("]["), l = 0; l < k.length; l++)
                    if (g = lt.Lyrics.LRCParser.TIME_EXP.exec($.trim(k[l]))) {
                        var h = 6E4 * g[1] + 1E3 * g[2];
                        3 < g.length && void 0 !== g[4] && (h += 10 * g[4]);
                        b ? c.insert({
                            time: h,
                            text: f
                        }) : c.append({
                            time: h,
                            text: f
                        })
                    } else if (g = lt.Lyrics.LRCParser.ATTR_EXP.exec($.trim(k[l])))
                        h = g[1],
                        "ti" == h ? h = "title" : "ar" == h ? h = "artist" : "al" == h ? h = "album" : "by" == h && (h = "user"),
                        c[h] = g[2]
            } else
                c.append({
                    text: f
                });
        e++
    }
    return c
}
;
lt.Lyrics.LRCParser.format = function(a) {
    return "[ti:" + a.title + "]\n[ar:" + a.artist + "]\n[al:" + a.album + "]\n[genre:" + a.genre + "]\n[lang:" + a.lang + "]\n[level:" + a.level + "]\n[start:" + a.start + "]\n[end:" + a.end + "]\n[offset:" + a.offset + "]\n[yt_video_id:" + a.yt_video_id + "]\n" + lt.Lyrics.LRCParser.formatLines(a)
}
;
lt.Lyrics.LRCParser.formatLines = function(a) {
    for (var b = "", c = 0; c < a.lines.length; c++)
        b += "[" + lt.Lyrics.formatTime(a.lines[c].time) + "]" + a.lines[c].text + "\n";
    return b
}
;
