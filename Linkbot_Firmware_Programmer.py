#!/usr/bin/env python

#from gi.repository import Gtk
import pygtk
import gtk as Gtk
import glib
import time

import os
from os.path import join
import subprocess

class Handler:
  def __init__(self, gtkbuilder):
    self.builder = gtkbuilder
    self.liststore = gtkbuilder.get_object("liststore_ttyDevices")
    self.combobox = gtkbuilder.get_object("combobox1")
    self.filechooser = gtkbuilder.get_object("filechooserwidget1")
    self.spinner = gtkbuilder.get_object("spinner1")
    self.start_button = gtkbuilder.get_object("button_start")
    self.elapsed_time_entry = gtkbuilder.get_object("entry1")

  def on_button_start_clicked(self, *args):
    model = self.combobox.get_model()
    active = self.combobox.get_active()
    if active < 0:
      self.__errorDialog('Please select a TTY device.')
      return
    cmd = [
      'avrdude', 
      '-c',
      'arduino', 
      '-P',
      model[active][0],
      '-p',
      'm128rfa1',
      '-e',
      '-U',
      'fl:w:{}'.format(self.filechooser.get_filename()),
      '-b',
      '57600']
    self.myprocess = subprocess.Popen(cmd)
    self.start_button.set_sensitive(False)
    glib.timeout_add(200, self.check_progress_timeout_cb)
    self.spinner.start()
    self.start_time = time.time()
    
  def check_progress_timeout_cb(self):
    rc = self.myprocess.poll()
    if rc is not None:
      if rc is not 0:
        self.__errorDialog("Error programming firmware.")
      self.spinner.stop()
      self.start_button.set_sensitive(True)
      return False
    self.elapsed_time_entry.set_text(
        '{} seconds'.format(time.time() - self.start_time))
    return True

  def on_button_quit_clicked(self, *args):
    Gtk.main_quit(*args)

  def button_apply_clicked_cb(self, *args):
    self.__programID()
    entry = self.builder.get_object("entry1")
    entry.set_text('')

  def button_cancel_clicked_cb(self, *args):
    Gtk.main_quit(*args)
    pass

  def button_ok_clicked_cb(self, *angs):
    self.__programID()
    Gtk.main_quit(*args)
    pass

  def button_clear_clicked_cb(self, *args):
    self.builder.get_object("entry1").set_text('')

  def gtk_main_quit(self, *args):
    Gtk.main_quit(*args)

  def entry1_activate_cb(self, *args):
    self.button_apply_clicked_cb(*args)

  def button_getid_clicked_cb(self, *args):
    linkbot = Linkbot()
    print 'Connecting to {}...'.format(self.combobox.get_child().get_text())
    linkbot.connectWithTTY(self.combobox.get_child().get_text())
    time.sleep(0.2)
    myid = linkbot.getID()
    linkbot.disconnect()
    d = Gtk.MessageDialog(type = Gtk.MESSAGE_ERROR, flags=Gtk.DIALOG_MODAL, buttons = Gtk.BUTTONS_CLOSE)
    d.set_markup('Linkbot id is {}'.format(myid))
    d.run()
    d.destroy()


  def __programID(self):
    entry = self.builder.get_object("entry1")
    text = entry.get_text()
    if len(text) != 4:
      self.__errorDialog("The Serial ID must be 4 characters long.")
      return
    # Connect to a linkbot
    try:
      """
      ttydev = find_tty_usb('03eb', '204b')
      if ttydev is None:
        self.__errorDialog("No Linkbot detected. Please turn on and connect a Linkbot.")
        return
      """
      linkbot = Linkbot()
      print 'Connecting to {}...'.format(self.combobox.get_child().get_text())
      linkbot.connectWithTTY(self.combobox.get_child().get_text())
      time.sleep(0.2)
      linkbot.setLEDColor(0, 255, 0)
      time.sleep(0.1)
      linkbot.setID(text.upper())
      time.sleep(0.1)
      if linkbot.getID() != text.upper():
        linkbot.disconnect()
        raise Exception('Error programming serial ID')
      linkbot.setBuzzerFrequency(440)
      time.sleep(0.5)
      linkbot.setBuzzerFrequency(0)
      linkbot.disconnect()
      try:
        f = open(logfile, 'a')
      except:
        f = open(logfile, 'w')
      f.write('{0}, {1}, {2}{3:02}{4:02}{5:02}{6:02}\n'.format(
            text.upper(), 
            versioninfo, 
            time.gmtime().tm_year,
            time.gmtime().tm_mon,
            time.gmtime().tm_mday,
            time.gmtime().tm_hour,
            time.gmtime().tm_min))
      f.close()
    except Exception as e:
      self.__errorDialog(str(e))

  def __errorDialog(self, text):
    d = Gtk.MessageDialog(type = Gtk.MESSAGE_ERROR, flags=Gtk.DIALOG_MODAL, buttons = Gtk.BUTTONS_CLOSE)
    d.set_markup(text)
    d.run()
    d.destroy()

#Get the current version string 
builder = Gtk.Builder()
builder.add_from_file("interface.glade")
sighandler = Handler(builder)
builder.connect_signals(sighandler)
window = builder.get_object("window1")
window.show_all()
Gtk.main()
