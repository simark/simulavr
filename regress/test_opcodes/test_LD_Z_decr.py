#! /usr/bin/env python
###############################################################################
#
# simulavr - A simulator for the Atmel AVR family of microcontrollers.
# Copyright (C) 2001, 2002  Theodore A. Roth
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
###############################################################################
#
# $Id: test_LD_Z_decr.py,v 1.1 2004/07/31 00:59:11 rivetwa Exp $
#

"""Test the LD_Z_decr opcode.
"""

import base_test
from registers import Reg, SREG

class LD_Z_decr_TestFail(base_test.TestFail): pass

class base_LD_Z_decr(base_test.opcode_test):
	"""Generic test case for testing LD_Z_decr opcode.

	LD_Z_decr - Load Indirect from data space to Register using index Z and
	pre decrement Z.

	Operation: Z <- Z - 1 then Rd <- (Z)

	opcode is '1001 000d dddd 0010' where 0 <= d <= 31 and d != {30,31}

	Only registers PC, R30, R31 and Rd should be changed.
	"""
	def setup(self):
		# Set the register values
		self.setup_regs[self.Rd] = 0
		self.setup_regs[Reg.R30] = (self.Z & 0xff)
		self.setup_regs[Reg.R31] = ((self.Z >> 8) & 0xff)

		# set up the val in memory (memory is read after Z is decremented,
		# thus we need to write to memory _at_ Z - 1)
		self.mem_byte_write( self.Z - 1, self.Vd )

		# Return the raw opcode
		return 0x9002 | (self.Rd << 4)

	def analyze_results(self):
		self.reg_changed.extend( [self.Rd, Reg.R30, Reg.R31] )
		
		# check that result is correct
		expect = self.Vd
		got = self.anal_regs[self.Rd]
		
		if expect != got:
			self.fail('LD_Z_decr: expect=%02x, got=%02x' % (expect, got))

		# check that Z was decremented
		expect = self.Z - 1
		got = (self.anal_regs[Reg.R30] & 0xff) | ((self.anal_regs[Reg.R31] << 8) & 0xff00)

		if expect != got:
			self.fail('LD_Z_decr Z not decr: expect=%04x, got=%04x' % (expect, got))

#
# Template code for test case.
# The fail method will raise a test specific exception.
#
template = """
class LD_Z_decr_r%02d_Z%04x_v%02x_TestFail(LD_Z_decr_TestFail): pass

class test_LD_Z_decr_r%02d_Z%04x_v%02x(base_LD_Z_decr):
	Rd = %d
	Z = 0x%x
	Vd = 0x%x
	def fail(self,s):
		raise LD_Z_decr_r%02d_Z%04x_v%02x_TestFail, s
"""

#
# automagically generate the test_LD_Z_decr_rNN_vXX class definitions.
#
# Operation is undefined for d = 30 and d = 31.
#
code = ''
for d in range(0,30):
	for z in (0x10f, 0x1ff):
		for v in (0xaa, 0x55):
			args = (d,z,v)*4
			code += template % args
exec code
