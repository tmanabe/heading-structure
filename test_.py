#!/usr/bin/env python
# coding: utf-8


from heading_structure import Block
from heading_structure import Headings
from heading_structure import HeadingStructure
from heading_structure import Range
from heading_structure import RangeList
import unittest


class TestRange(unittest.TestCase):

    def test(self):
        d = {
            Range.FROM: 0,
            Range.TO: 999,
            Range.MANDATORY: True,
        }
        r = Range.loadd(d, 999)
        self.assertTrue(isinstance(r, Range))
        self.assertEqual(d, r)

    def test_conversion(self):
        d = {
            Range.FROM: '123',
            Range.TO: '456',
            Range.MANDATORY: None,
        }
        r = Range.loadd(d, 999)
        self.assertEqual(123, r[Range.FROM])
        self.assertEqual(456, r[Range.TO])
        self.assertEqual(False, r[Range.MANDATORY])

    def test_default(self):
        d = {}
        r = Range.loadd(d, 999)
        self.assertEqual(0, r[Range.FROM])
        self.assertEqual(999, r[Range.TO])
        self.assertEqual(True, r[Range.MANDATORY])

    def test_lower_bound(self):
        d = {
            Range.FROM: -1,
        }
        r = Range.loadd(d, 999)
        self.assertEqual(0, r[Range.FROM])

    def test_upper_bound(self):
        d = {
            Range.TO: 1000,
        }
        r = Range.loadd(d, 999)
        self.assertEqual(999, r[Range.TO])

    def test_validation(self):
        d = {
            Range.FROM: 456,
            Range.TO: 123,
        }
        r = Range.loadd(d, 999)
        self.assertEqual(456, r[Range.FROM])
        self.assertEqual(456, r[Range.TO])

    def test_metadata(self):
        d = {
            'metaKey': 'metaValue',
        }
        r = Range.loadd(d, 999)
        self.assertTrue('metaKey' in r)
        self.assertEqual('metaValue', r['metaKey'])


class TestRangeList(unittest.TestCase):

    def test(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 123,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 456,
            Range.TO: 789,
            Range.MANDATORY: True,
        }
        rl = RangeList.loadl([d0, d1], 999)
        self.assertTrue(isinstance(rl, RangeList))
        self.assertEqual([d0, d1], rl)

    def test__insert(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 123,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 456,
            Range.TO: 789,
            Range.MANDATORY: True,
        }
        d2 = {
            Range.FROM: 456,
            Range.TO: 999,
            Range.MANDATORY: True,
        }
        d3 = {
            Range.FROM: 789,
            Range.TO: 999,
            Range.MANDATORY: True,
        }
        rl = RangeList.loadl([], 999)
        for d in (d0, d3, d1, d2):
            rl._insert(0, Range.loadd(d, 999))
        self.assertEqual([d0, d2, d1, d3], rl)

    def test_sort(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 123,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 456,
            Range.TO: 999,
            Range.MANDATORY: True,
        }
        rl = RangeList.loadl([d1, d0], 999)
        self.assertEqual([d0, d1], rl)

    def test_inclusion(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 123,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 0,
            Range.TO: 456,
            Range.MANDATORY: True,
        }
        d2 = {
            Range.FROM: 123,
            Range.TO: 456,
            Range.MANDATORY: True,
        }
        rl = RangeList.loadl([d0, d1, d2], 999)
        self.assertEqual([d1], rl)

    def test_inclusion_tf(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 789,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 123,
            Range.TO: 456,
            Range.MANDATORY: False,
        }
        rl = RangeList.loadl([d0, d1], 999)
        self.assertEqual([d0], rl)

    def test_inclusion_ft(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 789,
            Range.MANDATORY: False,
        }
        d1 = {
            Range.FROM: 123,
            Range.TO: 456,
            Range.MANDATORY: True,
        }
        rl = RangeList.loadl([d0, d1], 999)
        self.assertEqual([
            {Range.FROM: 0, Range.TO: 123, Range.MANDATORY: False},
            d1,
            {Range.FROM: 456, Range.TO: 789, Range.MANDATORY: False},
        ], rl)

    def test_overlap(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 456,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 123,
            Range.TO: 789,
            Range.MANDATORY: True,
        }
        d2 = {
            Range.FROM: 456,
            Range.TO: 999,
            Range.MANDATORY: True,
        }
        rl = RangeList.loadl([d0, d1, d2], 999)
        self.assertEqual([
            {
                Range.FROM: 0,
                Range.TO: 999,
                Range.MANDATORY: True,
            },
        ], rl)

    def test_overlap_tf(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 456,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 123,
            Range.TO: 789,
            Range.MANDATORY: False,
        }
        rl = RangeList.loadl([d0, d1], 999)
        self.assertEqual([
            d0,
            {
                Range.FROM: 456,
                Range.TO: 789,
                Range.MANDATORY: False,
            },
        ], rl)

    def test_overlap_ft(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 456,
            Range.MANDATORY: False,
        }
        d1 = {
            Range.FROM: 123,
            Range.TO: 789,
            Range.MANDATORY: True,
        }
        rl = RangeList.loadl([d0, d1], 999)
        self.assertEqual([
            {
                Range.FROM: 0,
                Range.TO: 123,
                Range.MANDATORY: False,
            },
            d1,
        ], rl)

    def test_empty(self):
        d = {
            Range.FROM: 123,
            Range.TO: 123,
            Range.MANDATORY: True,
        }
        rl = RangeList.loadl([d], 999)
        self.assertEqual([], rl)


class TestHeadings(unittest.TestCase):
    def test(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 123,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 456,
            Range.TO: 789,
            Range.MANDATORY: True,
        }
        h = Headings.loadl([[d0, d1]], 999)
        self.assertTrue(isinstance(h, Headings))
        self.assertEqual([[d0, d1]], h)


class TestBlock(unittest.TestCase):
    def test(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 123,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 123,
            Range.TO: 456,
            Range.MANDATORY: False,
        }
        d2 = {
            Range.FROM: 456,
            Range.TO: 789,
            Range.MANDATORY: True,
        }
        b = Block.loadd({
            Block.CHILDREN: [],
            Block.CONTENTS: [d0, d1, d2],
            Block.HEADINGS: [[d0, d2]],
        }, 999)
        self.assertTrue(isinstance(b, Block))
        self.assertEqual([], b[Block.CHILDREN])
        self.assertEqual([d0, d1, d2], b[Block.CONTENTS])
        self.assertEqual([[d0, d2]], b[Block.HEADINGS])

    def test_default(self):
        b = Block.loadd({}, 999)
        self.assertEqual([], b[Block.CHILDREN])
        self.assertEqual([], b[Block.CONTENTS])
        self.assertEqual([], b[Block.HEADINGS])

    def test_nest(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 123,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 123,
            Range.TO: 456,
            Range.MANDATORY: False,
        }
        d2 = {
            Range.FROM: 456,
            Range.TO: 789,
            Range.MANDATORY: True,
        }
        b = Block.loadd({
            Block.CHILDREN: [
                {
                    Block.CHILDREN: [],
                    Block.CONTENTS: [d1, d2],
                    Block.HEADINGS: [[d2]],
                }
            ],
            Block.CONTENTS: [d0, d1, d2],
            Block.HEADINGS: [[d0]],
        }, 999)
        self.assertTrue(isinstance(b[Block.CHILDREN][0], Block))
        self.assertEqual([], b[Block.CHILDREN][0][Block.CHILDREN])
        self.assertEqual([d1, d2], b[Block.CHILDREN][0][Block.CONTENTS])
        self.assertEqual([[d2]], b[Block.CHILDREN][0][Block.HEADINGS])

    def test_metadata(self):
        d = {
            'metaKey': 'metaValue',
        }
        b = Block.loadd(d, 999)
        self.assertTrue('metaKey' in b)
        self.assertEqual('metaValue', b['metaKey'])


class TestHeadingStructure(unittest.TestCase):
    def test(self):
        d0 = {
            Range.FROM: 0,
            Range.TO: 123,
            Range.MANDATORY: True,
        }
        d1 = {
            Range.FROM: 123,
            Range.TO: 456,
            Range.MANDATORY: False,
        }
        d2 = {
            Range.FROM: 456,
            Range.TO: 789,
            Range.MANDATORY: True,
        }
        b = HeadingStructure.loadd({
            Block.CHILDREN: [],
            Block.CONTENTS: [d0, d1, d2],
            Block.HEADINGS: [[d0, d2]],
            HeadingStructure.RAW_STRING: 'x' * 789,
        }, 999)
        self.assertTrue(isinstance(b, HeadingStructure))
        self.assertEqual([], b[Block.CHILDREN])
        self.assertEqual([d0, d1, d2], b[Block.CONTENTS])
        self.assertEqual([[d0, d2]], b[Block.HEADINGS])
        self.assertEqual('x' * 789, b[HeadingStructure.RAW_STRING])

    def test_default(self):
        hs = HeadingStructure.loads('{}')
        self.assertEqual('', hs[HeadingStructure.RAW_STRING])

    def test_load(self):
        with open('example.json') as f:
            HeadingStructure.load(f)

    def test_loads(self):
        with open('example.json') as f:
            HeadingStructure.loads(f.read())


if __name__ == '__main__':
    unittest.main()