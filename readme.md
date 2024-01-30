# MicroPython ST7735R TFT display driver

## WIP

See [test.py](/test.py) for examples

#### special methods

```python
def __init__(self, spi, dc, cs=None, rst=None, w=80, h=160, x=26, y=1, rot=0, inv=True, bgr=True)
```

#### private methods

```python
def _init_rotate(self, r)
def _dc_low(self)
def _dc_high(self)
def _rst_low(self)
def _rst_high(self)
def _cs_low(self)
def _cs_high(self)
def _repeat_data_slow(self, data, count)
def _repeat_data(self, data, count)
def _repeat_data_bulk(self, data, count)
```

#### public methods

```python
def init(self)
def hard_reset(self)
def soft_reset(self)
def rotate(self, r=0)
def cmd(self, command=None, data=None)
def data(self, data)
def sleep(self, sleep=False)
def power(self, on=None)
def invert(self, invert=True)
def set_window(self, x0, y0, x1, y1)
def fill(self, color=COLOR_WHITE)
def fill_slow(self, color=COLOR_WHITE)
def fill_bulk(self, color=COLOR_WHITE)
def color565(self, r, g, b)
def pixel(self, x, y, color)
def rect_outline(self, x, y, w, h, color)
def rect(self, x, y, w, h, color)
def circle(self, x, y, radius, color)
def circle_outline(self, x, y, radius, color)
def triangle_outline(x0, y0, x1, y1, x2, y2, color)
def line(self, x0, y0, x1, y1, color)
def hline(self, x, y, w, color)
def vline(self, x, y, h, color)
def text(self, x, y, string, font, color, size=1, x_wrap=None)
def char(self, x, y, char, font, color, sizex=1, sizey=1)
```

Inspired by various ST7735 implementations and sources:

* https://github.com/hosaka/micropython-st7735
* https://github.com/boochow/MicroPython-ST7735
* https://github.com/AnthonyKNorman/MicroPython_ST7735
* https://github.com/GuyCarver/MicroPython/blob/master/lib/ST7735.py
* https://github.com/adafruit/Adafruit-ST7735-Library
* https://github.com/adafruit/Adafruit_CircuitPython_ST7735R
* https://github.com/adafruit/Adafruit_CircuitPython_ST7735
* http://www.sunshine2k.de/coding/java/TriangleRasterization/TriangleRasterization.html
* https://www.instructables.com/Drawing-Filled-Circles-and-Triangles-With-MicroPyt/
* https://github.com/devbis/st7789py_mpy/blob/master/st7789py.py
* https://rgbcolorpicker.com/565
* https://docs.micropython.org/en/latest/library/framebuf.html

## License

Licensed under the [MIT License](http://opensource.org/licenses/MIT).

Copyright (c) 2024 Mike Causer
