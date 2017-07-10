#!/usr/bin/python

import sys
import queue
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

    def __init__(self):
        self.inputBuffer = queue.Queue()
        self.outputBuffer = queue.Queue()

    def setInput(self, strIn):
        for c in strIn:
            self.inputBuffer.put(c)

    def Read(self, conf):
        if conf.Realtime_Input_Flag:
            c = input('bf> ')[0]
            if c == '':
                c = '\n'
        else:
            c = self.inputBuffer.get()
        if c == '\n':
            return 10
        else:
            return ord(c)

    def Write(self, c, conf):
        if conf.Buffered_Output_Flag:
            self.outputBuffer.put(chr(c))
        else:
            print(chr(c), end='', flush=True)

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
        if config.Cell_Size != -1:
            if int.from_bytes(unhexlify('FF' * config.Cell_Size), byteorder='big') == self.L[self.dp]:
                self.L[self.dp] = 0
                return
        self.L[self.dp] += 1

    def decD(self, config):
        if config.Cell_Size != -1:
            if self.L[self.dp] == 0:
                self.L[self.dp] = int.from_bytes(unhexlify('FF' * config.Cell_Size), byteorder='big')
                return
        self.L[self.dp] -= 1

    def incP(self, config):
        self.dp += 1
        if self.dp == len(self.L):
            self._append()

    def decP(self, config):
        self.dp -= 1
        if self.dp == -1:
            self._prepend()

    def write(self, conf):
        ioShim().Write(self.L[self.dp], conf)

    def read(self, conf):
        self.L[self.dp] = ioShim().Read(conf)
        return self.L[self.dp]

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
    Comment_Flag    = False
    No_NewLine_Flag = False
    BreakPoint_Flag = False

    i = 0
    LoopStack = []
    while True:
        Debug_Info = ['','','','','']
        try:
            c = t[i]
        except IndexError:
            problem(3,False)
            break
        if conf.Debug_Flag:
            if Comment_Flag or c == '#':
                Debug_Info[0] = str(c).rjust(4)
            elif not c in " \n\t":
                Debug_Info[0] = str(c).rjust(4)
            Debug_Info[1] = str(i).rjust(4)
        if Comment_Flag:
            if c == '#':
                Comment_Flag = False
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
                Data().incD(conf)
            elif c == '-':
                Data().decD(conf)
            elif c == '>':
                Data().incP(conf)
            elif c == '<':
                Data().decP(conf)
            elif c == '.':
                if conf.Debug_Flag:
                    Debug_Info[4] = "Print: {}".format(chr(Data().data()[1][Data().data()[0]]))
                else:
                    Data().write(conf)
            elif c == ',':
                if conf.Debug_Flag:
                    Debug_Info[4] = "Reading: {}".format(chr(Data().read(conf)))
                else:
                    Data().read(conf)
            elif c == '[':
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
                                    Debug_Info[4]  = "jumping to {0}".format(i + 1)
                                break
                            else:
                                tempLoopStack.pop()
            elif c == ']':
                if len(LoopStack) == 0:
                    problem(1, True)
                else:
                    i = LoopStack[len(LoopStack)-1] - 1
            elif c == '!':
                if conf.Debug_Flag:
                    Debug_Info[4] = "End"
                if len(LoopStack) != 0:
                    problem(2, True)
                else:
                    break
            elif c == '#':
                No_NewLine_Flag = True
                Comment_Flag = True
            elif c == '%':
                if conf.Debug_Flag:
                    Debug_Info[4] = "Breakpoint"
                    BreakPoint_Flag = True
            elif c in " \n\t" :
                if conf.Debug_Flag:
                    No_NewLine_Flag = True
            else:
                if conf.Debug_Flag:
                    Debug_Info[4] = "Invalid Character"
                    problem(4, False)
                #More in the future

        if not No_NewLine_Flag and conf.Debug_Flag:
            Debug_Info[2] = str(Data().data()[0]).rjust(4)
            Debug_Info[3] = '['+','.join([str(x).rjust(4) for x in Data().data()[1]]) + ']'
            print(*Debug_Info)
            No_NewLine_Flag = False
        if conf.Debug_Flag:
            No_NewLine_Flag = False
        if BreakPoint_Flag:
            BreakPoint_Flag = False
            input('Press Enter to Continue.')
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
            ("-d", "--debug")),
        (
            ("b", "buffer-ouput"),
            ("-b", "--buffer-output"))
        (
            ("r", "realtime-input"),
            ("-r", "--realtime-input"))
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
        #print(opt, arg)
        if opt in iargs[0][1]:  #help
            help()
            sys.exit(0)
        elif opt in iargs[1][1]: #input
            inputfile = arg
        elif opt in iargs[2][1]: #debug
            con.Debug_Flag = True
        elif opt in iargs[3][1]: #Buffer Output
            con.Buffered_Output_Flag = True
        elif opt in iargs[4][1]: #Buffer Input
            con.Realtime_Input_Flag = True

    if inputfile:
        with open(inputfile) as file:
            interpret(file.read().replace('\n', ''), con)
    else:
        help()
        sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
