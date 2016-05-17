"""
Decorator for automatically setting args and kwargs to a function as attributes.

From https://stackoverflow.com/questions/1389180/python-automatically-initialize-instance-variables/1389216#1389216 and
https://gist.github.com/pmav99/137dbf4681be9a58de74

E.g.:

class Foo(object):
    @initializer
    def __init__(self, a, b, c=None, d=None, e=3):
        pass

f = Foo(1, 2, d="a")
assert f.a == 1
assert f.b == 2
assert f.c is None
assert f.d == "a"
assert f.e == 3



"""
from functools import wraps
import inspect


# Python3 compatible code (it runs fine under python2 too).
def initializer(fun):
    names, varargs, keywords, defaults = inspect.getargspec(fun)

    @wraps(fun)
    def wrapper(self, *args, **kargs):
        for name, arg in list(zip(names[1:], args)) + list(kargs.items()):
            setattr(self, name, arg)
        for i in range(len(defaults)):
            index = -(i + 1)
            if not hasattr(self, names[index]):
                setattr(self, names[index], defaults[index])
        fun(self, *args, **kargs)
    return wrapper
