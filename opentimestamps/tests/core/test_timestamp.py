# Copyright (C) 2016 The OpenTimestamps developers
#
# This file is part of python-opentimestamps.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-opentimestamps including this file, may be copied,
# modified, propagated, or distributed except according to the terms contained
# in the LICENSE file.

import unittest

from opentimestamps.core.notary import *
from opentimestamps.core.serialize import *
from opentimestamps.core.timestamp import *

class Test_Op(unittest.TestCase):
    def test_append(self):
        op = OpAppend(b'msg', b'suffix')
        self.assertEqual(op.timestamp.msg, b'msgsuffix')

    def test_prepend(self):
        op = OpPrepend(b'msg', b'prefix')
        self.assertEqual(op.timestamp.msg, b'prefixmsg')

    def test_reverse(self):
        op = OpReverse(b'abcd')
        self.assertEqual(op.timestamp.msg, b'dcba')

    def test_sha256(self):
        op = OpSHA256(b'')
        self.assertEqual(op.timestamp.msg, bytes.fromhex('e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'))

    def test_ripemd160(self):
        op = OpRIPEMD160(b'')
        self.assertEqual(op.timestamp.msg, bytes.fromhex('9c1185a5c5e9fc54612808977ee8f548b2258d31'))

    def test_changing_timestamps(self):
        op1 = OpRIPEMD160(b'')
        op2 = OpRIPEMD160(b'')

        self.assertIsNot(op1.timestamp, op2.timestamp)

        op1.timestamp = op2.timestamp
        self.assertIs(op1.timestamp, op2.timestamp)

        with self.assertRaises(ValueError):
            op1.timestamp = Timestamp(b'')

class Test_Timestamp(unittest.TestCase):
    def test_serialize(self):
        stamp = Timestamp(b'foo')
        stamp.add_op(OpVerify, PendingAttestation(b'foobar'))

        expected_serialized = b'\x00' + bytes.fromhex('83dfe30d2ef90c8e' + '07' + '06') + b'foobar'

        ctx = BytesSerializationContext()
        stamp.serialize(ctx)
        self.assertEqual(ctx.getbytes(), expected_serialized)

        stamp.add_op(OpVerify, PendingAttestation(b'foobar'))
        expected_serialized = b'\xff' + (b'\x00' + bytes.fromhex('83dfe30d2ef90c8e' + '07' + '06') + b'foobar') \
                                      + (b'\x00' + bytes.fromhex('83dfe30d2ef90c8e' + '07' + '06') + b'foobar') + \
                              b'\xfe'
