from backend.subeffect.Effect import WordEffect
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
        self.formatter = None
        self.data = None
        self.effect = None

        for key in lrc_effect.keys():
            if 'data' == key:
                self.data = lrc_effect[key]
            if 'formatter' == key:
                self.formatter = AssDialogueTextFormatter(lrc_effect[key])
            if 'effect' in key:
                self.effect = WordEffect(lrc_effect[key])
                # self.effect = AssDialueTextAnimatedTransform(lrc_effect[key]['config'])
        self.lyriceffect_processor = AssDialogueTextProcessor(keyword=self.data,
                                                              formatter=self.formatter,
                                                              animatedconf=self.effect.config)

    def apply_lyric_effect_by_line(self, line, duration):
        return self.lyriceffect_processor.keyword_process(line, duration)

    def apply_lyric_effect_to_file(self, ass_file, output=None):
        if output is None:
            output = ass_file
        subs = SSAFile.load(ass_file, encoding='utf-8')  # create ass file
        for line in subs:
            line.text = self.apply_lyric_effect_by_line(line.text, line.duration)
            print(line.text)
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
