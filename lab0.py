# No Imports Allowed!


def backwards(sound):
    rV = {'rate': sound['rate']} # initialize dict
    # filling in dictionary
    rV['left'] = sound['left'][::-1] # iterate over left backwards
    rV['right'] = sound['right'][::-1] # iterate over right backwards
    return rV

def mix(sound1, sound2, p):
    if sound1['rate'] == sound2['rate']: # check that the sampling rates are the same
        rV = {'rate': sound1['rate']} # arbitary choice because both rates are the same
        # initialize lists for right and left
        right = []
        left = []
        for i in range(min(len(sound1['right']), len(sound2['right']))): # if one is longer than the other, use shortest length
            # multiply the values from the original sounds by p and 1-p respectively
            right.append(sound1['right'][i]*p + sound2['right'][i]*(1-p))
            left.append(sound1['left'][i]*p + sound2['left'][i]*(1-p))
        rV['left'] = left
        rV['right'] = right
        return rV
    else: # cannot mix if rates are not the same
        return None


def echo(sound, num_echos, delay, scale):
    rV = {'rate': sound['rate']}
    # making copies of sound lists
    right = sound['right'].copy()
    left = sound['left'].copy()
    sample_delay = round(delay * sound['rate']) # from instructions
    
    for i in range(num_echos * sample_delay): # extend the lists to not cut off any echos
        right.append(0)
        left.append(0)
    
    for i in range(num_echos):
        multiplier = scale**(i+1) # mutliplier decreases for each consecutive echo
        index = 0 # used to access the elements of the original sound
        for j in range((i+1) * sample_delay, (i+1) * sample_delay + len(sound['right'])): 
            #lower bound is the number of times the echo has been delayed multiplied by the delay, upper bound is the former but with the length of the sound added
            right[j] += sound['right'][index] * multiplier
            left[j] += sound['left'][index] * multiplier
            index += 1 # move to the next element of the sound
    
    rV['right'] = right
    rV['left'] = left

    return rV

def pan(sound):
    rV = {'rate': sound['rate']}
    right = sound['right'].copy()
    left = sound['left'].copy()
    N = len(right) # store length of the sound lists
    for i in range(N):
        # edit the copies of each list by scaling the magnitude of the sound by the required amount (from instructions)
        right[i] = right[i] * i / (N-1)
        left[N-1 - i] = left[N-1-i] * i / (N-1)
    rV['right'] = right
    rV['left'] = left
    return rV


def remove_vocals(sound):
    right = []
    left = []
    N = len(sound['right'])
    for i in range(N):
        both = sound['left'][i]-sound['right'][i] # calculate sound['left'][i]-sound['right'][i]
        # fill sound lists with proper values
        right.append(both)
        left.append(both)
    rV['right'] = right
    rV['left'] = left
    return rV

def add_delay(sound):
    N = len(sound['right'])
    right = []
    left = []
    for i in range(int(N/20)):
        right.append(0)
        left.append(0)
    
    for j in range(N):
        right.append(sound['right'][j])
        left.append(sound['left'][j])
    
    return {'rate': sound['rate'], 'right': right, 'left': left}

# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    left = []
    right = []
    for i in range(count):
        frame = f.readframes(1)
        if chan == 2:
            left.append(struct.unpack('<h', frame[:2])[0])
            right.append(struct.unpack('<h', frame[2:])[0])
        else:
            datum = struct.unpack('<h', frame)[0]
            left.append(datum)
            right.append(datum)

    left = [i/(2**15) for i in left]
    right = [i/(2**15) for i in right]

    return {'rate': sr, 'left': left, 'right': right}


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')
    outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))

    out = []
    for l, r in zip(sound['left'], sound['right']):
        l = int(max(-1, min(1, l)) * (2**15-1))
        r = int(max(-1, min(1, r)) * (2**15-1))
        out.append(l)
        out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    hello = load_wav('sounds/hello.wav')

    rickroll = load_wav('rickroll_cut.wav')

    new_rickroll = add_delay(rickroll)

    write_wav(new_rickroll, 'test.wav')
    
    # mystery.wav
    # mystery = load_wav('sounds/mystery.wav')
    # write_wav(backwards(mystery), 'mystery_reversed.wav')

    # mixing
    # synth = load_wav('sounds/synth.wav')
    # water = load_wav('sounds/water.wav')

    # write_wav(mix(synth,water,0.2), 'synth_water_mix.wav')

    # echo
    # chord = load_wav('sounds/chord.wav')
    # write_wav(echo(chord, 5, 0.3, 0.6), 'chord_echo.wav')

    # pan
    # car = load_wav('sounds/car.wav')
    # write_wav(pan(car), 'car_pan.wav')

    # remove vocals
    # coffee = load_wav('sounds/coffee.wav')
    # write_wav(remove_vocals(coffee), 'coffee_karaoke.wav')

    # write_wav(backwards(hello), 'hello_reversed.wav')
