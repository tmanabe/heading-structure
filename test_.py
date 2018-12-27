#!/usr/bin/env python
# coding: utf-8


from heading_structure import HeadingStructure
import json
from os import system
from unittest import TestCase


class TestHeadingStructure(TestCase):

    def test_flake8(self):
        self.assertEqual(0, system('flake8 . --ignore=D'))

    def test_read_write(self):
        with open('example.json') as f:
            expect = json.load(f)
        hs = HeadingStructure.read(expect)
        hs.sort()
        hs.validate()
        actual = hs.write()
        assert expect == actual

    def test_flatten(self):
        def heading(axis):
            return '\t'.join(axis.block.get_heading(hs.rawString))

        def contents(axis):
            return '\t'.join(axis.block.get_contents(hs.rawString))

        with open('example.json') as f:
            hs = HeadingStructure.read(json.load(f))
        a = hs.flatten()
        assert 8 == len(a)

        assert heading(a[0]) == 'tmanabe github io Tomohiro Manabe'
        assert contents(a[0]).startswith('badge facebook com')
        assert contents(a[0]).endswith('DBLP GitHub Facebook')
        assert a[0].precedings == []
        assert a[0].preceding_siblings == []
        assert a[0].ancestors == []
        assert a[0].parent is None
        assert a[0].self == a[0]
        assert a[0].children == [a[1], a[2], a[6], a[7]]
        assert a[0].descendants == [a[3], a[4], a[5]]
        assert a[0].following_siblings == []
        assert a[0].followings == []

        assert heading(a[1]) == 'Career Summary'
        assert contents(a[1]).startswith('Career Summary')
        assert contents(a[1]).endswith('Yahoo Japan Corporation')
        assert a[1].precedings == []
        assert a[1].preceding_siblings == []
        assert a[1].ancestors == []
        assert a[1].parent == a[0]
        assert a[1].self == a[1]
        assert a[1].children == []
        assert a[1].descendants == []
        assert a[1].following_siblings == [a[2], a[6], a[7]]
        assert a[1].followings == [a[3], a[4], a[5]]

        assert heading(a[2]) == \
            'Research Interests and Main Publications'

        assert heading(a[3]) == \
            'Logical structure of tree-structured documents'
        assert contents(a[3]).startswith(
            'Logical structure of tree-structured documents')
        assert contents(a[3]).endswith('and poster')
        assert a[3].precedings == [a[1]]
        assert a[3].preceding_siblings == []
        assert a[3].ancestors == [a[0]]
        assert a[3].parent == a[2]
        assert a[3].self == a[3]
        assert a[3].children == []
        assert a[3].descendants == []
        assert a[3].following_siblings == [a[4], a[5]]
        assert a[3].followings == [a[6], a[7]]

        assert heading(a[4]) == \
            'Automatic summarization of structured documents'

        assert heading(a[5]) == 'Block-based web search'

        assert heading(a[6]) == 'Other Activities'

        assert heading(a[7]) == 'Links'
        assert a[7].preceding_siblings == [a[1], a[2], a[6]]
