#!/usr/bin/env python3
import os
import threading
import time
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Notify', '0.7')

from configparser import ConfigParser
from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify
from gi.repository import GdkPixbuf
from PIL import Image, ImageDraw, ImageFont

APPINDICATOR_ID = 'myappindicator'
applicationname = 'Battery conservation'
cm_path = '/sys/bus/platform/drivers/ideapad_acpi/VPC2004:00/conservation_mode'
bat_capacity_path = '/sys/class/power_supply/BAT0/capacity'
config_object = ConfigParser()
indicator = None
old_notification = None
bat_capacity = 0
percentage = 0
updatedelay = 30

# icons
icon_notification = os.path.abspath('battery_conservation.png')
icon_charging = 'charge.png'
icon_charging60 = 'limit60.png'
icon_charging80 = 'limit80.png'
icon_charging90 = 'limit90.png'
icon = icon_charging


def build_menu():
    menu = Gtk.Menu()
    item_charge90 = Gtk.MenuItem('Charge to 90%')
    item_charge90.connect('activate', charge90)
    menu.append(item_charge90)
    item_charge80 = Gtk.MenuItem('Charge to 80%')
    item_charge80.connect('activate', charge80)
    menu.append(item_charge80)
    item_charge60 = Gtk.MenuItem('Charge to 60%')
    item_charge60.connect('activate', charge60)
    menu.append(item_charge60)
    menu.append(Gtk.SeparatorMenuItem())
    item_charge_enabled = Gtk.MenuItem('Disabled')
    item_charge_enabled.connect('activate', charge_enabled)
    menu.append(item_charge_enabled)
    menu.append(Gtk.SeparatorMenuItem())
    item_quit = Gtk.MenuItem('Quit')
    item_quit.connect('activate', quit)
    menu.append(item_quit)
    menu.show_all()
    return menu


def notification(text, img=icon_notification, close=0):
    global old_notification
    # close old notification if exists
    try:
        old_notification.close()
    except:
        pass
    notification = Notify.Notification.new(applicationname, text)
    # Use GdkPixbuf to create the proper image type
    image = GdkPixbuf.Pixbuf.new_from_file(img)
    # Use the GdkPixbuf image
    notification.set_icon_from_pixbuf(image)
    notification.set_image_from_pixbuf(image)
    notification.show()
    if close != 0:
        old_notification = notification
        time.sleep(close)
        notification.close()


def notification_ht(text, img=icon_notification, close=0):
    threading.Thread(target = notification, args = (text, img, close)).start()


def create_conf():
    config_object["CONFIG"] = {
        "percentage": "0",
        "test": "testtext"
    }
    with open('config.ini', 'w') as conf:
        config_object.write(conf)
    notification("Created configuration File.", icon_notification)


def read_conf():
    global percentage
    config_object.read("config.ini")
    try:
        config = config_object["CONFIG"]
        # set global vars
        percentage = int(config["percentage"])
        #globaltestvar = config["test"]
    except:
        notification("Failed to read Settings!", icon_notification)
        create_conf()
        print('Created configuration file.')


def update_conf():
    global percentage
    #Read config.ini file
    config_object.read("config.ini")
    #Get the CONFIG section
    config = config_object["CONFIG"]
    #Update config object
    config["percentage"] = str(percentage)
    #config["test"] = "globaltestvar"
    try:
        #Write changes back to file
        with open('config.ini', 'w') as conf:
            config_object.write(conf)
        notification("Settings Saved.", icon_notification, 1)
    except:
        notification("Failed to save Settings!", icon_notification)
        create_conf()
        print('Created configuration file.')


def read_state(path):
    file = open(path, mode='r')
    text = file.read()
    file.close()
    return int(text)


def write_state(state):
    global cm_path
    global applicationname
    try:
        with open(cm_path, 'w') as f:
            f.write(str(state))
    except:
        print('Permission Error!\nSet perms for ' + cm_path + ' to 777')
        notification("Permission Error!\nPlease grant perms for: " + cm_path)


def limit_charging(seperate_thread=False):
    global icon
    global indicator
    global bat_capacity
    global percentage

    state = read_state(cm_path)
    bat_capacity = read_state(bat_capacity_path)
    old_icon = icon
    print('Actual battery capacity: ' + str(bat_capacity) + '%')

    if percentage == 0 or percentage == 100:
        print("charging...")
        icon = icon_charging
        # if limiting change to no limit
        if state == 1:
            write_state(0)
            print('Conservation mode changed to ' + str(read_state(cm_path)))
    elif bat_capacity >= percentage:
        print("charging limited to " + str(percentage) + "%")
        icon = 'limit' + str(percentage) + '.png'
        # if not limiting change to limit
        if state == 0:
            write_state(1)
            print('Conservation mode changed to ' + str(read_state(cm_path)))
            # background thread notifications
            if seperate_thread:
                notification("Conservation mode has been activated at " + str(percentage) + "%", icon_notification)
    else:
        icon = 'limit' + str(percentage) + '.png'
        # do not limit yet but later
        if state == 1:
            write_state(0)
            print('Conservation mode changed to ' + str(read_state(cm_path)))
        print('charging... limiting later automatically!')

    # update icon if changed
    if icon != old_icon:
        indicator.set_icon(os.path.abspath(icon))

    # notify if something changed (only if its not running on a seperate thread)
    if seperate_thread == False and icon != old_icon:
        if percentage == 0:
            notification_ht("Conservation mode disabled", icon_notification, 2)
        else:
            notification_ht("Conservation mode enabled at " + str(percentage) + "%", icon_notification, 2)


def charge90(_):
    global percentage
    percentage = 90
    limit_charging()


def charge80(_):
    global percentage
    percentage = 80
    limit_charging()


def charge60(_):
    global percentage
    percentage = 60
    limit_charging()


def charge_enabled(_):
    global percentage
    percentage = 0
    limit_charging()


def create_img(number):
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("OpenSans-Semibold.ttf", 240)
    draw.text((-9, -43),str(number),(256, 256, 256),font=font)
    img.save('limit'+str(number)+'.png')


def update(arg):
    while True:
        time.sleep(updatedelay)
        limit_charging(True)


def main(arg):
    global indicator
    global icon
    Gtk.init()
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath(icon), appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(build_menu())
    Notify.init(APPINDICATOR_ID)
    # read charging profile from config file
    read_conf()
    # set charging profile
    limit_charging()
    Gtk.main()


# needs to be done only once if images ain't created yet
#create_img(60)
#create_img(80)
#create_img(90)


def quit(_):
    update_conf()
    Notify.uninit()
    Gtk.main_quit()
    exit(0)

if __name__ == "__main__":
    bat_capacity = read_state(bat_capacity_path)
    # main thread for application and appindicator
    main_thread = threading.Thread(target = main, args = (None,))
    main_thread.start()
    # second thread to update automatically
    update_thread = threading.Thread(target = update, args = (None,))
    update_thread.start()
