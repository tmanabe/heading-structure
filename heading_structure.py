#!/usr/bin/env python
# coding: utf-8


import json


class Range(dict):
    FROM, TO = 'from', 'to'
    MANDATORY = 'mandatory'

    @classmethod
    def loadd(cls, d, ubound):
        r = cls()
        r.update(d)
        r[cls.FROM] = int(r[cls.FROM]) if (cls.FROM in r) else 0
        r[cls.TO] = int(r[cls.TO]) if (cls.TO in r) else ubound
        if cls.MANDATORY in r:
            r[cls.MANDATORY] = True if r[cls.MANDATORY] else False
        else:
            r[cls.MANDATORY] = True
        return r.validate(ubound)

    def is_empty(self):
        return self[self.FROM] == self[self.TO]

    def validate(self, ubound):
        self[self.FROM] = max(self[self.FROM], 0)
        self[self.TO] = min(ubound, self[self.TO])
        if self[self.TO] < self[self.FROM]:
            self[self.TO] = self[self.FROM]
        return self


class RangeList(list):
    @classmethod
    def loadl(cls, l, ubound):
        rl = cls()
        for d in l:
            rl.append(Range.loadd(d, ubound))
        rl.validate()
        return rl

    def _sort_key_of(self, r):
        return (r[Range.FROM], -r[Range.TO])

    def _insert(self, i, r):
        k = self._sort_key_of(r)
        while(i < len(self)):
            if(k < self._sort_key_of(self[i])):
                self.insert(i, r)
                return self
            else:
                i += 1
        self.append(r)
        return self

    def validate(self):
        self.sort(key=lambda r: self._sort_key_of(r))
        i = 0
        while(i < len(self) - 1):
            merger, mergee = self[i], self[i + 1]
            assert merger[Range.FROM] <= mergee[Range.FROM]
            if merger[Range.TO] < mergee[Range.FROM]:  # No relation
                i += 1
                continue
            # Inclusion or Overlap
            if merger[Range.MANDATORY] == mergee[Range.MANDATORY]:
                self.pop(i + 1)
                if merger[Range.TO] < mergee[Range.TO]:  # Overlap
                    merger[Range.TO] = mergee[Range.TO]
                continue
            if merger[Range.TO] == mergee[Range.FROM]:  # Optimal
                i += 1
            if merger[Range.MANDATORY]:
                if merger[Range.TO] < mergee[Range.TO]:  # Overlap
                    mergee[Range.FROM] = merger[Range.TO]
                else:  # Inclusion
                    self.pop(i + 1)
            else:
                if merger[Range.TO] < mergee[Range.TO]:  # Overlap
                    merger[Range.TO] = mergee[Range.FROM]
                else:  # Inclusion
                    r = Range.loadd({
                        Range.FROM: mergee[Range.TO],
                        Range.TO: merger[Range.TO],
                        Range.MANDATORY: False,
                    }, merger[Range.TO])
                    merger[Range.TO] = mergee[Range.FROM]
                    self._insert(i, r)
        while(i < len(self)):
            if(self[i].is_empty()):
                self.pop(i)
            else:
                i += 1


class Headings(list):  # is a range jag
    @classmethod
    def loadl(cls, j, ubound):
        h = cls()
        for l in j:
            h.append(RangeList.loadl(l, ubound))
        return h


class Block(dict):

    CHILDREN = 'children'
    CONTENTS = 'contents'
    HEADINGS = 'headings'

    @classmethod
    def loadd(cls, d, ubound):
        b = cls()
        b.update(d)

        b[Block.CHILDREN] = []
        if Block.CHILDREN in d:
            for c in d[Block.CHILDREN]:
                b[Block.CHILDREN].append(Block.loadd(c, ubound))
        b[Block.CONTENTS] = RangeList.loadl(
            d[Block.CONTENTS] if (Block.CONTENTS in d) else [],
            ubound,
        )
        b[Block.HEADINGS] = Headings.loadl(
            d[Block.HEADINGS] if (Block.HEADINGS in d) else [],
            ubound,
        )
        return b

    def __iter__(self):
        return iter(self[Block.CHILDREN])


class HeadingStructure(Block):

    RAW_STRING = 'rawString'

    @classmethod
    def load(cls, f):
        return cls.loads(f.read())

    @classmethod
    def loads(cls, s):
        d = json.loads(s)
        if HeadingStructure.RAW_STRING in d:
            rs = d[HeadingStructure.RAW_STRING]
        else:
            rs = ''
        hs = cls.loadd(d, len(rs))
        hs[HeadingStructure.RAW_STRING] = rs
        return hs
