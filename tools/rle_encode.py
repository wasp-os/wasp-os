from PIL import Image

im = Image.open('pine64.png')
pixels = im.load()

rle = []
rl = 0
px = 0
    
for y in range(im.height):
    for x in range(im.width):
        newpx = pixels[x, y]
        if newpx == px:
            rl += 1
            continue
        assert(rl < 255)
        rle.append(rl)
        rl = 1
        px = newpx
rle.append(rl)

sx = 240
sy = 240
image = bytes(rle)


data = bytearray(2*sx)
dp = 0
black = ord('#')
white = ord(' ')
color = black

for rl in image:
    while rl:
        data[dp] = color
        data[dp+1] = color
        dp += 2
        rl -= 1

        if dp >= (2*sx):
            print(data.decode('utf-8'))
            dp = 0

    if color == black:
        color = white
    else:
        color = black

assert(dp == 0)

print(image)
