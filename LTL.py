UNTIL_FREE, RELEASE_FREE = "until_free", "release_free"


class LTL(object):
    def __init__(self, text, type):
        self.text = text
        self.type = type

    def __str__(self):
        return self.text

    def to_nnf(self):
        if self.type == UNTIL_FREE:
            pass
        elif self.type == RELEASE_FREE:
            pass
        else:
            self.error()
        pass

    def to_dnf(self):
        pass

    def error(self):
        raise Exception("Invalid type")

