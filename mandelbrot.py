from PIL import Image
import numpy as np
from datetime import datetime
from datetime import timedelta

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

# makes a numpy array containing the real-values for a particular row of pixels
def make_array_reals(params):
    row = []
    for x in range(params['width']):
        real_val = params['left'] + params['x_scale'] * (x+0.5)
        row.append(real_val)
    array = np.array(row, dtype=np.double)
    return(array)

def get_row_intensities(row_num, params, const_r):
    a = np.full(params['width'], params['z_real'])
    b = np.full(params['width'], params['z_imag'])
    a2, b2 = np.square(a), np.square(b)
    const_i = np.full(params['width'], params['bottom'] + params['y_scale'] * (row_num+0.5))
    escape_times = np.full(params['width'], 0)
    
    for iteration in range(params['max_iterations']):
        a_next = a2 - b2 + const_r
        b_next = 2 * a * b + const_i
        a, b = a_next, b_next
        a2, b2 = np.square(a), np.square(b)
        escape_times += a2 + b2 < 4
    escape_times = np.minimum(escape_times, params['max_iterations']-1)
    return(escape_times)

def apply_palette(intensities, palette):
    pixels = []
    for i in range(len(intensities)):
        pixels.append(palette[intensities[i]])
    return(pixels)

# zoom 1 means the lowest dimension has a range of 4. range is halved for each zoom level
def make_params(center=(-0.675,0), zoom=1, width=1000, height=1000):
    width_scale = width / min(width, height)
    height_scale = height / min(width, height)
    params = {}
    params['z_real'] = 0
    params['z_imag'] = 0
    params['width'] = width
    params['height'] = height
    params['bottom'] = center[1] - 2 * height_scale * (2**-(zoom-1))
    params['top'] = center[1] + 2 * height_scale * (2**-(zoom-1))
    params['left'] = center[0] - 2 * width_scale * (2**-(zoom-1))
    params['right'] = center[0] + 2 * width_scale * (2**-(zoom-1))
    params['max_iterations'] = 256
    params['x_scale'] = (params['right'] - params['left']) / params['width']
    params['y_scale'] = (params['top'] - params['bottom']) / params['height']
    return(params)


def make_image(palette, filename, center=(-0.675,0), zoom=1, width=1200, height=1200):
    start_time = datetime.now()
    params = make_params(center, zoom, width, height)
    reals = make_array_reals(params)
    pixels = []
    for row in range(params['height']):
        row_intensities = get_row_intensities(row, params, reals)
        row_pixels = apply_palette(row_intensities, palette)
        pixels.append(row_pixels)

    array = np.array(pixels, dtype=np.uint8)
    img = Image.fromarray(array)
    img.save(filename)
    dt = datetime.now() - start_time
    ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
    print('runtime was ', ms, 'ms')
    return(pixels)

palette = make_palette(n=256, high=(255,128,255), exponents=(.75,2,.5), interior=(0,0,0))

# default image showing the whole set
make_image(palette, 'img/mandlebrot.png', zoom=1.66, width=318*4, height=300*4)

# zoomed in on a spiral
make_image(palette, 'img/spiral.png', center=(-.66468458, .355508837), zoom=12)
