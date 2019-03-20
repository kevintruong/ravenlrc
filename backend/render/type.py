class Size:
    def __init__(self, info: dict):
        self.width = int(info['width'])
        self.height = int(info['height'])


class Position:
    def __init__(self, info: dict):
        self.x = int(info['x'])
        self.y = int(info['y'])


class Font:
    def __init__(self, info: dict):
        self.name = info['name']
        self.color = int(info['color'], 16)
        self.size = int(info['size'])