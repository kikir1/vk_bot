import inspect


class BaseType:
    def __init__(self, name=None):
        self.name = name

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


class PageElementType(BaseType):
    def __set__(self, instance, value):
        from .elements import PageElement

        if not isinstance(value, PageElement):
            raise TypeError("Expected PageElement")
        super().__set__(instance, value)


class PageElementsType(BaseType):
    def __set__(self, instance, value):
        from .elements import PageElements

        if not isinstance(value, PageElements):
            raise TypeError("Expected PageElements")
        super().__set__(instance, value)


class RegionClassType(BaseType):
    def __set__(self, instance, value):
        from .page import Region

        if not inspect.isclass(value):
            raise TypeError("Expected Region class.")
        if not issubclass(value, Region):
            raise TypeError("Expect region")
        super().__set__(instance, value)


class checkedmeta(type):
    def __new__(mcs, clsname, bases, methods):
        for key, value in methods.items():
            if isinstance(value, BaseType):
                value.name = key
        return type.__new__(mcs, clsname, bases, methods)
