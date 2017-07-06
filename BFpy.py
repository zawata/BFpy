#!/usr/bin/python

import sys
import getopt

from Config.Config import *
from binascii import unhexlify

class Singleton(type):
    """
    Singleton Meta-Class
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def __str__(self):
        return "({0},{1})".format(self.char, self.cVal)

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
    size = [0, 0] # Cells on the left and right side, respectively
    L = [0]

    def _append(self):
        self.L.append(0)
        self.size[1] += 1

    def _prepend(self):
        self.L.insert(0, 0)
        self.size[0] += 1
        self.dp += 1

    def data(self):
        return [self.dp, self.L]

    def incD(self, config):
        if int.from_bytes(unhexlify('FF' * config.Cell_Size), byteorder='big') == self.L[self.dp]:
            self.L[self.dp] = 0
        else:
            self.L[self.dp] += 1

    def decD(self, config):
        if self.L[self.dp] == 0:
            self.L[self.dp] = int.from_bytes(unhexlify('FF' * config.Cell_Size), byteorder='big')
        else:
            self.L[self.dp] -= 1

    def incP(self, config):
        self.dp += 1
        if self.dp == len(self.L):
            self._append()

    def decP(self, config):
        self.dp -= 1
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

def problem(num, exitF):
    EList = [
        "Error with Error Function?",
        "Orphaned Right Brace.",
        "Unmatched Left Brace.",
        "No EOC Indicator.",
        "Invalid Character."
    ]
    print("Error {0}: {1}".format(num, EList[num]), end='  ')
    if exitF:
        exit(num)
    else:
        print('Continuing...', end='  ')

def interpret(t, conf):
    Comment_Flag = False
    No_NewLine_Flag = False

    i = 0
    LoopStack = []
    while True:
        try:
            c = t[i]
        except IndexError:
            problem(3,False)
            break
        if conf.Debug_Flag:
            if Comment_Flag or c == '#':
                print(c, end='')
            elif not c in " \n\t":
                print(c, end='  ')
                print(i, end='  ')
        if Comment_Flag:
            if c == '#':
                Comment_Flag = False
                if conf.Debug_Flag:
                    print()
            # if the continue isn't here, then when the comment ends
            # the loop advances into the instruction handler 
            # with the ending comment symbol as the current instruction,
            # putting the interpreter back in comment mode

            # The continue wont go to the bottom
            # of the loop so we need to increment the IP ourselves

            i += 1
            continue
        if not Comment_Flag:
            if c == '+':
                if conf.Debug_Flag:
                    print(*Data().data(), end='  ')
                Data().incD(conf)
            elif c == '-':
                if conf.Debug_Flag:
                    print(*Data().data(), end = '  ')
                Data().decD(conf)

            elif c == '>':
                if conf.Debug_Flag:
                    print(*Data().data(), end = '  ')
                Data().incP(conf)

            elif c == '<':
                if conf.Debug_Flag:
                    print(*Data().data(), end = '  ')
                Data().decP(conf)

            elif c == '.':
                if conf.Debug_Flag:
                    print(*Data().data(), end = '  ')
                Data().write()

            elif c == ',':
                if conf.Debug_Flag:
                    print(*Data().data(), end = '  ')
                Data().read()

            elif c == '[':
                if conf.Debug_Flag:
                    print(*Data().data(), end = '  ')
                if len(LoopStack) == 0:
                    LoopStack.append(i)
                elif LoopStack[-1] != i:
                    LoopStack.append(i)
                if not Data().nonzero():
                    LoopStack.pop()
                    tempLoopStack = []
                    while True:
                        i += 1
                        if t[i] == '[':
                            tempLoopStack.append('[')
                        elif t[i] == ']':
                            if len(tempLoopStack) == 0:
                                if conf.Debug_Flag:
                                    print("jumping to {0}".format(i), end=' ')
                                break
                            else:
                                tempLoopStack.pop()
            elif c == ']':
                if conf.Debug_Flag:
                    print(*Data().data(), end = '  ')
                if len(LoopStack) == 0:
                    problem(1, True)
                #elif Data().nonzero():
                else:
                    i = LoopStack[len(LoopStack)-1] - 1

            elif c == '!':
                if conf.Debug_Flag:
                    print("End")
                if len(LoopStack) != 0:
                    problem(2, True)
                else:
                    break

            elif c == '#':
                No_NewLine_Flag = True
                Comment_Flag = True

            elif c in " \n\t" :
                if conf.Debug_Flag:
                    No_NewLine_Flag = True

            else:
                if conf.Debug_Flag:
                    print(*Data().data(), end = '  ')
                    problem(4, False)
                #More in the future

        if not No_NewLine_Flag and conf.Debug_Flag:
            print()
            No_NewLine_Flag = False
        if conf.Debug_Flag:
            No_NewLine_Flag = False
        i += 1

def help():
    print('BFpy.py [-d] <inputfile>')
    print(' -h, --help       This Help Screen')
    print(' -i, --input      Input File')
    print(' -d, --Debug      Debug Mode')

def main(argv):
    Execution_Flag = False

    inputfile = ''
    con = Config()

    iargs = [
        (
            ("h", "help"),
            ("-h", "--help")),
        (
            ("i:", "input="),
            ("-i", "--input")),
        (
            ("d", "debug"),
            ("-d", "--debug"))
    ]

    try:
        opts, args = getopt.getopt(
                argv,
                ''.join([x[0][0] for x in iargs]), # first member of every tuple in the list, joined into a string
                [x[0][1] for x in iargs])          # second member of every tuple in the list, kept as a list
    except getopt.GetoptError:
        print('BFpy.py [-d] -i:<inputfile>')
        sys.exit(2)

    for opt, arg in opts:
        if opt in iargs[0][1]:  #help
            help()
            sys.exit(0)
        elif opt in iargs[1][1]: #input
            inputfile = arg
        elif opt in iargs[2][1]: #debug
            con.Debug_Flag = True

    if inputfile:
        with open(inputfile) as file:
            interpret(file.read().replace('\n', ''), con)
    else:
        help()
        sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
    print(ioShim().Print())
