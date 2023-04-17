from re2 import RegExp
from re2 import readUtf8

import unittest

class TestSubstring(unittest.TestCase):
    def test_null_pattern(self):
        re = RegExp('')
        g = re.search('abcd')
        self.assertEqual(g, {0: [0, 0]})

    def test_null_pattern_and_string(self):
        re = RegExp('')
        g = re.search('')
        self.assertEqual(g, {0: [0, 0]})

    def test_substring(self):
        re = RegExp('bcd')
        g = re.search('abcde')
        self.assertEqual(g, {0: [1, 4]})

    def test_fullmatch(self):
        re = RegExp('abcdefg')
        g = re.search('abcdefg')
        self.assertEqual(g, {0: [0, 7]})


class TestGroup(unittest.TestCase):
    def test_simple_group(self):
        re = RegExp('(ab)')
        g = re.search('AAAabBBB')
        self.assertEqual(g, {0: [3, 5], 1: [3, 5]})

    def test_multi_group(self):
        re = RegExp('(ab)+(cd)+')
        g = re.search('gggababcdef')
        self.assertEqual(g, {0: [3, 9], 1: [3, 5], 2: [7, 9]})

    def test_embeded_group(self):
        re = RegExp('((ab)(cd))')
        g = re.search('gggababcdef')
        self.assertEqual(g, {0: [5, 9], 1: [5, 9], 2: [5, 7], 3: [7, 9]})


class TestRepeat(unittest.TestCase):
    def test_star(self):
        re = RegExp('(AB)*')
        g = re.search('ababABABcd')
        self.assertDictEqual(g, {0: [0, 0]})

    def test_star2(self):
        re = RegExp('(AB)*')
        g = re.search('ABABcd')
        self.assertDictEqual(g, {0: [0, 4], 1: [0, 2]})

    def test_star_nongreedy(self):
        re = RegExp('(AB)*?')
        g = re.search('ABABcd')
        self.assertDictEqual(g, {0: [0, 0]})

    def test_plus(self):
        re = RegExp('(ab)+')
        g = re.search('abababc')
        self.assertDictEqual(g, {0: [0, 6], 1: [0, 2]})

    def test_plus_nongreedy(self):
        re = RegExp('(ab)+?')
        g = re.search('abababc')
        self.assertDictEqual(g, {0: [0, 2], 1: [0, 2]})

    def test_quest(self):
        re = RegExp('(a?)b')
        g = re.search('ab')
        self.assertDictEqual(g, {0: [0, 2], 1: [0, 1]})

    def test_quest_nongreedy(self):
        re = RegExp('(a??)b')
        g = re.search('ab')
        self.assertDictEqual(g, {0: [0, 2], 1: [0, 1]})

    def test_loop(self):
        re = RegExp('(a?)*')
        g = re.search('aaaa')
        self.assertDictEqual(g, {0: [0, 4], 1:[0, 1]})

    def test_loop2(self):
        re = RegExp('(a??)*')
        g = re.search('a')
        self.assertDictEqual(g, {0: [0, 0], 1: [0, 0]})

    def test_deletion(self):
        re = RegExp('ab{0}cd')
        g = re.search('abcd')
        self.assertIsNone(g)

    def test_single_repeat(self):
        re = RegExp('ab{1}cd')
        g = re.search('abcd')
        self.assertEqual(g, {0: [0, 4]})

    def test_multi_repeats(self):
        re = RegExp('ab{3}cd')
        g = re.search('abbbcd')
        self.assertEqual(g, {0: [0, 6]})

    def test_multi_repeats2(self):
        re = RegExp('ab{3,5}cd')
        g = re.search('abbcd')
        self.assertIsNone(g)

    def test_multi_repeats3(self):
        re = RegExp('ab{3,5}cd')
        g = re.search('abbbbcd')
        self.assertEqual(g, {0: [0, 7]})

    def test_multi_repeats4(self):
        re = RegExp('ab{3,5}?cd')
        g = re.search('abbbbcd')
        self.assertEqual(g, {0: [0, 7]})

    def test_multi_repeats5(self):
        re = RegExp('ab{3,5}')
        g = re.search('abbbbb')
        self.assertEqual(g, {0: [0, 6]})

    def test_multi_repeats6(self):
        re = RegExp('ab{3,5}?')
        g = re.search('abbbbb')
        self.assertEqual(g, {0: [0, 4]})

    def test_multi_repeats7(self):
        re = RegExp('ab{3,}')
        g = re.search('abbbbb')
        self.assertEqual(g, {0: [0, 6]})

    def test_multi_repeats8(self):
        re = RegExp('ab{3,}?')
        g = re.search('abbbbb')
        self.assertEqual(g, {0: [0, 4]})

    def test_infinite_repeats(self):
        re = RegExp('ab{3,}cd')
        g = re.search('abbbbbbbcd')
        self.assertEqual(g, {0: [0, 10]})


class TestAlternation(unittest.TestCase):
    def test_simple_alt(self):
        re = RegExp('(ab|c+?d)')
        g = re.search('ccccccccd')
        self.assertEqual(g, {0: [0, 9], 1:[0, 9]})

    def test_multi_alt(self):
        re = RegExp('(ab|cd|ef)+')
        g = re.search('abcdef')
        self.assertEqual(g, {0: [0, 6], 1:[0, 2]})

class TestEscape(unittest.TestCase):
    def test_escape_class(self):
        re = RegExp('(\\w+)\s*(\\d+)')
        g = re.search('hello  1984')
        self.assertEqual(g, {0: [0, 11], 1:[0, 5], 2:[7, 11]})

    def test_escape_alt(self):
        re = RegExp('(a\\|b)')
        g = re.search('a|b')
        self.assertEqual(g, {0: [0, 3], 1:[0, 3]})

    def test_phone_number(self):
        re = RegExp('(\\d+)-(\\d+)-(\\d+)')
        g = re.search('1234-567-890')
        self.assertEqual(g, {0: [0, 12], 1: [0, 4], 2: [5, 8], 3: [9, 12]})

    def test_dot(self):
        re = RegExp('a(.*)(b)')
        g = re.search('abab')
        self.assertEqual(g, {0: [0, 4], 1: [1, 3], 2: [3, 4]})


class TestCharacterClass(unittest.TestCase):
    def test_character_class(self):
        re = RegExp('[a-z\,]+')
        g = re.search('hello, world')
        self.assertEqual(g, {0: [0, 6]})

    def test_negate_class(self):
        re = RegExp('[^a-z]+')
        g = re.search('hello, world')
        self.assertEqual(g, {0: [5, 7]})


class TestUnicode(unittest.TestCase):
    def test_jp(self):
        re = RegExp('い+')
        g = re.search('私はどうすればいいの？')
        self.assertEqual(g, {0: [7, 9]})

    def test_read_utf8(self):
        re = RegExp('\\u6211+')
        g = re.search('我我我我')
        self.assertEqual(g, {0: [0, 4]})


class TestAnchor(unittest.TestCase):
    def test_anchor_begin(self):
        re = RegExp('^abc')
        g = re.search('dabc')
        self.assertIsNone(g)

    def test_anchor_in_middle(self):
        re = RegExp('^aabb^cc')
        g = re.search('aabbcc')
        self.assertIsNone(g)

    def test_anchor_begin2(self):
        re = RegExp('^abc')
        g = re.search('abc')
        self.assertEqual(g, {0: [0, 3]})

    def test_anchor_end(self):
        re = RegExp('abc$')
        g = re.search('abc')
        self.assertEqual(g, {0: [0, 3]})

    def test_anchor_begin_end(self):
        re = RegExp('^abc$')
        g = re.search('abc')
        self.assertEqual(g, {0: [0, 3]})


if __name__ == '__main__':
    unittest.main()