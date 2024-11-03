"""
Изначально принцип Барбары-Лисков нарушался для класса Square,
потому что он наследовался от родительского класса Rectangle.
И при изменении высоты/ширину у нас не изменялись ширина/высота соответветсвенно.
Что нарушало смысл класса квадрат, у которого стороны должны быть равны.
"""

"""Чтобы решить эту проблему в классе Square были объялвены свойства height и width
с помощью методов-сеттеров. В каждом из них при изменении одной величины меняется также и вторая."""
class Shape:
    """Базовый класс для фигур с координатами x и y"""
    def __init__(self, x=0, y=0):
        self._x = x
        self._y = y
class Rectangle(Shape):
    """"Класс-прямоугольник"""
    def __init__(self, width, height, x=0, y=0):
        """вызывает конструктор родительского класса Shape, передавая координаты x и y"""
        super().__init__(x, y)
        self._width = width
        self._height = height

    @property
    def width(self):
        return self._width #возвращаем width

    @width.setter
    def width(self, value):
        self._width = value #позволяет изменять значение свойства width

    @property
    def height(self):
        return self._height #возвращаем height

    @height.setter
    def height(self, value):
        self._height = value #позволяет изменять значение свойства height

class Square(Rectangle):
    """Класс-квадрат"""
    def __init__(self, side, x=0, y=0):
        """вызывает конструктор родительского класса Rectangle, передавая значения side для width и height."""
        super().__init__(side, side, x, y)

    @property
    def width(self):
        return self._width  # возвращаем width

    @width.setter
    def width(self, value):
        self._width = value
        self._height = value  # устанавливаем одинаковые значения для width и height квадрата

    @property
    def height(self):
        return self._height  # возвращаем высоту квадрата

    @height.setter
    def height(self, value):
        self._height = value
        self._width = value  # устанавливаем одинаковые значения для width и height квадрата


rect = Rectangle(10, 5)
print(rect.width, rect.height) # Вывод: 10 5

square = Square(5)
print(square.width, square.height) # Вывод: 5 5

square.width=10
print(square.width, square.height) # Вывод: 10 10

square.height += 10
print(square.width, square.height) # Вывод: 20 20