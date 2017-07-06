import sys

##########################
# Implementation Details #
##########################

# Left Cells             = Unbounded
# Right Cells            = Unbounded
# Cell Size              = 64b
# NewLine                = 0x10
# Right Brace Check      = True
# EOF                    = !
# Comments               = #Comment#
# Invalid Characters     = warn
# Spaces, tabs, newlines = allowed

#####################
# Upcoming Features #
#####################

# running from BF Files
# Runtime Input Prompts
# Output Buffer Flushing
# Better General IO Stuff
# Interpreter Re-configurations
# Command Line Options
# Maybe written in a faster language?

test1 = '+++++>>[-]<<[->>+<<]!'

test2='++++++++[> \
       ++++[>++>+ \
       ++>+++>+<< \
       <<-]>+>+>- \
       >>+[<]<-]> \
       >.>---.+++ \
       ++++..+++. \
       >>.<-.<.++ \
       +.------.- \
       -------.>> \
       +.>++.!'

class Singleton(type):
    """
    Singleton Meta-Class
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class loopElem:
    char = '['
    cVal = 0
    def __init__(self, char, cVal):
        self.char = char
        self.cVal = cVal
    def getVal(self):
        return self.cVal

class ioShim(metaclass = Singleton):
    """
    String-based IO class for delayed/controlled printing
    """
    inputBuffer = []
    outputBuffer = []

    def setInput(self, strIn):
        self.input = list(strIn)

    def Read(self):
        c = self.inputBuffer[0]
        del self.inputBuffer[0]
        return ord(c)

    def Write(self, c):
        self.outputBuffer.append(chr(c))

    def Print(self):
        return ''.join(self.outputBuffer)

class Data(metaclass = Singleton):
    """
    Tape Reel Object Class
    Includes commands for simplified implementation.
    """
    dp = 0
    L = [0]

    def _append(self):
        self.L.append(0)

    def _prepend(self):
        self.L.insert(0, 0)
        self.dp += 1

    def _data(self):
        return [self.dp, self.L]

    def incD(self):
        self.L[self.dp]+=1

    def decD(self):
        self.L[self.dp]-=1

    def incP(self):
        self.dp+=1
        if self.dp == len(self.L):
            self._append()

    def decP(self):
        self.dp-=1
        if self.dp == -1:
            self._prepend()

    def write(self):
        #sys.stdout.write(self.L[self.dp])
        ioShim().Write(self.L[self.dp])

    def read(self):
        #self.L[self.dp] = sys.stdin.read(1)
        self.L[self.dp] = ioShim().Read()

    def nonzero(self):
        return self.L[self.dp] != 0

EList = [
        "Error with Error Function?",
        "Orphaned Right Brace.",
        "Unmatched Left Brace.",
        "No EOC Indicator.",
        "Invalid Character."
]
def problem(num, exitF):
    print("Error {0}: {1}".format(num, EList[num]), end='  ')
    if exitF:
        exit(num)
    else:
        print('Continuing...', end='  ')


def interpret(t):
    Comment_Flag = False
    Debug_Flag = True
    No_NewLine_Flag = False

    i = 0
    LoopStack = []
    while True:
        try:
            c = t[i]
        except IndexError:
            problem(3,False)
            break
        if Debug_Flag and not c in " \n\t":
            print(c, end='  ')
        if Comment_Flag:
            if c == '#':
                Comment_Flag = False
            else:
                pass
        if not Comment_Flag:
            if c == '+':
                if Debug_Flag:
                    print(*Data()._data(), end = '  ')
                Data().incD()
            elif c == '-':
                if Debug_Flag:
                    print(*Data()._data(), end = '  ')
                Data().decD()
            elif c == '>':
                if Debug_Flag:
                    print(*Data()._data(), end = '  ')
                Data().incP()
            elif c == '<':
                if Debug_Flag:
                    print(*Data()._data(), end = '  ')
                Data().decP()
            elif c == '.':
                if Debug_Flag:
                    print(*Data()._data(), end = '  ')
                Data().write()
            elif c == ',':
                if Debug_Flag:
                    print(*Data()._data(), end = '  ')
                Data().read()
            elif c == '[':
                if Debug_Flag:
                    print(*Data()._data(), end = '  ')
                LoopStack.append(loopElem('[',i))
                if not Data().nonzero():
                    LoopStack.pop()
                    while(t[i] != ']'):
                        i+= 1
            elif c == ']':
                if Debug_Flag:
                    print(*Data()._data(), end = '  ')
                if len(LoopStack) == 0:
                    problem(1, True)
                elif Data().nonzero():
                    i = LoopStack[len(LoopStack)-1].getVal()
                else:
                    LoopStack.pop()
            elif c == '!':
                if Debug_Flag:
                    print("End")
                if len(LoopStack) != 0:
                    problem(2, True)
                else:
                    break
            elif c == '#':
                Comment_Flag = True
            elif c in " \n\t" :
                if Debug_Flag:
                    No_NewLine_Flag = True
            else:
                if Debug_Flag:
                    print(*Data()._data(), end = '  ')
                    problem(4, False)
                #More in the future
        if not No_NewLine_Flag and Debug_Flag:
            print()
            No_NewLine_Flag = False
        if Debug_Flag:
            No_NewLine_Flag = False
        i += 1


if __name__ == "__main__":
    interpret(test2)
    print(ioShim().Print())
