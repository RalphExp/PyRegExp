#!/usr/bin/python3

r""" This module provides a simplified version of regular expression
matching operations of python're library. It supports both 8-bit and 
Unicode strings; both the pattern and the strings being processed 
can contain null bytes and characters outside the US ASCII range.

The special characters are:
    "."      Matches any character except a newline.
    "*"      Matches 0 or more (greedy) repetitions of the preceding RE.
                Greedy means that it will match as many repetitions as possible.
    "+"      Matches 1 or more (greedy) repetitions of the preceding RE.
    "?"      Matches 0 or 1 (greedy) of the preceding RE.
    *?,      Non-greedy versions of the previous three special characters.
    +?,
    ??,
    {n}      Repeat n times.
    {m,n}    Repeat at least m times, at most n times.
    {n,}     Repeat at least n times.
    [...]    Character class.
    "|"      A|B, creates an RE that will match either A or B.
    (...)    Matches the RE inside the parentheses.
    "\\"     Either escapes special characters or signals a special sequence.

    The special sequences consist of "\\" and a character from the list
    below.  If the ordinary character is not on the list, then the
    resulting RE will match the second character.
        \d       Matches any decimal digit; equivalent to the set [0-9] in
                 bytes patterns or string patterns with the ASCII flag.
                 In string patterns without the ASCII flag, it will match the whole
                 range of Unicode digits.
        \D       Matches any non-digit character; equivalent to [^\d].
        \s       Matches any whitespace character; equivalent to [ \t\n\r\f\v] in
                 bytes patterns or string patterns with the ASCII flag.
                 In string patterns without the ASCII flag, it will match the whole
                 range of Unicode whitespace characters.
        \S       Matches any non-whitespace character; equivalent to [^\s].
        \w       Matches any alphanumeric character; equivalent to [a-zA-Z0-9_]
                 in bytes patterns or string patterns with the ASCII flag.
                 In string patterns without the ASCII flag, it will match the
                 range of Unicode alphanumeric characters (letters plus digits
                 plus underscore).
        \W       Matches the complement of \w.
        \u       Matches unicode characters.

Still testing ...............

For fun only:)
"""

from __future__ import annotations
from collections import OrderedDict
from itertools import count

import sys
import pdb
import copy
import typing as t


def readUtf8(s:str) -> int:
    b = s.encode('utf-8')
    utf8 = 0

    # 1-byte
    if b[0] & 0x80 == 0:
        assert(len(b) == 1)
        utf8 = b[0]
        return utf8
    
    # 2-bytes
    if b[0] & 0xe0 == 0xc0:
        assert(len(b) == 2)
        utf8 = ((b[0] & 0x1f) << 6) + \
                (b[1] & 0x3f)
        return utf8

    # 3-bytes
    if b[0] & 0xf0 == 0xe0:
        assert(len(b) == 3)
        utf8 = ((b[0] & 0x0f) << 12) + \
               ((b[1] & 0x3f) << 6) + \
                (b[2] & 0x3f)
        return utf8
    
    # 4-bytes
    if b[0] & 0xf0 == 0xf0:
        assert(len(b) == 4)
        utf8 = ((b[0] & 0x07) << 24) + \
               ((b[1] & 0x3f) << 16) + \
               ((b[2] & 0x3f) << 8) + \
                (b[3] & 0x3f)
        return utf8

    raise ValueError('Utf-8 error')

def readUnicode(s:str) -> int:
    if len(s[0:4]) != 4:
        raise ValueError(f'Unicode format error: {s}')
    
    u = 0
    for i in range(4):
        u <<= 4
        if not '0' <= s[i] <= '9':
            raise ValueError('Unicode format error')
        u += int(s[i])
        
    return u


class Token(object):
    END = 0
    CHAR = 1
    DOT = 2
    ALTER = 3
    LPAREN = 4
    RPAREN = 5
    STAR = 6
    PLUS = 7
    QUEST = 8
    STAR2 = 9
    PLUS2 = 10
    QUEST2 = 11
    LBRACE = 12
    RBRACE = 13
    LBRACK = 14
    RBRACK = 15
    BACKSLASH = 16
    CARET = 17
    DOLLAR = 18
    HYPHEN = 19
    COMMA = 20
    
    tokenName = ['END', 'CHAR', 'DOT', 'ALTER', 'LPAREN', 
                 'RPAREN', 'STAR', 'PLUS', 'QUEST', 'STAR2', 
                 'PLUS2', 'QUEST2', 'LBRACE', 'RBRACE', 'LBRACK', 
                 'RBRACK', 'BACKSLASH', 'CARET', 'DOLLAR', 
                 'HYPHEN', 'COMMA']

    def __init__(self, type, value=None, pos=None):
        self.type = type
        self.value = value
        self.pos = pos

    def __repr__(self) -> str:
        if self.type == Token.CHAR:
            return f'token: type = {Token.tokenName[self.type]}, val = {chr(self.value)}, pos = {self.pos}'
        elif self.type == Token.BACKSLASH:
            return f'token: type = {Token.tokenName[self.type]}, val = {self.value}, pos = {self.pos}'
        else:
            return f'token: type = {Token.tokenName[self.type]}, pos = {self.pos}'


class Tokenizer(object):
    def __init__(self, pattern, regexp:RegExp):
        self.pat = pattern
        self.regexp = regexp
        self.token = None
        self.index = 0
        self.tokenDict = {
            '|': Token(Token.ALTER),
            '(': Token(Token.LPAREN),
            ')': Token(Token.RPAREN),
            '[': Token(Token.LBRACK),
            ']': Token(Token.RBRACK),
            '{': Token(Token.LBRACE),
            '}': Token(Token.RBRACE),
            '*': Token(Token.STAR),
            '+': Token(Token.PLUS),
            '?': Token(Token.QUEST),
            '^': Token(Token.CARET),  # currently not supported
            '$': Token(Token.DOLLAR), # currently not supported
            '.': Token(Token.DOT),
            '\\': Token(Token.BACKSLASH),
            '-': Token(Token.HYPHEN),
            ',': Token(Token.COMMA)
        }
        self.next()

    def next(self):
        s = self.pat
        if self.index == len(s):
            self.token = Token(Token.END, None, len(s))
            return self.token

        token = self.tokenDict.get(s[self.index], None)
        if token is None:
            token = Token(Token.CHAR, readUtf8(s[self.index]))
            token.pos = self.index
            self.index += 1

        elif Token.STAR <= token.type <= Token.QUEST:
            if self.index + 1 < len(s):
                next = self.tokenDict.get(s[self.index+1], None)
                if next and next.type == Token.QUEST:
                    token.type += 3
                    token.pos = self.index
                    self.index += 2
                else:
                    token.pos = self.index
                    self.index += 1
            else:
                token.pos = self.index
                self.index += 1

        # currently supports \d \D \w \W \s \S \u
        elif token.type == Token.BACKSLASH:
            if self.index + 1 == len(s):
                raise Exception(f'Invalid escape at pos {self.index-1}')
            if s[self.index+1] in ('d', 'D', 'w', 'W', 's', 'S'):
                token = Token(Token.BACKSLASH, s[self.index+1], self.index)
                self.index += 2
            elif s[self.index+1] == 'u':
                token = Token(Token.CHAR, readUnicode(s[self.index+2:self.index+6]), self.index)
                self.index += 6
            else:
                token = Token(Token.CHAR, readUtf8(s[self.index+1]), self.index)
                self.index += 2

        # tokenizer can not tell whether the hyphen is
        # meta character need regexp to tell it.
        elif token.type == Token.HYPHEN and not self.regexp.inrange:
            token.type = Token.CHAR
            token.value = 45 # '-'
            token.pos = self.index
            self.index += 1
        else:
            token.pos = self.index
            self.index += 1

        self.token = token
        return token


class Range(object):
    def __init__(self, ranges:list[tuple]=None, negate=False):
        self.ranges = ranges or []
        self.negate = negate

    def __repr__(self) -> str:
        return str(self.ranges)

    def match(self, c):
        if not self.negate:
            for r in self.ranges:
                if r[0] <= c <= r[1]:
                    return True
            return False
        
        # negation
        for r in self.ranges:
            if r[0] <= c <= r[1]:
                return False
        return True


class NFAArc(object):
    """ NFAArc represent the arcs connecting to the nextN States,
    value is diffent according to different type. if type is 
        1) EPSILON_TYPE, value is None
        2) CHAR_TYPE, value is a single character
        3) CLASS_TYPE, value is a Range object
        4) LPAR_TYPE, value is the group number
        5) RPAR_TYPE, value is the group number
    """
    EPSILON = 0
    CHAR = 1
    CLASS = 2
    LGROUP = 3
    RGROUP = 4
    ANCHOR = 5 # ^ matches the beginning, $ matches the end

    def __init__(self, target:NFAState=None, value:t.Union[int, str, Range]=None, type_:int=0):
        self.type = type_
        self.value = value
        self.target = target


class NFAState(object):
    def __init__(self):
        self.index = None
        self.arcs = []
        self.accept = False

    def appendArc(self, target:NFAState, value, type_):
        self.arcs.append(NFAArc(target, value, type_))

    def appendState(self, target:NFAState):
        self.arcs += target.arcs

    def prependArc(self, target:NFAState, value, type_):
        assert(len(self.arcs) == 1)
        self.arcs.insert(0, NFAArc(target, value, type_))

    def prependState(self, target:NFAState):
        self.arcs = target.arcs + self.arcs

    def copy(self, state2):
        self.arcs = state2.arc
        self.accept = state2.accept
        state2.arc = None

    @staticmethod
    def _closure(state:NFAState, result:list[NFAState], filter:set):
        """ closure return the states can be reach by 
        an ε transition in DFS order.
        """
        
        for arc in state.arcs:
            if arc.type == NFAArc.EPSILON and arc.target not in filter:
                result.append(arc.target)
                filter.add(arc.target)
                NFAState._closure(arc.target, result, filter)
            
    @staticmethod
    def closure(state):
        result = [state]
        filter = {state}
        NFAState._closure(state, result, filter)
        return result
    
    def __hash__(self):
        # assert(self._index is not None)
        return self.index

    def __eq__(self, state:NFAState):
        # __eq__ can be used to simplify the states
        if len(self.arcs) != len(state.arcs):
            return False
        
        for i in range(len(self.arcs)):
            if self.arcs[i] != state.arcs[i]:
                return False
        return True


class NFA(object):
    def __init__(self):
        self.start = None
        self.end = None
        self.nodes = []
        self.groups = 0
    
    def newState(self) -> NFAState:
        state = NFAState()
        # state._index = len(self._nodes)
        # self._nodes.append(state)
        return state
    
    def serialize(self, start, debug:bool=False) -> list[NFAState]:
        """ Serialize the NFS states into a list. """
        todo = [start]

        for i, state in enumerate(todo):
            # set index to the state, index will be used in hashing
            state.index = i
            if debug: 
                print("  State", i, state is self.end and "(final)" or "")
            for arc in state.arcs:
                next = arc.target
                if next in todo:
                    j = todo.index(next)

                    # XXX: there's a trap here, because of the __eq__, 
                    # next may not equal to todo[j], must fix the arc to 
                    # point to the correct state
                    if next.index != todo[j].index:
                        arc.target = todo[j]
                else:
                    j = len(todo)
                    todo.append(next)
                if debug:
                    if arc.type == NFAArc.EPSILON:
                        print("    %s -> %d" % ("ε", j))
                    elif arc.type == NFAArc.LGROUP:
                        print("    ( -> %d" % j)
                    elif arc.type == NFAArc.RGROUP:
                        print("    ) -> %d" % j)
                    elif arc.type == NFAArc.CHAR:
                        print("    %s -> %d" % (chr(arc.value), j))
                    elif arc.type == NFAArc.CLASS:
                        if not arc.value.negate:
                            print("    %s -> %d" % (arc.value, j))
                        else:
                            print("    ! %s -> %d" % (arc.value, j))

        if debug:
            print("")

        return todo

    def star(self, a:NFAState, z:NFAState) -> tuple[NFAState, NFAState]:
        z1 = self.newState()
        a.appendArc(z1, None, NFAArc.EPSILON)
        z.appendArc(a, None, NFAArc.EPSILON)
        z = z1
        return a, z
    
    def star2(self, a:NFAState, z:NFAState) -> tuple[NFAState, NFAState]:
        z1 = self.newState()
        a.prependArc(z1, None, NFAArc.EPSILON)
        z.appendArc(a, None, NFAArc.EPSILON)
        z = z1
        return a, z
    
    def plus(self, a:NFAState, z:NFAState) -> tuple[NFAState, NFAState]:
        z1 = self.newState()
        z.appendArc(a, None, NFAArc.EPSILON)
        z.appendArc(z1, None, NFAArc.EPSILON)
        z = z1
        return a, z
    
    def plus2(self, a:NFAState, z:NFAState) -> tuple[NFAState, NFAState]:
        z1 = self.newState()
        z.appendArc(z1, None, NFAArc.EPSILON)
        z.appendArc(a, None, NFAArc.EPSILON)
        z = z1
        return a, z

    def quest(self, a:NFAState, z:NFAState) -> tuple[NFAState, NFAState]:
        a.appendArc(z, None, NFAArc.EPSILON)
        return a, z

    def quest2(self, a:NFAState, z:NFAState) -> tuple[NFAState, NFAState]:
        a.prependArc(z, None, NFAArc.EPSILON)
        return a, z

    def copyFragment(self, nfaList:list[NFAState], z:NFAState) -> tuple[NFAState, NFAState]:
        
        # FIXME: this is a really bad implementation,
        # To implement {m,n}, just copy the NFA fragment m times
        # and concat them together.

        newList = [self.newState() for i in range(len(nfaList))]

        for i in range(len(nfaList)):
            # copy the arcs but not copy the index
            newList[i].arcs = [NFAArc() for j in range(len(nfaList[i].arcs)) ]
            for j in range(len(nfaList[i].arcs)):
                newList[i].arcs[j].type = nfaList[i].arcs[j].type
                newList[i].arcs[j].value = nfaList[i].arcs[j].value
                newList[i].arcs[j].target = newList[nfaList[i].arcs[j].target.index]

        return (newList[0], newList[z.index])


class Thread(object):
    """ use google re2's BFS matching algorithm
    """
    def __init__(self, id, state, text, pos, groups=None):
        self.id = id
        self.state = state
        self.text = text
        self.pos = pos
        self.groups = groups or {0: [pos, None]}

    def _advance(self, threads:list[Thread]) -> None:
        state = self.state

        if state.accept:
            self.groups = copy.deepcopy(self.groups)
            self.groups[0][1] = self.pos
            threads.append(self)
            return threads

        for arc in state.arcs:
            if arc.type == NFAArc.EPSILON:
                th = self.copy(arc.target)
                th._advance(threads)

            elif arc.type == NFAArc.CHAR and self.pos < len(self.text):
                if arc.value == readUtf8(self.text[self.pos]):
                    th = self.copy(arc.target, pos=self.pos+1)
                    if arc.target.accept:
                        th.groups = copy.deepcopy(self.groups)
                        th.groups[0][1] = self.pos + 1
                    threads.append(th)

            elif arc.type == NFAArc.CLASS and self.pos < len(self.text):
                char = readUtf8(self.text[self.pos])
                if arc.value.match(char):
                    th = self.copy(arc.target, pos=self.pos+1)
                    if arc.target.accept:
                        th.groups = copy.deepcopy(self.groups)
                        th.groups[0][1] = self.pos + 1
                    threads.append(th)

            elif arc.type == NFAArc.LGROUP:
                th = self.copy(arc.target)
                # only record the first occurrence
                if not th.groups.get(arc.value):
                    th.groups = copy.deepcopy(self.groups)
                    th.groups[arc.value] = [self.pos, None]
                th._advance(threads)

            elif arc.type == NFAArc.RGROUP:
                assert(self.groups[arc.value])
                th = self.copy(arc.target)
                if not th.groups[arc.value][1]:
                    th.groups = copy.deepcopy(self.groups)
                    th.groups[arc.value][1] = self.pos
                th._advance(threads)
        return

    def copy(self, state, pos=None) -> Thread:
        th = Thread(self.id, state, self.text, self.pos, self.groups)
        if pos:
            th.pos = pos
        return th

    def advance(self) -> list[NFAState]:
        newThreads = []
        self._advance(newThreads)
        return newThreads
    

class RegExp(object):
    """ A simple regular expression using NFA for matching
    note that is this different from pgen's NFA, we want to 
    make it more intuitive.

    usage:
        re = re2.RegExp(pattern)
        g = re.search(text)
        ...
    """
    def __init__(self, pattern:str, debug:bool=False):
        self.pat = pattern
        self.debug = debug
        self.tokenizer = Tokenizer(self.pat, self)
        self.nfa = NFA()
        self.compiled = False
        self.inrange = False # for hyphen

    def getToken(self):
        # getToken get the current token but not consume it
        return self.tokenizer.token

    def nextToken(self):
        # nextToken consumes the current one and get 
        # the next token from tokenizer
        return self.tokenizer.next()
    
    def getRepeat(self) -> tuple[int, int]:
        # currently the hi value is not allowed to be greater than 100.

        token = self.nextToken() # consume '{'
        if token.type != Token.CHAR or token.value < 48 or token.value > 57:
            raise Exception(f'invalid repeat value {token}')

        def getValue(regexp):
            nonlocal token
            v = 0
            while True:
                v *= 10
                v += token.value - 48
                if v >= 100:
                    raise Exception(f'too much repeat')

                token = regexp.nextToken()
                if token.type != Token.CHAR:
                    return v
                elif token.value < 48 or token.value > 57:
                    raise Exception(f'Invalid repeat value from {token}')
                
        lo = getValue(self)

        # repeat: {n}
        token = self.getToken()
        if token.type == Token.RBRACE:
            self.nextToken() # consume '}'
            return lo, lo
        
        if token.type != Token.COMMA:
            raise Exception(f'Unexpected {token}')
        
        # repeat: {n,}
        token = self.nextToken()
        if token.type == Token.RBRACE:
            self.nextToken()
            return lo, None

        # repeat: {m,n}
        hi = getValue(self)
        if token.type != Token.RBRACE:
            raise Exception(f'Unexpected {token}')
        
        self.nextToken() # consume '}'
        if lo > hi:
            raise Exception(f'Invalid repeat value {(lo, hi)}')
        return lo, hi

    def genRepeat(self, a:NFAState, z:NFAState, 
                  lo:int, hi:int, greedy:bool) -> tuple[NFAState]:
        
        if (lo, hi) == (0, 0):
            return None, None
        if (lo, hi) == (1, 1):
            return a, z
        if (lo, hi, greedy) == (0, 1, True):
            a, z = self.nfa.quest(a, z)
        elif (lo, hi, greedy) == (0, 1, False):
            a, z = self.nfa.quest2(a, z)
        elif (lo, hi, greedy) == (0, None, True):
            a, z = self.nfa.star(a, z)
        elif (lo, hi, greedy) == (0, None, False):
            a, z = self.nfa.star2(a, z)
        elif (lo, hi, greedy) == (1, None, True):
            a, z = self.nfa.plus(a, z)
        elif (lo, hi, greedy) == (1, None, False):
            a, z = self.nfa.plus2(a, z)
        else:
            lst = self.nfa.serialize(a)
            repeatNum = hi-1 if hi is not None else lo-1
            repeats = [(a, z)] + [self.nfa.copyFragment(lst, z) for i in range(repeatNum)]

            if hi is not None:
                for i in range(hi-1):
                    repeats[i][1].appendState(repeats[i+1][0])
                if lo < hi:
                    for i in range(lo, hi):  
                        if greedy:
                            repeats[lo-1][1].appendArc(repeats[i][1], None, NFAArc.EPSILON)
                        else:
                            repeats[lo-1][1].prependArc(repeats[i][1], None, NFAArc.EPSILON)
                z = repeats[hi-1][1]
                assert(z is None or len(z.arcs) == 0)
            else:
                for i in range(lo-2):
                    repeats[i][1].appendState(repeats[i+1][0])
                ah, zh = self.nfa.plus(repeats[lo-1][0], repeats[lo-1][1])
                if greedy:
                    repeats[lo-2][1].appendState(ah)
                else:
                    repeats[lo-2][1].prependState(ah)
                z = zh

            for s in lst: 
                s.index = None # clear the index

        return a, z

    def modify(self, a:NFAState, z:NFAState) -> tuple[NFAState, NFAState]:
        """ handles STAR/QUEST/PLUS,... etc.
        """
 
        # invariant property: len(z.arc) == 0
        # now handle the STAR/PLUS/QUESTION

        token = self.getToken()
        if token.type == Token.STAR:
            self.nextToken()
            a, z = self.nfa.star(a, z)
        elif token.type == Token.STAR2:
            self.nextToken()
            a, z = self.nfa.star2(a, z)
        elif token.type == Token.PLUS:
            self.nextToken()
            a, z = self.nfa.plus(a, z)
        elif token.type == Token.PLUS2:
            self.nextToken()
            a, z = self.nfa.plus2(a, z)
        elif token.type == Token.QUEST:
            self.nextToken()
            a, z = self.nfa.quest(a, z)
        elif token.type == Token.QUEST2:
            self.nextToken()
            a, z = self.nfa.quest2(a, z)
        elif token.type == Token.LBRACE: # '{' repeat
            lo, hi = self.getRepeat()
            greedy = token.type != Token.QUEST
            a, z = self.genRepeat(a, z, lo, hi, greedy)
        else:
            return a, z

        # not allow ++/**/*+/+*/... etc
        idx = self.tokenizer.index
        token = self.getToken()
        if token.type in {Token.PLUS, Token.PLUS2, Token.STAR, 
                          Token.STAR2, Token.QUEST, Token.QUEST2,
                          Token.LBRACK}:
            raise Exception(f'Mutiple repeats are now allow: {idx}')
        
        assert(z is None or len(z.arcs) == 0) 
        return a, z

    def getRange(self) -> Range:
        # e.g [a-zA-Z0-9_]
        self.inrange = True
        self.nextToken() # consume '['
        r = Range()

        token = self.getToken()
        if token.type == Token.CARET:
            r.negate = True
            self.nextToken()

        # if hyphen happens at the begin of the range
        # tolerates it and take it as an character
        token = self.getToken()
        if token.type == Token.HYPHEN:
            token.type = Token.CHAR
            token.value = 45 # '-'

        while True:
            token = self.getToken()
            if token.type != Token.CHAR:
                raise Exception(f'Unexpected token {token}')

            self.nextToken()
            token2 = self.getToken()
            if token2.type == Token.CHAR:
                r.ranges.append((token.value, token.value))
                continue
            elif token2.type == Token.HYPHEN:
                self.nextToken()
                token2 = self.getToken()
                if token2.type == Token.CHAR:
                    if token.value > token2.value:
                        # FIXME: not consider it as an error
                        # just flip the values of the 2 tokens
                        token.value, token2.value = token2.value, token.value
                    r.ranges.append((token.value, token2.value))
                    continue
                elif token2.type == Token.RBRACK:
                    # if hyphen happens at the end of the range
                    # tolerates it and take it as an character
                    r.ranges.append((45, 45)) # '-' character
                    break
            elif token2.type == Token.RBRACK:
                r.ranges.append((token.value, token.value))
                break

        self.inrange = False
        self.nextToken() # consume ']'
        return r

    def concat(self) -> tuple[NFAState, NFAState]:
        aa = None
        zz = None

        while True:
            token = self.getToken()

            if token.type == Token.LPAREN:
                self.nfa.groups += 1
                group = self.nfa.groups
                self.nextToken() # consume '('
                a1, z1 = self.alternate()
                token = self.getToken()
                if token.type != Token.RPAREN:
                    raise Exception('Unmatch parenthesis')

                self.nextToken() # consume ')'
                if a1 is not None:
                    a = self.nfa.newState()
                    z = self.nfa.newState()
                    a.appendArc(a1, group, NFAArc.LGROUP)
                    z1.appendArc(z, group, NFAArc.RGROUP)
                
                # a1 can be None e.g. 'a()b', if this is the case,
                # don't do anything, because () can never capture anything
            elif token.type == Token.CHAR:
                a = self.nfa.newState()
                z = self.nfa.newState()
                a.appendArc(z, token.value, NFAArc.CHAR)
                self.nextToken()

            elif token.type == Token.DOT:
                a = self.nfa.newState()
                z = self.nfa.newState()
                a.appendArc(z, Range([(0, sys.maxunicode)]), NFAArc.CLASS)
                self.nextToken()

            elif token.type == Token.LBRACK:
                r = self.getRange()
                a = self.nfa.newState()
                z = self.nfa.newState()
                a.appendArc(z, r, NFAArc.CLASS)

            elif token.type == Token.BACKSLASH:
                a = self.nfa.newState()
                z = self.nfa.newState()

                if token.value == 'd':
                    a.appendArc(z, Range([(48, 57)]), NFAArc.CLASS)
                elif token.value == 'D':
                    a.appendArc(z, Range([(48, 57)], True), NFAArc.CLASS)
                elif token.value == 'w':
                    a.appendArc(z, Range([(65, 90),(97, 122),(95, 95)]), NFAArc.CLASS)
                elif token.value == 'W':
                    a.appendArc(z, Range([(65, 90),(97, 122),(95, 95)], True), NFAArc.CLASS)
                elif token.value == 's':
                    a.appendArc(z, Range([(9, 13),(32, 32)]), NFAArc.CLASS)
                elif token.value == 'S':
                    a.appendArc(z, Range([(9, 13),(32, 32)], True), NFAArc.CLASS)
                else:
                    # currently not support other type of character-class
                    pass
                self.nextToken()

            else:
                # if we don't capture anything and come across the token
                # which can not be processed, raise an exception.
                if token.type != Token.RPAREN and aa is None:
                    raise Exception(f'unexpected {token}')
                break

            a, z = self.modify(a, z)
            if not a:
                # e.g. (abc){0} is still consider a valid syntax
                continue
            if not aa:
                aa = a
                zz = z
            else:
                zz.appendState(a)
                zz = z

        if zz == aa:
            # Null String!
            return None, None
        return aa, zz

    def alternate(self) -> tuple[NFAState, NFAState]:
        """ alternate split s into different section delimited by '|'
        """
        a, z = self.concat()
        token = self.getToken()
        if token.type != Token.ALTER:
            return a, z
 
        aa = self.nfa.newState()
        zz = self.nfa.newState()

        while True:
            aa.appendArc(a, None, NFAArc.EPSILON)
            z.appendArc(zz, None, NFAArc.EPSILON)

            token = self.getToken()
            if token.type != Token.ALTER:
                break

            while True:
                # if multiple '|' shows up, combine them into one
                self.nextToken()
                if self.getToken().type != Token.ALTER:
                    break

            a, z = self.concat()
            if a is None: # one possible pattern is 'abc|'
                break

        return aa, zz

    def compile(self) -> None:
        if self.compiled:
            return

        s = self.pat
        start, end = self.alternate()
        if self.tokenizer.index != len(s):
            raise Exception(f'Unexpected {self.getToken()}')

        if start is None:
            assert(end is None)
            start = self.nfa.newState()
            end = self.nfa.newState()

        end.accept = True
        self.nfa.start = start
        self.nfa.end = end
        self.nodes = self.nfa.serialize(self.nfa.start, self.debug)
        self.compiled = True

    def addThread(self, text:str, pos:int, gen):
        start = self.nfa.start
        threads = []
        th = Thread(next(gen), start, text, pos, groups=None)
        threads += th.advance()
        return threads

    def search(self, text, pos=0) -> dict:
        if self.compiled == False:
            self.compile()

        threads = OrderedDict()
        gen = count()
        matchThread = None
        matched = False

        while pos <= len(text):
            newThreads = OrderedDict() # result (state, thread)
            matched = False

            for _, thread in threads.items():
                threads = thread.advance()
                for th in threads:
                    if th.state.accept:
                        matchThread = th
                        # all the thread in threads have the same gid
                        # we don't need to advance any more
                        matched = True
                        break
                    
                    if not newThreads.get(th.state):
                        newThreads[th.state] = th
                if matched:
                    # from here on, the rest threads are not considered a
                    # candidate, e.g. in the regular expression A|B, when A
                    # is a correct matching, B is not considered any more
                    break
            
            # try to add new threads at the start state
            if not matchThread:
                threads = self.addThread(text, pos, gen)
                for th in threads:
                    if th.state.accept:
                        matchThread = th
                        # all the thread in threads have the same gid
                        # we don't need to advance any more
                        break
                    if not newThreads.get(th.state):
                        newThreads[th.state] = th
            
            if len(newThreads) == 0 and matchThread:
                break

            threads = newThreads

            # print(f'--- pos {pos} ---')
            # for state, th in threads.items():
            #     print(f'thread id: {th.id}, state: {state.index}')
            # if matchThread is not None:
            #     print(f'match thread: id {matchThread.id}, state: {matchThread.state.index}')
            # print()

            pos += 1

        return matchThread.groups if matchThread is not None else None