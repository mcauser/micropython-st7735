# MicroPython ST7735 TFT display driver

# v0.0.6

# tested with
# UM TinyPICO + UM IPS LCD 160x80
# MicroPython v1.22.1

from time import sleep_ms
import math

class ST7735R:
	# commands
	CMD_SWRESET = const(0x01)
	CMD_SLPIN = const(0x10)
	CMD_SLPOUT = const(0x11)
	CMD_PTLON = const(0x12)
	CMD_NORON = const(0x13)
	CMD_INVOFF = const(0x20)
	CMD_INVON = const(0x21)
	CMD_DISPOFF = const(0x28)
	CMD_DISPON = const(0x29)
	CMD_CASET = const(0x2A)
	CMD_RASET = const(0x2B)
	CMD_RAMWR = const(0x2C)
	CMD_COLMOD = const(0x3A)
	CMD_MADCTL = const(0x36)

	# panel function commands
	CMD_FRMCTR1 = const(0xB1)
	CMD_FRMCTR2 = const(0xB2)
	CMD_FRMCTR3 = const(0xB3)
	CMD_INVCTR = const(0xB4)
	CMD_DISSET5 = const(0xB6) # Bcmd
	CMD_PWCTR1 = const(0xC0)
	CMD_PWCTR2 = const(0xC1)
	CMD_PWCTR3 = const(0xC2)
	CMD_PWCTR4 = const(0xC3)
	CMD_PWCTR5 = const(0xC4)
	CMD_VMCTR1 = const(0xC5)
	CMD_GMCTRP1 = const(0xE0)
	CMD_GMCTRN1 = const(0xE1)
	CMD_PWCTR6 = const(0xFC) # Bcmd

	# colors
	COLOR_BLACK   = const(0x0000)
	COLOR_BLUE    = const(0x001F)
	COLOR_RED     = const(0xF800)
	COLOR_GREEN   = const(0x07E0)
	COLOR_CYAN    = const(0x07FF)
	COLOR_MAGENTA = const(0xF81F)
	COLOR_YELLOW  = const(0xFFE0)
	COLOR_WHITE   = const(0xFFFF)

	def __init__(self, spi, dc, cs=None, rst=None, w=80, h=160, x=26, y=1, rot=0, inv=True, bgr=True):
		self.spi = spi
		self.dc = dc
		self.cs = cs # optional
		self.rst = rst # optional

		self.w = w # panel w, not affected by rotation
		self.h = h # panel h, not affected by rotation
		self.x = x
		self.y = y

		self.rot = rot # rotation
		self.inv = inv # invert
		self.bgr = bgr # rgb/bgr

		self._init_rotate(rot)
		self._caset = bytearray(4) # col
		self._raset = bytearray(4) # row

	def init(self):
		self.hard_reset()
		self.soft_reset()
		self.sleep(False)
		sleep_ms(255)

		# TODO extrapolate out init seq to support various LCDs

		# Bcmd
		#self.cmd(CMD_COLMOD, b'\x05') # 16-bit
		#self.cmd(CMD_FRMCTR1, b'\x00\x06\x03')
		#sleep_ms(10)
		#self.cmd(CMD_DISSET5, b'\x15\x02')
		#self.cmd(CMD_INVCTR, b'\x00')
		#self.cmd(CMD_PWCTR1, b'\x02\x70')
		#sleep_ms(10)
		#self.cmd(CMD_PWCTR2, b'\x05')
		#self.cmd(CMD_PWCTR3, b'\x3C\x38')
		#self.cmd(CMD_PWCTR6, b'\x11\x15')
		#self.cmd(CMD_GMCTRP1, b'\x09\x16\x09\x20\x21\x1B\x13\x19\x17\x15\x1E\x2B\x04\x05\x02\x0E')
		#self.cmd(CMD_GMCTRN1, b'\x0B\x14\x08\x1E\x22\x1D\x18\x1E\x1B\x1A\x24\x2B\x06\x06\x02\x0F')
		#sleep_ms(10)
		#self.cmd(CMD_CASET, b'\x00\x02\x00\x81')
		#self.cmd(CMD_RASET, b'\x00\x02\x00\x81')

		# Rcmd
		self.cmd(CMD_FRMCTR1, b'\x01\x2C\x2D')
		self.cmd(CMD_FRMCTR2, b'\x01\x2C\x2D')
		self.cmd(CMD_FRMCTR3, b'\x01\x2C\x2D\x01\x2C\x2D')
		sleep_ms(10)

		self.cmd(CMD_INVCTR, b'\x07')
		self.cmd(CMD_PWCTR1, b'\xA2\x02\x84')
		self.cmd(CMD_PWCTR2, b'\xC5')
		self.cmd(CMD_PWCTR3, b'\x8A\x00')
		self.cmd(CMD_PWCTR4, b'\x8A\x2A')
		self.cmd(CMD_PWCTR5, b'\x8A\xEE')
		self.cmd(CMD_VMCTR1, b'\x0E')

		self.invert(self.inv)
		self.rotate(self.rot)

		self.cmd(CMD_COLMOD, b'\x05') # 16-bit

		self._set_window(0, 0, self.width, self.height)
		# self._caset[1] = self.xoff
		# self._caset[3] = self.xoff + self.width
		# self._raset[1] = self.yoff
		# self._raset[3] = self.yoff + self.height
		# self.cmd(CMD_CASET, self._caset)
		# self.cmd(CMD_RASET, self._raset)
		# self.cmd(CMD_RAMWR)

		self.cmd(CMD_GMCTRP1, b'\x02\x1C\x07\x12\x37\x32\x29\x2D\x29\x25\x2B\x39\x00\x01\x03\x10')
		self.cmd(CMD_GMCTRN1, b'\x03\x1D\x07\x06\x2E\x2C\x29\x2D\x2E\x2E\x37\x3F\x00\x00\x02\x10')

		self.cmd(CMD_NORON)
		sleep_ms(10)

		self.power(True)
		sleep_ms(100)

	def hard_reset(self):
		self._dc_low()
		if self.rst is not None:
			self._rst_high()
			sleep_ms(500)
			self._rst_low()
			sleep_ms(500)
			self._rst_high()
			sleep_ms(500)

	def soft_reset(self):
		self.cmd(CMD_SWRESET)
		sleep_ms(150)

	def _init_rotate(self, r):
		if r & 1 == 0:
			# landscape on 160x80
			self.width = self.w
			self.height = self.h
			self.xoff = self.x
			self.yoff = self.y
		else:
			# portrait on 160x80
			self.width = self.h
			self.height = self.w
			self.xoff = self.y
			self.yoff = self.x

	def rotate(self, r=0):
		self._init_rotate(r)

		if r == 0:
			madctl = 0x00 # tab on left
		elif r == 1:
			madctl = 0x60 # tab on bottom
		elif r == 2:
			madctl = 0xC0 # tab on right
		if r == 3:
			madctl = 0xA0 # tab on top
		if self.bgr:
			madctl |= 0x08 # alt ordering
		self.cmd(CMD_MADCTL, bytes([madctl]))

	def _dc_low(self):
		self.dc.off()

	def _dc_high(self):
		self.dc.on()

	def _rst_low(self):
		if self.rst is not None:
			self.rst.off()

	def _rst_high(self):
		if self.rst is not None:
			self.rst.on()

	def _cs_low(self):
		if self.cs is not None:
			self.cs.off()

	def _cs_high(self):
		if self.cs is not None:
			self.cs.on()

	def cmd(self, command=None, data=None):
		self._cs_low()
		if command is not None:
			self._dc_low()
			self.spi.write(bytes([command]))
		if data is not None:
			self._dc_high()
			self.spi.write(data)
		self._cs_high()

	def data(self, data):
		# Display data write implementation using SPI
		self._dc_high()
		self._cs_low()
		self.spi.write(data)
		self._cs_high()

	def _repeat_data_slow(self, data, count):
		# Slowed down by many spi.write() calls. optimise by batching data, see: _repeat_data
		self._dc_high()
		self._cs_low()
		for _ in range(count):
			self.spi.write(data)
		self._cs_high()

	def _repeat_data(self, data, count):
		# Attempt to optimise by calling spi.write() in groups of 50 bytes
		batch_size = 50
		repeat = count // batch_size
		remain = count % batch_size
		if repeat > 0:
			repeat_bytes = bytes(data) * batch_size
		if remain > 0:
			remain_bytes = bytes(data) * remain
		self._dc_high()
		self._cs_low()
		for _ in range(repeat):
			self.spi.write(repeat_bytes)
		for _ in range(remain):
			self.spi.write(remain_bytes)
		self._cs_high()

	def _repeat_data_bulk(self, data, count):
		# Ram hungry version. Calls spi.write() once with many bytes
		# Garbage collect after?
		self._dc_high()
		self._cs_low()
		self.spi.write(bytes(data) * count)
		self._cs_high()

	def sleep(self, sleep=False):
		self.cmd(CMD_SLPIN if sleep else CMD_SLPOUT)

	def power(self, on=None):
		self.cmd(CMD_DISPON if on else CMD_DISPOFF)

	def invert(self, invert=True):
		self.cmd(CMD_INVON if invert else CMD_INVOFF)

	def _set_window(self, x0, y0, x1, y1):
		self._caset[1] = self.xoff + x0
		self._caset[3] = self.xoff + x1
		self._raset[1] = self.yoff + y0
		self._raset[3] = self.yoff + y1
		self.cmd(CMD_CASET, self._caset)
		self.cmd(CMD_RASET, self._raset)
		self.cmd(CMD_RAMWR)

	def fill(self, color=COLOR_WHITE):
		# TODO ~190ms @ 160x80
		self.rect(0, 0, self.width, self.height, color)

	def fill_slow(self, color=COLOR_WHITE):
		# TODO ~2596ms @ 160x80
		self._set_window(0, 0, self.width-1, self.height-1)
		self._repeat_data_slow(bytearray([color >> 8, color]), self.width * self.height)

	def fill_bulk(self, color=COLOR_WHITE):
		# TODO ~140ms @ 160x80
		self._set_window(0, 0, self.width-1, self.height-1)
		self._repeat_data_bulk(bytearray([color >> 8, color]), self.width * self.height)

	def color565(self, r, g, b):
		# convert 24-bit RGB888 into 16-bit RGB565 value
		# 0b_RRRR_RGGG_GGGB_BBBB
		return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3

	def pixel(self, x, y, color):
		# based on hosaka's
		# Draw a single pixel on the display with given color
		self._set_window(x, y, x + 1, y + 1)
		self._repeat_data(bytearray([color >> 8, color]), 1)

	def rect_outline(self, x, y, w, h, color):
		self.hline(x, y, w, color)
		self.vline(x+w-1, y, h, color)
		self.hline(x, y+h-1, w, color)
		self.vline(x, y, h, color)

	def rect(self, x, y, w, h, color):
		# based on hosaka's
		# Draw a rectangle with specified coordinates/size and fill with color
		# Check the coordinates and trim if necessary
		if (x >= self.width) or (y >= self.height):
			# raise error?
			return
		if (x + w - 1) >= self.width:
			w = self.width - x
		if (y + h - 1) >= self.height:
			h = self.height - y

		self._set_window(x, y, x + w - 1, y + h - 1)
		self._repeat_data(bytearray([color >> 8, color]), (w*h))

	def circle(self, x, y, radius, color):
		# x,y = centre
		self.hline(x-radius, y, radius*2, color)
		for i in range(1, radius):
			a = int(math.sqrt(radius*radius - i*i)) # Pythagoras' theorem
			self.hline(x-a, y+i, a*2, color) # bot half
			self.hline(x-a, y-i, a*2, color) # top half

	def circle_outline(self, x, y, radius, color):
		# x,y = centre
		self.pixel(x-radius, y, color) # top
		self.pixel(x+radius, y, color) # right
		self.pixel(x, y-radius, color) # bot
		self.pixel(x, y+radius, color) # left
		for i in range(1, radius):
			a = int(math.sqrt(radius*radius - i*i)) # Pythagoras' theorem
			# draw arcs (clockwise and anti-clockwise as they each fade out)
			self.pixel(x-a, y-i, color) # top to right
			self.pixel(x-i, y-a, color) # right to top
			self.pixel(x+a, y-i, color) # bot to right
			self.pixel(x+i, y-a, color) # right to bot
			self.pixel(x-a, y+i, color) # top to left
			self.pixel(x-i, y+a, color) # left to top
			self.pixel(x+a, y+i, color) # bot to left
			self.pixel(x+i, y+a, color) # left to bot

	def triangle_outline(self, x0, y0, x1, y1, x2, y2, color):
		# just 3 connected lines
		self.line(x0, y0, x1, y1, color)
		self.line(x1, y1, x2, y2, color)
		self.line(x2, y2, x0, y0, color)

	# def fill_triangle():
	# TODO

	def line(self, x0, y0, x1, y1, color):
		# based on hosaka's
		# line is vertical
		if x0 == x1:
			# use the smallest y
			start, end = (x1, y1) if y1 < y0 else (x0, y0)
			self.vline(start, end, abs(y1 - y0) + 1, color)

		# line is horizontal
		elif y0 == y1:
			# use the smallest x
			start, end = (x1, y1) if x1 < x0 else (x0, y0)
			self.hline(start, end, abs(x1 - x0) + 1, color)

		else:
			# Bresenham's algorithm
			dx = abs(x1 - x0)
			dy = abs(y1 - y0)
			inx = 1 if x1 - x0 > 0 else -1
			iny = 1 if y1 - y0 > 0 else -1

			# steep line
			if (dx >= dy):
				dy <<= 1
				e = dy - dx
				dx <<= 1
				while (x0 != x1):
					# draw pixels
					self.pixel(x0, y0, color)
					if (e >= 0):
						y0 += iny
						e -= dx
					e += dy
					x0 += inx

			# not steep line
			else:
				dx <<= 1
				e = dx - dy
				dy <<= 1
				while (y0 != y1):
					# draw pixels
					self.pixel(x0, y0, color)
					if (e >= 0):
						x0 += inx
						e -= dy
					e += dx
					y0 += iny

	def hline(self, x, y, w, color):
		# based on hosaka's
		if (x >= self.width) or (y >= self.height):
			return
		if (x + w - 1) >= self.width:
			w = self.width - x

		self._set_window(x, y, x + w - 1, y)
		self._repeat_data(bytearray([color >> 8, color]), x + w - 1)

	def vline(self, x, y, h, color):
		# based on hosaka's
		if (x >= self.width) or (y >= self.height):
			return
		if (y + h - 1) >= self.height:
			h = self.height - y

		self._set_window(x, y, x, y + h - 1)
		self._repeat_data(bytearray([color >> 8, color]), y + h - 1)

	def text(self, x, y, string, font, color, size=1, x_wrap=None):
		# based on hosaka's
		# Draw text at a given position using the user font.
		# Font can be scaled with the size parameter.
		if font is None:
			return

		width = size * font.width() + 1

		px = x
		for c in string:
			self.char(px, y, c, font, color, size, size)
			px += width

			# wrap the text to the next line if it reaches the end
			if px + width > self.width:
				y += font.height() * size + 1
				# when the text wraps, what should the lowest x be? (x or x_wrap)
				if x_wrap is not None:
					px = x_wrap
				else:
					px = x

	def char(self, x, y, char, font, color, sizex=1, sizey=1):
		# based on hosaka's
		# Draw a character at a given position using the user font.
		# Font is a data dictionary, can be scaled with sizex and sizey.
		if font is None:
			return

		startchar = font.start()
		endchar = font.end()
		ci = ord(char)

		if (startchar <= ci <= endchar):
			width = font.width()
			height = font.height()
			ci = (ci - startchar) * width

			ch = font._font[ci:ci + width]

			# no font scaling
			px = x
			if (sizex <= 1 and sizey <= 1):
				for c in ch:
					py = y
					for _ in range(height):
						if c & 0x01:
							self.pixel(px, py, color)
						py += 1
						c >>= 1
					px += 1

			# scale to given sizes
			else:
				for c in ch:
					py = y
					for _ in range(height):
						if c & 0x01:
							self.rect(px, py, sizex, sizey, color)
						py += sizey
						c >>= 1
					px += sizex
		else:
			# character not found in this font
			return
