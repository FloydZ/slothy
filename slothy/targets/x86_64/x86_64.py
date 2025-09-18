#!/usr/bin/env python3


import logging
import inspect
import re
import math
from enum import Enum
from functools import cache
from sympy import simplify

from unicorn import (
    UC_ARCH_X86,
    UC_MODE_64,
)


from unicorn.x86_const import (
    UC_X86_REG_RAX,
    UC_X86_REG_RBX,
    UC_X86_REG_RCX,
    UC_X86_REG_RDX,
    UC_X86_REG_RSI,
    UC_X86_REG_RDI,
    UC_X86_REG_RSP,
    UC_X86_REG_RBP,
    UC_X86_REG_RIP,
    UC_X86_REG_R8, 
    UC_X86_REG_R9, 
    UC_X86_REG_R10,
    UC_X86_REG_R11,
    UC_X86_REG_R12,
    UC_X86_REG_R13,
    UC_X86_REG_R14,
    UC_X86_REG_R15,
)


from slothy.targets.common import FatalParsingException, UnknownInstruction
from slothy.helper import Loop, SourceLine

arch_name = "x86_64"

llvm_mca_arch = "x86_64"
llvm_mc_arch = "x86_64"
# Always add aes flag for llvm-mc assembly -- assuming that the user will not
# use aes instructions on CPUs that do not support it
llvm_mc_attr = "aes"

unicorn_arch = UC_ARCH_X86
unicorn_mode = UC_MODE_64


class RegisterType(Enum):
    GPR = 1
    AVX2 = 2
    FLAGS = 5

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @cache
    def _spillable(reg_type):
        # TODO: maybe also AVX2
        return reg_type in [RegisterType.GPR]  

    # TODO: remove workaround (needed for Python 3.9)
    spillable = staticmethod(_spillable)
    
    @staticmethod
    def unicorn_link_register():
        return 0 # TODO UC_ARM64_REG_X30

    @staticmethod
    def unicorn_stack_pointer():
        return UC_X86_REG_RSP

    @staticmethod
    def unicorn_program_counter():
        return UC_X86_REG_RIP

    @cache
    def _unicorn_reg_by_name(reg):
        """Converts string name of register into numerical identifiers used
        within the unicorn engine"""

        d = {
            "rax": UC_X86_REG_RAX,
            "rbx": UC_X86_REG_RBX,
            "rcx": UC_X86_REG_RCX,
            "rdx": UC_X86_REG_RDX,
            "rsp": UC_X86_REG_RSP,
            "rbp": UC_X86_REG_RBP,
            "rip": UC_X86_REG_RIP,
            "r8": UC_X86_REG_R8,
            "r9": UC_X86_REG_R9,
            "r10": UC_X86_REG_R10,
            "r11": UC_X86_REG_R11,
            "r12": UC_X86_REG_R12,
            "r13": UC_X86_REG_R13,
            "r14": UC_X86_REG_R14,
            "r15": UC_X86_REG_R15,
        }
        return d.get(reg, None)

    # TODO: remove workaround (needed for Python 3.9)
    unicorn_reg_by_name = staticmethod(_unicorn_reg_by_name)

    def _list_registers(
        reg_type, only_extra=False, only_normal=False, with_variants=False
    ):
        """Return the list of all registers of a given type"""
        raise NotImplementedError()
        return []


class Branch:
    """Helper for emitting branches"""

    @staticmethod
    def if_equal(cnt, val, lbl):
        """Emit assembly for a branch-if-equal sequence"""
        yield f"cmp {cnt}, ${val}"
        yield f"je {lbl}"

    @staticmethod
    def if_zero(cnt, val, lbl):
        """Emit assembly for a branch-if-zero sequence"""
        yield f"cmp {cnt}, ${val}"
        yield f"jz {lbl}"

    @staticmethod
    def if_greater(cnt, val, lbl):
        """Emit assembly for a branch-if-greater sequence"""
        yield f"cmp {cnt}, ${val}"
        yield f"jg {lbl}"

    @staticmethod
    def if_greater_equal(cnt, val, lbl):
        """Emit assembly for a branch-if-greater-equal sequence"""
        yield f"cmp {cnt}, ${val}"
        yield f"jge {lbl}"

    @staticmethod
    def unconditional(lbl):
        """Emit unconditional branch"""
        yield f"jmp {lbl}"


class SubLoop(Loop):
    """
    Loop ending in a (optionally flag setting) subtraction and a branch.

    Example:

    .. code-block:: asm

        loop_lbl:
           {code}
           sub  <cnt>, #<imm>
           (jnz|jz) <cnt>, loop_lbl

    where cnt is the loop counter in lr.
    """

    def __init__(self, lbl="lbl") -> None:
        super().__init__()
        # TODO not implemented


class Instruction:

    class ParsingException(Exception):
        """An attempt to parse an assembly line as a specific instruction failed

        This is a frequently encountered exception since assembly lines are parsed by
        trial and error, iterating over all instruction parsers."""

        def __init__(self, err=None):
            super().__init__(err)

    def __init__(
        self, *, mnemonic, arg_types_in=None, arg_types_in_out=None, arg_types_out=None
    ):
        pass


class X86_64Instruction(Instruction):
    """Abstract class representing x86_64 instructions"""

    PARSERS = {}


class nop(X86_64Instruction):
    pattern = "nop"


class adc(X86_64Instruction):
    pattern = "adc <aR64>, <bR64>, <cR64>"
    inputs = ["bR64", "cR64"]
    outputs = ["aR64"]
