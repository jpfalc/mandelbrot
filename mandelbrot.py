from PIL import Image
import numpy as np
from datetime import datetime
from datetime import timedelta

# faster divergence check; precalculates real^2 and imaginary^2, avoids generic multiplication
def check_diverge(z, c, max_iterations=256):
    a = z[0]
    b = z[1]
    a2 = a*a
    b2 = b*b
    for iteration in range(max_iterations):
        a_next = a2 - b2 + c[0]
        b_next = 2*a*b + c[1]
        a,b = a_next, b_next
        a2 = a*a
        b2 = b*b
        if a2 + b2 > 4:
            return(iteration)
    return(iteration)

# calculates pixel intensity based on # of steps needed to diverge
def pixel_intensity(i, n, exponent, low, high):
    percentile = (i / (n-1)) ** exponent
    intensity = round(low + (high-low) * percentile)
    return max(0, min(255, intensity))

# makes a color palette for n different intensities. optionally can force interior to equal a color
def make_palette(n, low=(0,0,0), high=(255,255,255), exponents=(1,1,1), interior=None):
    palette = []
    for i in range(n):
        intensity_r = pixel_intensity(i, n, exponents[0], low[0], high[0])
        intensity_g = pixel_intensity(i, n, exponents[1], low[1], high[1])
        intensity_b = pixel_intensity(i, n, exponents[2], low[2], high[2])
        color = (intensity_r, intensity_g, intensity_b)
        palette.append(color)
    if interior is not None:
        palette[n-1] = interior
    return palette

# create mandlebrot image
def make_image(palette, filename, z_initial=(0,0), dimensions=(318,300), left=-2, right=.65, top=1.25, bottom=-1.25, max_iterations=256):
    width, height = dimensions
    x_scale = (right - left) / width
    y_scale = (top - bottom) / height
    pixels = []
    start_time = datetime.now()
    
    for y in range(height):
        y_val = bottom + y_scale * (y+0.5)
        row = []
        for x in range(width):
            x_val = left + x_scale * (x+0.5)
            c = (x_val, y_val)
            n_iter = check_diverge(z_initial, c, max_iterations)
            row.append(palette[n_iter])
        pixels.append(row)
    array = np.array(pixels, dtype=np.uint8)
    img = Image.fromarray(array)
    img.save(filename)
    dt = datetime.now() - start_time
    ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    print('runtime was ', ms, 'ms')
    return pixels

palette_v1 = make_palette(n=256, high=(255,0,0))
palette_v2 = make_palette(n=256, low=(255,0,0), high=(0,0,0))
palette_v3 = make_palette(n=256, high=(128,128,255), interior=(0,0,0))
palette_v4 = make_palette(n=256, high=(128,128,255), exponents=(.5,.5,.5), interior=(0,0,0))
palette_v5 = make_palette(n=256, high=(255,128,255), exponents=(.75,2,.5), interior=(0,0,0))

dim_small = (318,300)
dim_large = (1272, 1200)
dim_huge = (1272*2, 1200*2)

# test images
#make_image(palette_v1, 'sm_mbrot_v1.png', dimensions=dim_small)
#make_image(palette_v2, 'sm_mbrot_v2.png', dimensions=dim_small)
#make_image(palette_v3, 'sm_mbrot_v3.png', dimensions=dim_small)
#make_image(palette_v4, 'sm_mbrot_v4.png', dimensions=dim_small)
make_image(palette_v5, 'sm_mbrot_v5_test2.png', dimensions=dim_small)
        
# main images. each of these takes ~10min to run
#make_image(palette_v1, 'mbrot_v1.png')
#make_image(palette_v2, 'mbrot_v2.png')
#make_image(palette_v3, 'mbrot_v3.png')
#make_image(palette_v4, 'mbrot_v4.png')
#make_image(palette_v5, 'mbrot_v5.png')