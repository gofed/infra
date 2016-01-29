class ProjectID(object):

    @classmethod
    def get(cls, name, commit):
        return '{}-{}'.format(name.replace('.', '-').replace('/', '-'), commit)
