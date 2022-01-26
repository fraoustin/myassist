from flask import Blueprint

class Node(Blueprint):

    def __init__(self, name="", path="", import_name=__name__, *args, **kwargs):
        if len(name) == 0:
            self._nodename = self.__class__.__name__.lower()
        else:
            self._nodename = name
        Blueprint.__init__(self, self._nodename, import_name=__name__, *args, **kwargs)

    def register(self, app, options):
        try:
            Blueprint.register(self, app, options)
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self._nodename, 'files')
            app.register_blueprint(Static(name="%sstatic" % self._nodename, url_prefix="/%s/" % self._nodename, path=path))
        except Exception:
            app.logger.error("init node %s on register is failed" % self._nodename)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
