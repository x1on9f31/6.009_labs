import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __mul__(self, other):
        return Mul(self, other)

    def __truediv__(self, other):
        return Div(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __rsub__(self, other):
        return Sub(other, self)

    def __rmul__(self, other):
        return Mul(other, self)

    def __rtruediv__(self, other):
        return Div(other, self)
    
    def simplify(self):
        return self


class Var(Symbol):
    pemdas = 100

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'

    def deriv(self,var):
        #var is the variable taking deriv with respect to
        if var == self.name:
            return Num(1) 
        else:
            return Num(0)
    
    def eval(self,mapping):
        return mapping[self.name]


class Num(Symbol):
    pemdas = 100

    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'

    def deriv(self,var):
        return Num(0)

    def eval(self,mapping):
        return self.n

def convert(x):
    if isinstance(x,int):
        return Num(x)
    elif isinstance(x,str):
        return Var(x)
    elif isinstance(x,Symbol):
        return x
    else:
        raise TypeError

def check_zero(arg):
    if isinstance(arg,Num):
        if arg.n == 0:
            return True
    else:
        return False

def check_one(arg):
    if isinstance(arg,Num):
        if arg.n == 1:
            return True
    else:
        return False

class BinOp(Symbol):
    def __init__(self, left, right):
        self.left = convert(left)
        self.right = convert(right)

    def __str__(self):
        l = str(self.left)
        if self.left.pemdas < self.pemdas:
            l = '(' + l + ')'
        r = str(self.right)
        if (self.associative and self.pemdas > self.right.pemdas) or (not self.associative and self.pemdas >= self.right.pemdas):
            r = '(' + r + ')'
        return l + ' ' + self.oper + ' ' + r

    def __repr__(self):
        return self.__class__.__name__ + '(' + repr(self.left) + ', ' + repr(self.right) + ')'

class Add(BinOp):
    associative = True
    oper  = '+'
    pemdas = 0

    def deriv(self,var):
        return Add(self.left.deriv(var), self.right.deriv(var))

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        if isinstance(l,Num) and isinstance(r,Num):
            return Num(l.n+r.n)
        if check_zero(l):
            return r
        if check_zero(r):
            return l
        return Add(l,r)
    
    def eval(self,mapping):
        l = self.left.eval(mapping)
        r = self.right.eval(mapping)
        return l + r



class Sub(BinOp):
    associative = False
    oper = '-'
    pemdas = 0

    def deriv(self,var):
        return Sub(self.left.deriv(var), self.right.deriv(var))

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        if isinstance(l,Num) and isinstance(r,Num):
            return Num(l.n-r.n)
        if check_zero(r):
            return l
        return Sub(l,r)
    
    def eval(self,mapping):
        l = self.left.eval(mapping)
        r = self.right.eval(mapping)
        return l - r
    

class Mul(BinOp):
    associative = True
    oper = '*'
    pemdas = 1

    def deriv(self,var):
        return Add(Mul(self.left, self.right.deriv(var)), Mul(self.right, self.left.deriv(var)))

    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        if isinstance(l,Num) and isinstance(r,Num):
            return Num(l.n*r.n)
        if check_zero(l):
            return Num(0)
        if check_zero(r):
            return Num(0)
        if check_one(l):
            return r
        if check_one(r):
            return l
        return Mul(l,r)
    
    def eval(self,mapping):
        l = self.left.eval(mapping)
        r = self.right.eval(mapping)
        return l * r
    


class Div(BinOp):
    associative = False
    oper = '/'
    pemdas = 1

    def deriv(self,var):
        return Div(Sub(Mul(self.right, self.left.deriv(var)), Mul(self.left, self.right.deriv(var))), Mul(self.right, self.right))
    
    def simplify(self):
        l = self.left.simplify()
        r = self.right.simplify()
        if isinstance(l,Num) and isinstance(r,Num):
            return Num(l.n/r.n)
        if check_zero(l):
            return Num(0)
        if check_one(r):
            return l
        return Div(l,r)

    def eval(self,mapping):
        l = self.left.eval(mapping)
        r = self.right.eval(mapping)
        return l / r
    
def tokenize(source):
    x = source.replace('(', ' ( ')
    x = x.replace(')', ' ) ')
    return x.split()

def parse(tokens):
    find_op = {
        '+': Add,
        '-': Sub,
        '*': Mul,
        '/':Div
    }
    def parse_expression(index):
        current = tokens[index]
        if current.isdigit() or (current[1:].isdigit() and current[0] == '-'): # is a number
            return Num(int(current)), index+1
        elif current != '(' and current != ')': # is a variable
            return Var(current), index+1
        else: # is opening parentheses for an expression
            left, index = parse_expression(index+1)
            oper = find_op[tokens[index]]
            right, index = parse_expression(index+1)
            return oper(left, right), index+1
    
    parsed_expression, next_index = parse_expression(0)
    return parse_expression(0)[0]

def sym(input):
    return parse(tokenize(input))

if __name__ == '__main__':
    #doctest.testmod()
    x = Mul('x','y')
    y = Add('a','b')
    print(Sub(x,y))
