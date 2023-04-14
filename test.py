from re2 import RegExp
from re2 import readUtf8

import pdb

if __name__ == '__main__':
    try:
        re = RegExp('a+b*c*', debug=True)
        g = re.search('sabbbbbbcdddef')
        print(g)

        re = RegExp('(ab)+(cd)+', debug=True)
        g = re.search('gggababcdef')
        print(g)

        re = RegExp('(ab|c+?d)', debug=True)
        re.compile()
        g = re.search('ccccccccd')
        print(g)

        re = RegExp('(ab)*', debug=True)
        g = re.search('ab')
        print(g)

        re = RegExp('(ab)*?', debug=True)
        g = re.search('ab')
        print(g)

        re = RegExp('(ab)+?', debug=True)
        g = re.search('abab')
        print(g)

        re = RegExp('a(.*)bc', debug=True)
        g = re.search('abababc')
        print(g)

        re = RegExp('a(.*?)b', debug=True)
        g = re.search('abab')
        print(g)

        re = RegExp('a(.*)(b)', debug=True)
        g = re.search('abab')
        print(g)

        re = RegExp('(a\\|b)', debug=True)
        g = re.search('a|b')
        print(g)

        re = RegExp('(\\d+)-(\\d+)-(\\d+)', debug=True)
        g = re.search('1234-567-890')
        print(g)

        re = RegExp('(\\w+)\s*(\\d+)', debug=True)
        g = re.search('hello  1984')
        print(g)

        re = RegExp('い+', debug=True)
        g = re.search('私はどうすればいいの？')
        print(g)

        re = RegExp('\\u6211+', debug=True)
        g = re.search('我我我我')
        print(g)

        re = RegExp('[a-z\,]+', debug=True)
        g = re.search('hello, world')
        print(g)

        re = RegExp('[^a-z]+', debug=True)
        g = re.search('hello, world')
        print(g)

        # # pdb.set_trace()
        re = RegExp('ab{0}cd', debug=True)
        g = re.search('abcd')
        print(g)

        re = RegExp('ab{0}cd', debug=True)
        g = re.search('acd')
        print(g)

        re = RegExp('ab{1}cd', debug=True)
        g = re.search('abcd')
        print(g)

        re = RegExp('ab{2}cd', debug=True)
        g = re.search('abbcd')
        print(g)

        re = RegExp('ab{3,5}cd', debug=True)
        g = re.search('abbcd')
        print(g)

        re = RegExp('ab{3,5}cd', debug=True)
        g = re.search('abbbbcd')
        print(g)

        re = RegExp('ab{3,}cd', debug=True)
        g = re.search('abbbbcd')
        print(g)

        re = RegExp('ab(cd*){3,5}', debug=True)
        g = re.search('abcdddcddcd')
        print(g)

        re = RegExp('a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*a*', debug=True)
        g = re.search('aab')
        print(g)

        re = RegExp('((ab)*){3,5}', debug=True)
        g = re.search('abcdddcddcd')
        print(g)

        re = RegExp('aaabbbccc$', debug=True)
        g = re.search('aaabbbccc')
        print(g)

        re = RegExp('^aaabbbccc', debug=True)
        g = re.search('daaabbbccc')
        print(g)

        re = RegExp('^aaabbb^ccc', debug=True)
        g = re.search('aaabbbccc')
        print(g)

        re = RegExp('^aaabbbccc$', debug=True)
        g = re.search('aaabbbccc')
        print(g)

        re = RegExp('(a?)*$', debug=True)
        g = re.search('aaaa')
        print(g)

    except Exception:
        import traceback
        print(traceback.format_exc())
