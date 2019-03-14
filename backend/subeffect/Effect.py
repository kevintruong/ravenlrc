import abc


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


class WordEffect(Effect):

    def execute_effect(self, lyric: str):
        pass

    def __init__(self, info: dict):
        super().__init__(info)


class SentenceEffect(Effect):

    def __init__(self, info: dict):
        super().__init__(info)
