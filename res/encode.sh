#!/bin/sh

# Split clock.png into digits
for i in `seq 9`
do
	convert clock.png -crop 48x60+$((i*48 - 48))+0 clock_$i.png
done
convert clock.png -crop 48x60+$((9*48))+0 clock_0.png
convert clock.png -crop 48x60+$((11*48))+0 clock_colon.png

# Encode the clock digits
