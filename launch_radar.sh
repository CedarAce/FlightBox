#!/bin/bash

# 1. Kill any existing chromium to free up the profile lock
pkill chromium

# 2. Launch using your ACTUAL user profile
# This carries over the WebGL settings that worked when you opened it manually
chromium --kiosk \	
--user-data-dir="/home/$USER/.config/chromium" \
--window-size=480,320 \
--force-device-scale-factor=0.8 \
--enable-gpu-rasterization \
--ignore-gpu-blocklist \
"https://www.flightradar24.com/45.33,-75.67/13" &

# 3. Wait for load
sleep 10

# 4. Clear the popups
export DISPLAY=:0
xdotool mousemove 240 160 click 1
