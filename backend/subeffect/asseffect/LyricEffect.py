from backend.subeffect.keyword.keyword import *
from backend.subeffect.pysubs2 import SSAFile


class KeyWordInfo:
    def __init__(self, keywordinfo: dict):
        self.keywords = None
        self.keyword_fmt = None
        for key in keywordinfo.keys():
            if 'keywords' in key:
                self.keywords = keywordinfo['keywords']
            if 'keyword_fmt' in key:
                self.keyword_fmt = keywordinfo['keyword_fmt']

    def get_keyword(self):
        return self.keywords

    def get_keyword_formatter(self):
        return self.keyword_fmt


class EffectInfo:
    def __init__(self, type_effect: int, effectinfo: dict):
        if type_effect == 1:
            self.effect_info = AssDialueTextAnimatedTransform.json2dict(effectinfo)
        pass


class LyricEffect:
    def __init__(self, lrc_effect: dict):
        self.keywordinfo = None
        self.effect_info = None
        for key in lrc_effect.keys():
            if 'keyword_info' in key:
                self.keywordinfo = KeyWordInfo(lrc_effect['keyword_info'])
            if 'effect_info' in key:
                effect_type = lrc_effect['effect_type']
                self.effect_info = EffectInfo(effect_type,
                                              lrc_effect['effect_info']).effect_info
        self.lyriceffect_processor = AssDialogueTextProcessor(keyword=self.keywordinfo.keywords,
                                                              formatter=self.keywordinfo.keyword_fmt,
                                                              animatedconf=self.effect_info)

    def apply_lyric_effect_by_line(self, line, duration):
        return self.lyriceffect_processor.keyword_process(line, duration)

    def apply_lyric_effect_to_file(self, ass_file, output=None):
        if output is None:
            output = ass_file
        subs = SSAFile.load(ass_file, encoding='utf-8')  # create ass file
        for line in subs:
            line.text = self.apply_lyric_effect_by_line(line.text, line.duration)
        subs.save(output)
        return output

    def apply_lyric_effect_to_asscontent(self, asscontent: SSAFile, output):
        subs = asscontent
        for line in subs:
            line.text = self.apply_lyric_effect_by_line(line.text,
                                                        line.duration)
        subs.save(output)


class TransformEffectProfile:
    pass
