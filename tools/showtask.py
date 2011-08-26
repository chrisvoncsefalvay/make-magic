#! /usr/bin/env python

'''monitor a task in realtime

This should use the HTTP interface. It currently doesn't
'''

title = "make-magic stat"

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import GObject
import sys
import traceback

import lib.magic

# Deal with keyboard interrupts gracefully
def exc_handler(exc, val, tb):
	if exc != KeyboardInterrupt:
		traceback.print_exception(exc, val, tb)
		sys.exit()
	else:
		gtk.main_quit()
sys.excepthook = exc_handler

class ShowStuff(object):
	def __init__(self, stuff, update_interval=1000):
		self.window = window = gtk.Window()
		window.set_title(title)
		window.connect('destroy', lambda win: gtk.main_quit())
		window.set_border_width(5)

		sw = gtk.ScrolledWindow()
		window.add(sw)
		vp = gtk.Viewport()
		sw.add(vp)
		vbox = self.vbox = gtk.VBox(spacing=0)
		vp.add(vbox)
		#window.add(vbox)

		self.labels = {}
		self.frames = {}
		self.ebox = {}
		for k,v,col in stuff:
			eb = gtk.EventBox()
			f = gtk.Frame(label=k)
			l = gtk.Label(v)
			l.set_alignment(0,.5)
			#l.set_justification(gtk.Justification.LEFT)
			f.add(l)
			eb.add(f)
			self.labels[k] = l
			self.frames[k] = f
			self.ebox[k] = eb
			vbox.pack_start(eb, True, True, 0)
			if col: self.set_color(k,col)
		window.show_all()
		GObject.timeout_add(update_interval, self.update_stuff)

	def set_color(self, k, col):
		self.ebox[k].modify_bg(gtk.StateType.NORMAL, gdk.color_parse(col)[1])

	def update_stuff(self):
		print "update timer"
		return True


class MonitorTask(ShowStuff):
	def __init__(self, uuid, interval=1000):
		self.magic = lib.magic.Magic()
		self.uuid = uuid
		ShowStuff.__init__(self, self.get_task_tuples(), interval)
		self.window.set_title("make-magic task: "+uuid)

	def get_task_tuples(self):
		task = self.magic.get_task(self.uuid)
		for item in task['items']:
			color = "green" if item['state'] == 'COMPLETED' else None
			item.pop('depends',None)
			desc = ', '.join(str(k)+": "+str(v) for k,v in item.items())
			yield (item['name'], desc, color)
		
	def update_stuff(self):
		print "updating"
		return True

def monitor_task(uuid):
	mt = MonitorTask(uuid)
	gtk.main()

if __name__ == "__main__":
	#stuff = (('a', "Hello", 'green'), ('b', "World", None))
	#ShowStuff(stuff)
	#gtk.main()
	monitor_task(sys.argv[1])