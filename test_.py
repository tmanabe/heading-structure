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
