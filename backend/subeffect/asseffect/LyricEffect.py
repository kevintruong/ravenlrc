from backend.subeffect.keyword.keyword import AssDialogueTextKeyWordFormatter


class KeyWordInfo:
    def __init__(self, keywordinfo: dict):
        for key in keywordinfo.keys():
            if 'keywords' in key:
                self.keywords = keywordinfo['keywords']
            if 'keyword_fmt' in key:
                self.keyword_fmt = AssDialogueTextKeyWordFormatter(keywordinfo['keyword_fmt'])


class EffectInfo:
    def __init__(self, effectinfo: dict):

        pass


class LyricEffect:
    def __init__(self, lrc_effect: dict):
        for key in lrc_effect.keys():
            if 'keyword_info' in key:
                self.keywordinfo = KeyWordInfo(lrc_effect['keyword_info'])
            if 'effect_info' in key:
                self.effect_info = None
        pass
