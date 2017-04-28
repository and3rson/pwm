#!/bin/bash

echo autostart
setxkbmap -layout 'us,ru,ua' -option grp:alt_shift_toggle
xmodmap ~/.Xmodmap
xset r rate 200 25
compton --config ~/.compton.conf -b -f
echo /autostart
