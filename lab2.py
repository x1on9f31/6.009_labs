#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image


# PASTED FROM LAB 1

def get_pixel(image, x, y):
    width = image['width']
    return image['pixels'][width * y + x ]


def set_pixel(image, x, y, c):
    width = image['width']
    image['pixels'][width * y + x] = c


def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'].copy(),
    }
    for y in range(image['height']):
        for x in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def get_cpixel(image, x,y):
    """
    Takes coordinates (including those out of bounds) as input
    and determines the coordinates that get_pixel should call and subsequently
    calls it
    """
    newX = x
    newY = y
    height = image['height']
    width = image['width']
    if x < 0:
        newX = 0
    if y < 0:
        newY = 0
    if x >= width:
        newX = width - 1
    if y >= height:
        newY = height - 1
    return get_pixel(image, int(newX), int(newY))


def correlate(image, kernel):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    Store the n x n kernel as a length n**2 list. The first n elements represent the first row, and so on.
    """

    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'].copy(),
    }
    n = int(len(kernel)**0.5)
    
    assert n%2 == 1, "kernel should have odd length!" # kernel expected to be odd

    center = (n-1)/2 #kernel guaranteed to be odd, this is the index of the center element of the kernel
    
    for y in range(image['height']):
        for x in range(image['width']):
            c = 0
            for i in range(n): # row
                for j in range(n): # column
                    c += kernel[i*n+j] * get_cpixel(image,x+j-center, y+i-center)
                    # the terms j - center and i - center offset from the center pixel to get the pixels around it
                    """
                    if c != 0:
                        print("x,y =",(x,y))
                        print("i,j =", (i,j))
                        print(c)
                    """
            set_pixel(result,x,y,c)
            """
            c = 0
            for i in range(n):
                for j in range(n):
                    c += kernel[i][j] * get_cpixel(image,x+i-center, y+j-center)
                    if c != 0:
                        print("x,y =",(x,y))
                        print("i,j =", (i,j))
                        print(c)
            set_pixel(result,x,y,c)
            """
    return result


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'].copy(),
    }
    
    for y in range(image['height']):
        for x in range(image['width']):
            if get_pixel(image,x,y) < 0:
                set_pixel(result,x,y,0)
            if get_pixel(image,x,y) > 255:
                set_pixel(result,x,y,255)
            set_pixel(result,x,y, round(get_pixel(result,x,y)))
    
    return result

# FILTERS
def generate_blur_kernel(n):
    # helper function for generating kernels for blurring
    assert n%2 == 1, "kernel should have odd length!"
    kernel = []
    value = 1 / (n**2)
    for i in range(n**2):
        kernel.append(value)
    return kernel

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    
    # helper function defined above

    # then compute the correlation of the input image with that kernel
    correlated_image = correlate(image, generate_blur_kernel(n))

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(correlated_image)
    
def sharpened(image, n):
    kernel = generate_blur_kernel(n)
    center = (n-1)/2
    # modifying kernel to correlate with one kernel
    for y in range(n):
        for x in range(n):
            kernel[y*n + x] *= -1
            if y == center and x == center:
                kernel[y*n+x] += 2
    correlated_image = correlate(image, kernel)
    return round_and_clip_image(correlated_image)

def edges(image):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'].copy()
    }
    Kx = [
        -1,0,1,
        -2,0,2,
        -1,0,1
    ]
    Ky = [
        -1,-2,-1,
        0,0,0,
        1,2,1
    ]
    xCorrelated = correlate(image,Kx)
    yCorrelated = correlate(image,Ky)

    for y in range(image['height']):
        for x in range(image['width']):
            set_pixel(result,x,y,round(math.sqrt(get_pixel(xCorrelated,x,y)**2 + get_pixel(yCorrelated,x,y)**2)))
    
    return round_and_clip_image(result)

def split(image):
    red = {
            'height': image['height'],
            'width': image['width'],
            'pixels': []
        }
    green = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []
    }
    blue = {
        'height': image['height'],
        'width': image['width'],
        'pixels': []
    }
    for tup in image['pixels']:
        red['pixels'].append(tup[0])
        green['pixels'].append(tup[1])
        blue['pixels'].append(tup[2])
    
    return (red,green,blue)

def combine(tup):
    r,g,b = tup
    assert r['height'] == g['height'] == b['height']
    assert r['width'] == g['width'] == b['width']

    rV = {
        'height': r['height'],
        'width': r['width'],
        'pixels':[]
    }
    
    for i in range(rV['height']*rV['width']):
        rV['pixels'].append((r['pixels'][i], g['pixels'][i], b['pixels'][i]))

    return rV

def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color_filter(image):
        r,g,b = split(image)
        red = filt(r)
        green = filt(g)
        blue = filt(b)
        return combine((red,green,blue))
    
    return color_filter

def make_blur_filter(n):
    
    def blur_filter(image):
        return blurred(image,n)
    
    return blur_filter


def make_sharpen_filter(n):
    
    def sharpen_filter(image):
        return sharpened(image,n)

    return sharpen_filter


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def cascade(image):
        rV = image.copy()
        for filt in filters:
            rV = filt(rV)
        return rV
    
    return cascade


# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    rV = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'].copy()
    }
    for i in range(ncols):
        # print(i)
        grey = greyscale_image_from_color_image(rV)
        energy = compute_energy(grey)
        cem = cumulative_energy_map(energy)
        seam = minimum_energy_seam(cem)
        rV = image_without_seam(rV,seam)
    return rV


# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    greyImage = {
        'height': image['height'],
        'width': image['width'],
        'pixels':[]
    }
    for tup in image['pixels']:
        r,g,b = tup
        greyImage['pixels'].append(round(.299*r + .587*g + .114*b))
    
    return greyImage


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)

def find_min(energyList):
    """
    takes a list and returns the index of the minimum value (leftmost if multiple)
    """
    return energyList.index(min(energyList))

def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    cumulativeEnergy = {
        'height': energy['height'],
        'width': energy['width'],
        'pixels':[]
    }
    for i in range(energy['width']):
        # the cumulative energy for the top row is unchanged
        cumulativeEnergy['pixels'].append(energy['pixels'][i])
    
    for y in range(1, energy['height']):
        for x in range(energy['width']):
            left = get_cpixel(cumulativeEnergy,x-1,y-1)
            up = get_cpixel(cumulativeEnergy,x,y-1)
            right = get_cpixel(cumulativeEnergy,x+1,y-1)
            minEnergy = min(left,up,right)
            cumulativeEnergy['pixels'].append(minEnergy+energy['pixels'][y*energy['width']+x])
    
    return cumulativeEnergy


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    seam = []
    h = cem['height']
    w = cem['width']
    lastRow = cem['pixels'][w*(h-1):w*h]
    recentY = h-1
    recentX = find_min(lastRow) # x coordinate of the minimum value
    seam.append(recentY*w+recentX)
    for i in range(h-1):
        left = get_cpixel(cem, recentX-1,recentY-1)
        up = get_cpixel(cem,recentX,recentY-1)
        right = get_cpixel(cem,recentX+1,recentY-1)
        offset = find_min([left,up,right]) #0 if left, 1 if up, 2 if right
        recentY -= 1
        if recentX == 0 and offset == 0: # if we are currently at the left edge of the image, there is no left value even though get_cpixel returns the up value as the left value
            pass
        else:
            recentX += offset-1
        seam.append(recentY*w+recentX)
    
    return seam

def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    rV = {
        'height': image['height'],
        'width': image['width'] - 1
    }
    pixelList = image['pixels'][:]
    for elem in seam:
        pixelList.pop(elem)

    rV['pixels'] = pixelList
    return rV

def ripple(image, n):
    """
    image is the image, n is the maximum number of pixels of offset desired in the ripple
    """
    height = image['height']
    width = image['width']
    newList = []
    for y in range(height):
        recentRow = image['pixels'][width*y: width*(y+1)]
        offset = round(n * math.sin(2 * math.pi * y / 20))
        if offset == 0:
            newList.extend(recentRow)
        elif offset < 0: #move elements in the row to the left
            offset *= -1
            sub1 = recentRow[0:offset]
            sub2 = recentRow[offset:width]
            sub2.extend(sub1)
            newList.extend(sub2)
        elif offset > 0: #move elements in the row to the right
            sub1 = recentRow[0:width-offset]
            sub2 = recentRow[width-offset:width]
            sub2.extend(sub1)
            newList.extend(sub2)
    return {
        'height': image['height'],
        'width': image['width'],
        'pixels': newList
    }

def draw_circle(image,x,y,r,fill):
    """
    circle of radius r centered at x,y drawn with color fill (rgb tuple)
    """
    rV = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:]
    }
    for currentY in range(y-r, y+r+1):
        for currentX in range(x-r, x+r+1):
            if round(math.sqrt((currentY - y)**2 + (currentX - x)**2)) <= r:
                set_pixel(rV,currentX,currentY,fill)
    return rV

def draw_bottom_circle(image,x,y,r,fill):
    rV = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:]
    }
    for currentY in range(y, y+r+1):
        for currentX in range(x-r, x+r+1):
            if round(math.sqrt((currentY - y)**2 + (currentX - x)**2)) <= r:
                set_pixel(rV,currentX,currentY,(255,255,255))
    return rV

def draw_vertical_line(image,x,y,l,fill):
    """
    vertical line starting from x,y and extending down for l pixels
    fill is color of line
    """
    rV = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:]
    }
    for i in range(y, y+l):
        set_pixel(rV,x,i,fill)
    return rV

def draw_horizontal_line(image,x,y,l,fill):
    """
    horizontal line starting from x,y and extending to the right for l pixels
    fill is the color of the line
    """
    rV = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:]
    }
    for i in range(x, x+l):
        set_pixel(rV,i,y,fill)
    return rV

def draw_peen(image,x,y,r,g,l,fill):
    """
    draws a peen (two balls with radius r) and a shaft of length l. x,y is the pixel between the two balls
    fill is the color of the peen
    """
    rV = {
    'height': image['height'],
    'width': image['width'],
    'pixels': image['pixels'][:]
    }
    set_pixel(rV,x,y,fill)
    rV = draw_circle(rV,x-round(0.9*r),y,r,fill)
    rV = draw_circle(rV,x+round(0.9*r),y,r,fill)
    rV = draw_vertical_line(rV,x-g-1,y,l+r,fill)
    rV = draw_vertical_line(rV,x+g+1,y,l+r,fill)
    for j in range(y,y+l+r):
        for i in range(x-g-1,x+g+1):
            set_pixel(rV,i,j,fill)
    rV = draw_circle(rV,x,y+r+l,round(1.2*g),fill)

    rV = draw_vertical_line(rV,x,y+r+l+round(0.6*g),round(0.6*g)+1,(0,0,0))
    rV = draw_horizontal_line(rV,x-g-1,y+r+l - round(math.sqrt((1.2*g)**2-g**2)),2*g+3,(0,0,0))


    return rV

# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_greyscale_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    """
    cat = load_color_image('test_images/cat.png')
    invert_color = color_filter_from_greyscale_filter(inverted)
    save_color_image(invert_color(cat),'cat_invert.png')
    """

    """
    snek = color_filter_from_greyscale_filter(make_blur_filter(9))(load_color_image('test_images/python.png'))
    save_color_image(snek,'python_blur_9.png')

    birb = color_filter_from_greyscale_filter(make_sharpen_filter(7))(load_color_image('test_images/sparrowchick.png'))
    save_color_image(birb,'sparrowchick_sharp_7.png')
    """

    """
    filter1 = color_filter_from_greyscale_filter(edges)
    filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    filt = filter_cascade([filter1, filter1, filter2, filter1])

    frog = filt(load_color_image('test_images/frog.png'))
    save_color_image(frog,"frog_filtered.png")
    """

    """
    twoCats = load_color_image('test_images/twocats.png')
    for i in range(100):
        print(i)
        grey = greyscale_image_from_color_image(twoCats)
        energy = compute_energy(grey)
        cem = cumulative_energy_map(energy)
        seam = minimum_energy_seam(cem)
        twoCats = image_without_seam(twoCats,seam)
    save_color_image(twoCats, 'twocats_seam.png')
    """
    tree = load_color_image('test_images/tree.png')
    print((tree['width'],tree['height']))

    save_color_image(draw_peen(tree, 150,30,15,25,20,(255,255,255)), 'tree_chode.png')
    pass