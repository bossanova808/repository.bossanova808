#!/usr/bin/env python

from pylms.server import Server
from pylms.player import Player

sc = Server(hostname="192.168.1.51", port=9090)
sc.connect()

print "Logged in: %s" % sc.logged_in
print "Version: %s" % sc.get_version()

sq = sc.get_player("00:04:20:12:75:15")

print "Name: %s | Mode: %s | Time: %s | Connected: %s | WiFi: %s" % (sq.get_name(), sq.get_mode(), sq.get_time_elapsed(), sq.is_connected, sq.get_wifi_signal_strength())

#print sc.request("radios 0 100000")
#print sq.request("local items 0 100000")
#print sq.request("local playlist play item_id:7cec804f.15")
print sq.request("picks items 0 100000 item_id:be4417d3.0")



