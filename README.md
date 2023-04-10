# PyRegExp
A tiny regular expression engine written in Python3

This module provides a simplified version of regular expression
matching operations of python're library. It supports both 8-bit and 
Unicode strings; both the pattern and the strings being processed 
can contain null bytes and characters outside the US ASCII range.
The special characters are:

*       "."      Matches any character except a newline.

*       "*"      Matches 0 or more (greedy) repetitions of the preceding RE.
                
*       "+"      Matches 1 or more (greedy) repetitions of the preceding RE.

*       "?"      Matches 0 or 1 (greedy) of the preceding RE.

*       *?,+?,?? Non-greedy versions of the previous three special characters.

*       "|"      A|B, creates an RE that will match either A or B.

*       (...)    Matches the RE inside the parentheses.

*       "\\"     Escapes special characters.
    
*       \d       Matches any decimal digit; equivalent to the set [0-9] in
                 bytes patterns or string patterns with the ASCII flag.
                 In string patterns without the ASCII flag, it will match the whole
                 range of Unicode digits.
*       \D       Matches any non-digit character; equivalent to [^\d].
*       \s       Matches any whitespace character; equivalent to [ \t\n\r\f\v] in
                 bytes patterns or string patterns with the ASCII flag.
                 In string patterns without the ASCII flag, it will match the whole
                 range of Unicode whitespace characters.
*       \S       Matches any non-whitespace character; equivalent to [^\s].
*       \w       Matches any alphanumeric character; equivalent to [a-zA-Z0-9_]
                 in bytes patterns or string patterns with the ASCII flag.
                 In string patterns without the ASCII flag, it will match the
                 range of Unicode alphanumeric characters (letters plus digits
                 plus underscore).
                 With LOCALE, it will match the set [0-9_] plus characters defined
                 as letters for the current locale.
*       \W       Matches the complement of \w.
*       \u       Matches unicode characters.
