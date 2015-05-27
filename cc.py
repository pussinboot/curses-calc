# setup
import curses
from curses import wrapper # play nice
################
# Variables
default_items = ['main','quit','test','clear','draw']
draw_menu = ['draw','quit','line','v_line','h_line','box','clear']
DEFAULT_CHAR = 'X'
################

################
# 
class Curse():
	def __init__(self):
		self.stdscr = curses.initscr()
		self.WIDTH = curses.COLS
		self.HEIGHT = curses.LINES
		# dont write on screen and dont wait for enter
		curses.noecho()
		curses.cbreak()
		curses.curs_set(False) # no blinking
		curses.start_color() # colors
		# epic keys
		self.stdscr.keypad(True)
		self.stdscr = curses.newwin(self.HEIGHT-1,self.WIDTH,0,0)
		self.bottom = curses.newwin(1,self.WIDTH,self.HEIGHT-1,0)
		self.bar(default_items)
		curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
		if curses.has_colors():
			curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
			curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
			curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
			curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
		self.painter = Painter(self.stdscr,self.WIDTH,self.HEIGHT)

	def clear(self):
		self.stdscr.clear()
		self.stdscr.refresh()
	
	def quit(self):
	# kill it
		curses.nocbreak()
		self.stdscr.keypad(False)
		curses.echo()
		curses.endwin()
	
	def test(self):
		self.clear()
		self.stdscr.addstr(0,0,'\nthis screen is {} wide and {} tall'.format(self.WIDTH,self.HEIGHT))
		if curses.has_colors():
			self.stdscr.addstr('\nthis screen should support color')
			for i in range(1,6):
				self.stdscr.addstr('\n' + str(i) , curses.color_pair(i))
		else:
			self.stdscr.addstr('\nthis screen does not support color')
		self.stdscr.refresh()
	
	def bar(self,items):
		def make_el(msg):
			l = len(msg)
			if l < 7: msg += ' '*(7-l)
			self.bottom.addstr(msg[0].upper(),curses.A_STANDOUT)
			self.bottom.addstr(msg[1:6].lower() + ' ')
		self.bottom.move(0,1)
		# to-do enforce max amount of menu elements disp ... if more :^)
		for msg in items[1:]:
			make_el(msg)
		self.bottom.move(0,self.WIDTH-len(items[0])-1)
		self.bottom.addstr(items[0].upper(),curses.A_BOLD)
		self.bottom.refresh()
	
	def prompt(self,text,cond=lambda x: x):
		while True:
			self.bottom.clear()
			self.bottom.move(0,1)
			self.bottom.addstr(text)
			curses.curs_set(True)
			curses.echo()
			s = self.bottom.getstr(0,len(text)+2)
			if cond(s): 
				curses.noecho()
				curses.curs_set(False)
				return s

	def draw(self):
		self.stdscr.clear()
		self.bar(draw_menu)
		while True:
			c = self.stdscr.getch()
			if c == ord('l'):
				p1 = int(self.prompt('x1?',self.painter.isint))
				p2 = int(self.prompt('y1?',self.painter.isint))
				p3 = int(self.prompt('x2?',self.painter.isint))
				p4 = int(self.prompt('y2?',self.painter.isint))
				ch = self.prompt('paint?',lambda x: True)
				if ch: 
					self.painter.line(p2,p1,p4,p3,ch[0])
				else:
					self.painter.line(p2,p1,p4,p3)
				self.bar(draw_menu)
			elif c == ord('v'):
				p1 = int(self.prompt('x?',self.painter.isint))
				p2 = int(self.prompt('y?',self.painter.isint))
				l = int(self.prompt('length?',self.painter.isint))
				self.painter.v_line(p2,p1,l)
				self.bar(draw_menu)
			elif c == ord('h'):
				p1 = int(self.prompt('x?',self.painter.isint))
				p2 = int(self.prompt('y?',self.painter.isint))
				l = int(self.prompt('length?',self.painter.isint))
				self.painter.h_line(p2,p1,l)
				self.bar(draw_menu)
			elif c == ord('b'):
				p1 = int(self.prompt('x1?',self.painter.isint))
				p2 = int(self.prompt('y1?',self.painter.isint))
				w = int(self.prompt('w?',self.painter.isint))
				h = int(self.prompt('h?',self.painter.isint))
				self.painter.box(p2,p1,h,w)
				self.bar(draw_menu)
			elif c == ord('c'):
				self.clear()
			elif c == ord('q'):
				self.bottom.clear()
				self.bar(default_items)
				break

################

################
# Drawing stuff
class Painter():
	# checks
	def __init__(self,stdscr,W,H):
		self.stdscr = stdscr
		self.W = W
		self.H = H

	def isint(self,value):
		try:
			int(value)
			return True
		except ValueError:
			return False
	
	def check_y(self,y):
		return y < self.H
	
	def check_x(self,x):
		return x < self.W
	
	def points(self,tup,c=DEFAULT_CHAR,col=1): # connect list of tuples of points :^)
		for i in range(len(tup)-1):
			y1,x1 = tup[i]
			y2,x2 = tup[i+1]
			self.line(self.stdscr,y1,x1,y2,x2,c,col)
	
	def line(self,start_y,start_x,end_y,end_x,c=DEFAULT_CHAR,col=1): # draw any line
		if start_x == end_x and start_y == end_y:
			self.stdscr.move(start_y,start_x)
			self.stdscr.addch(ord(c),col)
		elif self.check_y(start_y) and self.check_y(end_y) and self.check_x(start_x) and self.check_x(end_x):
			if start_y == end_y: h_line(self.stdscr,start_y,start_x,end_x-start_x+1)
			if start_x == end_x: v_line(self.stdscr,start_y,start_x,end_y-start_y+1)
			else: # Bresenham's algorithm
				dx = end_x - start_x
				dy = end_y - start_y
				ax = abs(2*dx)
				ay = abs(2*dy)
				sx = dx//abs(dx)
				sy = dy//abs(dy)
				x, y = start_x, start_y
				if ax > ay:
					d = ay - ax // 2
					while True:
						self.stdscr.move(y,x)
						self.stdscr.addch(c,col)
						if x == end_x: return
						if d >= 0:
							y += sy
							d -= ax
						x += sx
						d += ay
				else:
					d = ax - ay // 2
					while True:
						self.stdscr.move(y,x)
						self.stdscr.addch(c,col)
						if y == end_y: return
						if d >= 0:
							x += sx
							d -= ay
						y += sy
						d += ax
	
	
	
	def v_line(self,start_y,start_x,length,col=1): # draw a vertical line
		if self.check_y(start_y + length): # don't draw outside ..
			for i in range(length+1):
				self.stdscr.move(start_y+i,start_x)
				self.stdscr.addch(curses.ACS_VLINE,col)
	
	def h_line(self,start_y,start_x,length,col=1): # draw a horizontal line
		if self.check_x(start_x + length): # don't draw outside ..
			for i in range(length+1):
				self.stdscr.move(start_y,start_x+i)
				self.stdscr.addch(curses.ACS_HLINE,col)
	
	def box(self,start_y,start_x,h,w,col=1): # draw a box
		if self.check_y(start_y + h) and self.check_x(start_x + w):
			self.stdscr.move(start_y,start_x)
			self.stdscr.addch(curses.ACS_ULCORNER,col)
			self.stdscr.move(start_y,start_x+w)
			self.stdscr.addch(curses.ACS_URCORNER,col)
			self.stdscr.move(start_y+h,start_x)
			self.stdscr.addch(curses.ACS_LLCORNER,col)
			self.stdscr.move(start_y+h,start_x+w)
			self.stdscr.addch(curses.ACS_LRCORNER,col)
			self.v_line(start_y+1,start_x,h-2,col)
			self.v_line(start_y+1,start_x+w,h-2,col)
			self.h_line(start_y,start_x+1,w-2,col)
			self.h_line(start_y+h,start_x+1,w-2,col)

################

################
# Menus	
def main(stdscr):
	main_screen = Curse()
	main_screen.bar(default_items)
	while True:
		c = stdscr.getch()
		if c == ord('t'):
			main_screen.test()
			#points(stdscr,((1,1),(5,5),(1,10),(5,15),(1,20)))
		elif c == ord('c'):
			main_screen.clear()
		elif c == ord('d'):
			main_screen.draw()
		elif c == ord('q'):
			break
	main_screen.quit()

################

### start the program 
if __name__ == '__main__':
	wrapper(main)