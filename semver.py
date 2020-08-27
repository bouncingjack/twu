import re


class Version:
    version = {
        'major': 0,
        'minor': 0,
        'patch': 0
    }

    def __init__(self, *args, **kwargs):
        try:
            self._from_string(args[0])
        except IndexError:
            try:
                self._from_string(kwargs['version'])
            except KeyError:
                pass

    def _from_string(self, s):
        match = re.search(pattern=r'(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)',
                          string=s)
        try:
            self.version['major'] = int(match.group('major'))
            self.version['minor'] = int(match.group('minor'))
            self.version['patch'] = int(match.group('patch'))
        except AttributeError:
            raise 'Bad version {}'.format(s)

    def __eq__(self, other):
        ret = []
        for k, v in self.version.items():
            ret.append(v == other.version[k])
        return all(ret)

    def __gt__(self, other):
        if self.version['major'] > other.version['major']:
            return True
        elif self.version['minor'] > other.version['minor']:
                return True
        elif self.version['patch'] > other.version['patch']:
            return True
        else:
            return False
