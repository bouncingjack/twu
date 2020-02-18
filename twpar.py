"""
This module houses an implementation of a Singleton :class:`TimeWatchParametersSingleton`
for parameters access.
Also a subclass :class:`TimeWatchParameters` that is used for the access.
"""

import json


class TimeWatchParametersSingleton(object):
    """
    Singleton & Context manager implementation for parameters access.
    Instantiation is emtpy.
    parameters are added later via a call to `with` statement:
    """
    _instance = None
    file_path = None
    parameters = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        if not cls._instance.__getattr__('file_path'):
            try:
                cls._instance.file_path = args[0]
                with open(cls._instance.file_path) as f:
                    cls._instance.parameters = json.loads(f.read()) 
            except IndexError:
                pass
        return cls._instance

    def __getattr__(self, name):
        return getattr(self._instance, name)


class TimeWatchParameters(TimeWatchParametersSingleton):
    """
    Inherited Singleton - actual parameters access class
    """
    pass


class TWParams:
    
    file_path = None

    def __init__(self, file_path):
        self.file_path = file_path

    def __enter__(self):
        with open(self.file_path) as f:
            self.parameters = json.loads(f.read())
        return self

    def __exit__(self, *exception):
        pass