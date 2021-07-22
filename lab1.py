#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


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

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
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


def save_image(image, filename, mode='PNG'):
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
    #i = load_image('test_images/bluegill.png')
    #newImage = inverted(i)
    #save_image(newImage, "bluegill_inverted.png")
    
    """
    k = [
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0
    ]
    i = load_image("test_images/pigbird.png")
    newImage = correlate(i, k)
    roundedImage = round_and_clip_image(newImage)
    save_image(roundedImage, "pigbird_correlated.png")
    """

    """
    i = load_image('test_images/python.png')
    newImage = sharpened(i, 11)
    save_image(newImage, 'python_sharpened.png')
    """

    """
    i = load_image('test_images/construct.png')
    newImage = edges(i)
    save_image(newImage, 'construct_edges.png')
    """
   
    pass
