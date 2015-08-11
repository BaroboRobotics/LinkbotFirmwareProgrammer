#!/bin/sh

fwFile=Z-Link_C-STEM_Firmware_20150608.hex

for i in /dev/ttyACM*; do 
	avrdude -c arduino -P $i -p m128rfa1 -e -U fl:w:$fwFile -b 57600 &
done
