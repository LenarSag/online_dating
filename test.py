class A:
    counter = 0

    def meth(self):
        return 'metod'


a = A()

print(a.meth() == A.meth(a))


from sqlalchemy.ext.hybrid import hybrid_method


class SomeClass:
    @hybrid_method
    def value(self, x, y):
        return self._value + x + y

    @value.expression
    @classmethod
    def value(cls, x, y):
        return func.some_function(cls._value, x, y)
