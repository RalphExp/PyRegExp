from re2 import RegExp
from re2 import readUtf8


if __name__ == '__main__':
    kanji = '私'
    print(readUtf8(kanji))

    re = RegExp('(ab|c+?d)', debug=True)
    g = re.search('ccccccccd')
    print(g)

    re = RegExp('(a(b*)c(d*e))', debug=True)
    g = re.search('sssabbbbbbcdddef')
    print(g)

    re = RegExp('(ab)*', debug=True)
    g = re.search('ab')
    print(g)

    re = RegExp('(ab)*?', debug=True)
    g = re.search('ab')
    print(g)

    re = RegExp('(ab)+', debug=True)
    g = re.search('abab')
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