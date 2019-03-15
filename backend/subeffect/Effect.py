import abc

from backend.subeffect.keyword.keyword import AssDialueTextAnimatedTransform
from backend.utility.Utility import PyJSON


class Effect:

    @staticmethod
    def generate_effect_executor(cls, effect_code):
        pass

    @abc.abstractmethod
    def execute_effect(self, lyric: str):
        pass

    def __init__(self, info: dict):
        self.type = info['type']
        self.code = info['code']
        pass


class SongEffect(Effect):

    def execute_effect(self, lyric: str):
        print("SongEffect execute effect")
        pass

    def __init__(self, info: dict):
        super().__init__(info)


class WordEffect(PyJSON):
    def __init__(self, d):
        """
        :self.code str
        :self.type str
        :param d:
        """
        super().__init__(d)
        # for keyvalue in effect.keys():
        #     if keyvalue == 'type':
        #         self.type = effect[keyvalue]
        #     if keyvalue == 'code':
        #         self.code = effect[keyvalue]
        #     if keyvalue == 'start':
        #         pass
        if 'config' in d:
            self.config = AssDialueTextAnimatedTransform(d['config'])


class SentenceEffect(Effect):

    def __init__(self, info: dict):
        super().__init__(info)
