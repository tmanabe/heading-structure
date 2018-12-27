#!/usr/bin/env python
# coding: utf-8

import json
import os


class InvalidHeadingStructureException(Exception):
    pass


IHSE = InvalidHeadingStructureException


class Range(object):
    FROM, TO = 'from', 'to'
    MANDATORY = 'mandatory'
    __slots__ = [FROM, TO, MANDATORY]

    @classmethod
    def read(cls, obj):
        if not isinstance(obj, dict):
            raise IHSE("Each range must be a JSON dict: " + obj)
        for k in obj.keys():
            if k not in cls.__slots__:
                raise IHSE("Unknown property of a range: " + k)

        self = cls()
        if cls.FROM in obj:
            setattr(self, cls.FROM, int(obj[cls.FROM]))
        else:
            raise IHSE("A range without %s: %s" % (cls.FROM, obj))
        if cls.TO in obj:
            setattr(self, cls.TO, int(obj[cls.TO]))
        else:
            raise IHSE("A range without %s: %s" % (cls.TO, obj))
        setattr(self, cls.MANDATORY, obj.get(cls.MANDATORY, True))
        return self

    def sort(self):
        return (getattr(self, Range.FROM), getattr(self, Range.TO))

    def to_string(self, raw_string):
        return raw_string[getattr(self, self.FROM):getattr(self, self.TO)]

    def validate(self):
        assert isinstance(getattr(self, self.FROM), int)
        assert isinstance(getattr(self, self.TO), int)
        if getattr(self, self.TO) < getattr(self, self.FROM):
            raise IHSE("Invalid range: %s" % json.dumps(self.write()))
        assert getattr(self, self.MANDATORY) in [False, True]

    def write(self):
        return {
            self.FROM: getattr(self, self.FROM),
            self.TO: getattr(self, self.TO),
            self.MANDATORY: getattr(self, self.MANDATORY),
        }


class RangeList(list):
    @classmethod
    def read(cls, obj):
        if not isinstance(obj, list):
            raise IHSE("Each range list must be a JSON list: " + obj)
        if len(obj) <= 0:
            raise IHSE("Each range list must contain an element: " + obj)

        self = cls()
        for d in obj:
            self.append(Range.read(d))
        return self

    def sort(self):
        super().sort(key=lambda r: r.sort())
        return (getattr(self[0], Range.FROM), getattr(self[-1], Range.TO))

    def to_string(self, raw_string):
        return [r.to_string(raw_string) for r in self]

    def validate(self):
        for r in self:
            assert isinstance(r, Range)
            r.validate()
        for i in range(len(self) - 1):
            if getattr(self[i + 1], Range.FROM) < getattr(self[i], Range.TO):
                raise IHSE("Overlapped ranges: %s" % json.dumps(self.write()))

    def write(self):
        return [r.write() for r in self]


class RangeJag(list):
    @classmethod
    def read(cls, obj):
        if not isinstance(obj, list):
            raise IHSE("Each range jag must be a JSON list: " + obj)
        if len(obj) <= 0:
            raise IHSE("Each range jag must contain an element: " + obj)

        self = cls()
        for l in obj:
            self.append(RangeList.read(l))
        return self

    def sort(self):
        super().sort(key=lambda rl: rl.sort())

    def validate(self):
        for rl in self:
            assert isinstance(rl, RangeList)
            rl.validate()
        for i in range(len(self) - 1):
            if (getattr(self[i + 1][0], Range.FROM) <
                    getattr(self[i][-1], Range.TO)):
                raise IHSE("Overlapped range lists: %s" %
                           json.dumps(self.write()))

    def write(self):
        return [rl.write() for rl in self]


class BlockList(list):
    @classmethod
    def read(cls, obj):
        if not isinstance(obj, list):
            raise IHSE("Each block list must be a JSON list: " + obj)

        self = cls()
        for d in obj:
            self.append(Block.read(d))
        return self

    def sort(self):
        super().sort(key=lambda b: b.sort())

    def validate(self):
        for b in self:
            assert isinstance(b, Block)
            b.validate()

    def write(self):
        return [b.write() for b in self]


class Block(object):
    CHILDREN = 'children'
    CONTENTS = 'contents'
    HEADINGS = 'headings'
    STYLE = 'style'
    __slots__ = [CHILDREN, CONTENTS, HEADINGS, STYLE]

    @classmethod
    def read(cls, obj):
        if not isinstance(obj, dict):
            raise IHSE("Each block must be a JSON dict: " + obj)
        for k in obj.keys():
            if k not in cls.__slots__:
                raise IHSE("Unknown property of a block: " + k)

        self = cls()
        if cls.CHILDREN in obj:
            setattr(self, cls.CHILDREN, BlockList.read(obj[cls.CHILDREN]))
        else:
            setattr(self, cls.CHILDREN, BlockList())
        if cls.CONTENTS in obj:
            setattr(self, cls.CONTENTS, RangeList.read(obj[cls.CONTENTS]))
        else:
            raise IHSE("Each block must contain some contents: " + obj)
        if cls.HEADINGS in obj:
            setattr(self, cls.HEADINGS, RangeJag.read(obj[cls.HEADINGS]))
        else:
            raise IHSE("Each block must include some headings: " + obj)
        setattr(self, cls.STYLE, obj.get(cls.STYLE, None))
        return self

    def get_contents(self, raw_string):
        return getattr(self, self.CONTENTS).to_string(raw_string)

    def flatten(self_block,
                results,
                ancestor_axes=[],
                preceding_axes=None,
                preceding_sibling_axes=[]):
        class Axis(object):
            def __init__(self, self_block):
                self.block = self_block
                self.precedings = []
                self.preceding_siblings = []
                self.ancestors = []
                self.parent = None
                self.self = self
                self.children = []
                self.descendants = []
                self.following_siblings = []
                self.followings = []

        self_axis = Axis(self_block)
        results.append(self_axis)

        if preceding_axes is None:
            preceding_axes = []
        for preceding_axis in preceding_axes:
            if preceding_axis not in (ancestor_axes + preceding_sibling_axes):
                preceding_axis.followings.append(self_axis)
                self_axis.precedings.append(preceding_axis)
        preceding_axes.append(self_axis)

        if 0 < len(ancestor_axes[:-1]):
            for ancestor_axis in ancestor_axes[:-1]:
                ancestor_axis.descendants.append(self_axis)
                self_axis.ancestors.append(ancestor_axis)

        if 0 < len(ancestor_axes):
            ancestor_axes[-1].children.append(self_axis)
            self_axis.parent = ancestor_axes[-1]

        preceding_sibling_axes = []
        for child_block in getattr(self_block, self_block.CHILDREN):
            child_axis = child_block.flatten(results,
                                             ancestor_axes + [self_axis],
                                             preceding_axes,
                                             preceding_sibling_axes)
            for preceding_sibling_axis in preceding_sibling_axes:
                preceding_sibling_axis.following_siblings.append(child_axis)
                child_axis.preceding_siblings.append(preceding_sibling_axis)
            preceding_sibling_axes.append(child_axis)

        return self_axis

    def get_heading(self, raw_string):
        return getattr(self, self.HEADINGS)[0].to_string(raw_string)

    def sort(self):
        getattr(self, self.CHILDREN).sort()
        getattr(self, self.HEADINGS).sort()
        return getattr(self, self.CONTENTS).sort()

    def validate(self):
        assert isinstance(getattr(self, self.CHILDREN), BlockList)
        getattr(self, self.CHILDREN).validate()
        assert isinstance(getattr(self, self.CONTENTS), RangeList)
        getattr(self, self.CONTENTS).validate()
        assert isinstance(getattr(self, self.HEADINGS), RangeJag)
        getattr(self, self.HEADINGS).validate()
        if getattr(self, self.STYLE) is not None:
            assert isinstance(getattr(self, self.STYLE), str)

    def write(self):
        results = {
            self.CHILDREN: getattr(self, self.CHILDREN).write(),
            self.CONTENTS: getattr(self, self.CONTENTS).write(),
            self.HEADINGS: getattr(self, self.HEADINGS).write(),
        }
        if getattr(self, self.STYLE, None) is not None:
            results[self.STYLE] = getattr(self, self.STYLE)
        return results


class HeadingStructure(Block):
    RAW_STRING = 'rawString'
    _URL, BASE_URL = 'URL', 'baseURL'
    __slots__ = Block.__slots__ + [RAW_STRING, _URL, BASE_URL]

    @classmethod
    def read(cls, obj):
        if isinstance(obj, str):
            if os.path.isfile(obj):  # File path
                with open(obj) as f:
                    return cls.read(f)
            else:  # JSON
                return cls.read(json.loads(obj))
        if hasattr(obj, 'read'):  # File-like object
            return cls.read(obj.read())

        # dict
        self = super().read(obj)
        if cls.RAW_STRING in obj:
            setattr(self, cls.RAW_STRING, obj[cls.RAW_STRING])
        else:
            raise IHSE("Root block must contain raw string: " + obj)
        setattr(self, cls._URL, obj.get(cls._URL, None))
        setattr(self, cls.BASE_URL, obj.get(cls.BASE_URL, None))
        return self

    def flatten(self):
        results = []
        super().flatten(results)
        return results

    def write(self):
        results = super().write()
        results[self.RAW_STRING] = getattr(self, self.RAW_STRING)
        if self._URL is not None:
            results[self._URL] = getattr(self, self._URL)
        if self._URL is not None:
            results[self.BASE_URL] = getattr(self, self.BASE_URL)
        return results


if __name__ == '__main__':
    import sys
    sys.stderr.write('Listing JSONs invalid as heading structure...\n')
    for path in sys.argv[1:]:
        if os.path.isfile(path):
            try:
                HeadingStructure.read(path).validate()
            except Exception:
                print(path)
                sys.stderr.write('Invalid: %s\n' % path)
        else:
            sys.stderr.write('File not found: %s\n' % path)
