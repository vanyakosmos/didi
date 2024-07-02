import abc


class Lazy(abc.ABC):
    @abc.abstractmethod
    def resolve(self):
        pass


class LazyAttr(Lazy):
    def __init__(self, instance, value):
        self._instance = instance
        self._value = value

    def __repr__(self):
        return f"LazyAttr({self._instance!r}, {self._value!r})"

    def resolve(self):
        return getattr(self._instance, self._value)


class Composer:
    def __init__(self):
        pass


class Config:
    def __init__(self):
        self._data = None

    def __set__(self, composer: Composer, value):
        self._data = value

    def __getattr__(self, item: str):
        if self._data:
            return getattr(self._data, item)
        return LazyAttr(self, item)


class Singleton(Lazy):
    REGISTRY = {}

    def __init__(self, maker, **kwargs):
        self._maker = maker
        self._kwargs = kwargs

    def __get__(self, composer: Composer, owner: type[Composer]):
        return self.resolve

    def resolve(self):
        if self._maker not in self.REGISTRY:
            kwargs = {}
            for k, v in self._kwargs.items():
                if isinstance(v, Lazy):
                    v = v.resolve()
                kwargs[k] = v
            self.REGISTRY[self._maker] = self._maker(**kwargs)
        return self.REGISTRY[self._maker]


class Factory(Lazy):
    def __init__(self, maker, **kwargs):
        self._maker = maker
        self._kwargs = kwargs

    def __get__(self, composer: Composer, owner: type[Composer]):
        return self.resolve

    def resolve(self):
        kwargs = {}
        for k, v in self._kwargs.items():
            if isinstance(v, Lazy):
                v = v.resolve()
            kwargs[k] = v
        return self._maker(**kwargs)


class Resource(Lazy):
    REGISTRY = {}

    def __init__(self, generator_maker, **kwargs):
        self._generator_maker = generator_maker
        self._generator = None
        self._kwargs = kwargs

    def __get__(self, composer: Composer, owner: type[Composer]):
        return self.resolve

    def resolve(self):
        if self._generator_maker not in self.REGISTRY:
            kwargs = {}
            for k, v in self._kwargs.items():
                if isinstance(v, Lazy):
                    v = v.resolve()
                kwargs[k] = v
            self._generator = self._generator_maker(**kwargs)
            self.REGISTRY[self._generator_maker] = next(self._generator)
        return self.REGISTRY[self._generator_maker]


def resource(**kwargs):
    def decorator(generator_maker):
        return Resource(generator_maker, **kwargs)

    return decorator
