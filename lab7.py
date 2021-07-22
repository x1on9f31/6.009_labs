# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences


class Trie:
    def __init__(self, key_type):
        self.value = None
        self.key_type = key_type
        self.children = {}


    def __setitem__(self, key, value):
        """
        Add a key with the given value to the trie, or reassign the associated
        value if it is already present in the trie.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is of
        the wrong type.
        """
        if type(key) != self.key_type:
            raise TypeError

        if len(key) == 1:
            if key in self.children:
                self.children[key].value = value
            else:
                self.children[key] = Trie(self.key_type)
                self.children[key].value = value
        else:
            if key[:1] in self.children:
                self.children[key[:1]][key[1:]] = value
            else:
                self.children[key[:1]] = Trie(self.key_type)
                self.children[key[:1]][key[1:]] = value



    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        >>> t = Trie(str)
        >>> t['bark'] = ':)'
        >>> t['bark']
        ':)'
        """
        if type(key) != self.key_type:
            raise TypeError
        if len(key) == 1:
            if key in self.children:
                rV = self.children[key].value
                if rV == None:
                    raise KeyError
                return rV
            else:
                raise KeyError
        else:
            if key[:1] in self.children:
                return self.children[key[:1]][key[1:]]
            else:
                raise KeyError

    def __delitem__(self, key):
        """
        Delete the given key from the trie if it exists. If the given key is not in
        the trie, raise a KeyError.  If the given key is of the wrong type,
        raise a TypeError.
        >>> t = Trie(str)
        >>> t['bark'] = ':)'
        >>> del t['bark']
        >>> 'bark' in t
        False
        """
        if type(key) != self.key_type:
            raise TypeError
        
        if key in self:
            self.__setitem__(key,None)
        else:
            raise KeyError

    def __contains__(self, key):
        """
        Is key a key in the trie? return True or False.
        >>> t = Trie(str)
        >>> t['bark'] = 'bonk'
        >>> 'bark' in t
        True
        >>> t = Trie(str)
        >>> 'hello' in t
        False
        """
        #print('contain go brr')
        try:
            temp = self.__getitem__(key)
            return True
        except:
            False

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this trie and
        its children.  Must be a generator!
        """
        for key,subtrie in self.children.items():
            if subtrie.value != None:
                yield (key,subtrie.value)
        for key,subtrie in self.children.items():
            for child_key,child_value in subtrie:
                yield (key+child_key,child_value)


def make_word_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    words in the text, and whose values are the number of times the associated
    word appears in the text
    >>> list(make_word_trie('hello there'))
    [('hello', 1), ('there', 1)]
    """
    rV = Trie(str)
    seen = set()
    strings = tokenize_sentences(text)
    for sentence in strings:
        for word in sentence.split():
            if word in seen:
                rV[word] += 1
            else:
                rV[word] = 1
            seen.add(word)
    return rV

def make_phrase_trie(text):
    """
    Given a piece of text as a single string, create a Trie whose keys are the
    sentences in the text (as tuples of individual words) and whose values are
    the number of times the associated sentence appears in the text.
    """
    rV = Trie(tuple)
    strings = tokenize_sentences(text)
    for sentence in strings:
        key = tuple(sentence.split())
        if key in rV:
            rV[key] += 1
        else:
            rV[key] = 1
    return rV

def autocomplete(trie, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is of an inappropriate type for the
    trie.
    >>> t = make_word_trie('bat bat bark bar')
    >>> autocomplete(t,'ba',1)
    ['bat']
    >>> t = make_word_trie('bat bat bark bark bark bar')
    >>> autocomplete(t,'ba',2)
    ['bat', 'bark']
    """
    if trie == None:
        return []
    if type(prefix) != trie.key_type:
        raise TypeError

    if max_count == 0:
        return []

    search = prefix
    next_trie = trie
    while len(search) > 0:
        try:
            next_trie = next_trie.children[search[:1]]
        except:
            return []
        search = search[1:]
    
    temp = [(prefix + x[0],x[1]) for x in next_trie]

    if prefix in trie:
        temp.append((prefix,trie[prefix]))

    if not max_count:
        return [tup[0] for tup in temp]
    else:
        freq_sorted = sorted(temp, key = lambda x: x[1])

        if len(freq_sorted) <= max_count:
            return [tup[0] for tup in freq_sorted]
        else:
            return [tup[0] for tup in freq_sorted[(-1 * max_count):]]
        


def autocorrect(trie, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    >>> t = make_word_trie('the cat in the hat')
    >>> autocorrect(t,'at')
    ['hat', 'cat']
    """
    def edit(prefix):
        letters = 'abcdefghijklmnopqrstuvwxyz'
        for j in range(len(prefix)+1):
            yield prefix[:j] + prefix[j+1:] # removing a letter
            for i in range(26):
                yield prefix[:j] + letters[i] + prefix[j:] # adding a letter
                yield prefix[:j] + letters[i] + prefix[j+1:] #substituting a letter
        for i in range(len(prefix)-1):
            yield prefix[:i]+prefix[i+1]+prefix[i]+prefix[i+2:] #swapping letters

    """
    def auto_with_freq(trie, prefix):
        if trie == None:
            return []
        if type(prefix) != trie.key_type:
            raise TypeError
        search = prefix
        next_trie = trie
        while len(search) > 0:
            try:
                next_trie = next_trie.children[search[:1]]
            except:
                return []
            search = search[1:]
    
        temp = [(prefix + x[0],x[1]) for x in next_trie]

        if prefix in trie:
            temp.append((prefix,trie[prefix]))
        
        return temp
    """
    if max_count == 0:
        return []

    temp = autocomplete(trie,prefix)

    seen = set(temp)

    if max_count and len(temp) >= max_count:
        temp = sorted(temp, key = lambda x: trie[x])
        return temp[-max_count]
    
    extra = []
    for elem in edit(prefix):
        if elem in trie and elem not in seen:
            extra.append(elem)
    
    if not max_count:
        return temp + extra
    else:
        extra = sorted(extra, key = lambda x: trie[x])
        return temp + extra[- (max_count - len(temp)):]
    
    


    """
    if not max_count or c < max_count:
        edited_set = set(edit(prefix))
        edited_set.remove(prefix)
        #print(edited_set)

        temp = []
        for edited in edited_set:
            if edited in trie:
                #print(edited)
                auto = autocomplete(trie,edited)
                #print(auto)
                for x in auto:
                    if x not in seen:
                        temp.append(x)
                        seen.add(x)
        sorted_freq = sorted(temp, key = lambda x: trie[x])
    if not max_count:
        return rV + sorted_freq
    elif c < max_count:
        return rV + sorted_freq[c-max_count:]
    else: # c >= max_count
        rV = sorted(rV, key = lambda x: trie[x])
        return rV[(-1 * max_count):]
    """

                


def word_filter(trie, pattern):
    """
    Return list of (word, freq) for all words in trie that match pattern.
    pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    #print('=====')
    #print(pattern)
    #print(trie.value)
    #print(trie.children)
    
    if pattern == '': #empty pattern
        if trie.value !=  None: # no value
            return [('',trie.value)]
        else:
            return []

    p = pattern[0]

    rV = []
    seen = set()
    
    if p == '*': # any sequence of zero or more characters
        for k,v in word_filter(trie,pattern[1:]): #assume 0 characters in the *
            if (k,v) not in seen:
                rV.append((k,v))
                seen.add((k,v))

    for key,subtrie in trie.children.items():
        #print(key,subtrie.value)
        if p == '*': # any sequence of zero or more characters
            for k,v in word_filter(subtrie,pattern[1:]): # assume 1 character in the *
                if (key+k,v) not in seen:
                    rV.append((key + k,v))
                    seen.add((key+k,v))
            for k,v in word_filter(subtrie,pattern): #assume more characters in the *
                if (key+k,v) not in seen:
                    rV.append((key + k,v))
                    seen.add((key+k,v))
        elif p == '?':
            for k,v in word_filter(subtrie,pattern[1:]): #assume that this particular key is the ? in the word
                if (key+k,v) not in seen:
                    rV.append((key + k,v))
                    seen.add((key+k,v))
        else:
            if key == p:
                for k,v in word_filter(subtrie,pattern[1:]):
                    if (key+k,v) not in seen:
                        rV.append((key + k,v))
                        seen.add((key+k,v))
    
    return rV
        


# you can include test cases of your own in the block below.
if __name__ == '__main__':
    doctest.testmod()
    with open('two_cities.txt',encoding='utf-8') as f:
        text = f.read()
    t = make_word_trie(text)
    print(word_filter(t, 'r?c*t'))
    
    
