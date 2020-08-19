"""CPU functionality."""

import sys
import re

# Instruction Set
# https://github.com/tmshkr/Computer-Architecture/blob/master/LS8-spec.md#instruction-set
HLT = 0b00000001
LDI = 0b10000010
NOP = 0b00000000
PUSH = 0b01000101
POP = 0b01000110
PRN = 0b01000111

# ALU Instruction Set
ADD = 0b10100000
AND = 0b10101000
CMP = 0b10100111
DEC = 0b01100110
DIV = 0b10100011
INC = 0b01100101
MOD = 0b10100100
MUL = 0b10100010
OR = 0b10101010
SHL = 0b10101100
SHR = 0b10101101
SUB = 0b10100001
XOR = 0b10101011


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[7] = 0xF4  # stack pointer
        self.pc = 0

        # Set up the branch table
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[MUL] = self.alu
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop

    def load(self):
        """Load a program into memory."""

        with open(sys.argv[1]) as f:
            address = 0
            for line in f:
                byte = re.match(r"[01]{8}", line)
                if byte:
                    instruction = int(byte.group(), 2)
                    self.ram[address] = instruction
                    address += 1

    def alu(self, op, a, b):
        """ALU operations."""
        # bitwise-AND the result with 0xFF (255) to keep the register values in range

        if op == MUL:
            self.reg[a] *= self.reg[b] & 0xFF
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        self.running = True
        while self.running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            self.branchtable[ir](ir, operand_a, operand_b)

            instruction_size = ir >> 6
            self.pc += 1 + instruction_size

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def handle_hlt(self, op, a, b):
        self.running = False

    def handle_ldi(self, op, a, b):
        self.reg[a] = b

    def handle_prn(self, op, a, b):
        print(self.reg[a])

    def handle_push(self, op, a, b):
        self.reg[7] -= 1
        self.ram[self.reg[7]] = self.reg[a]

    def handle_pop(self, op, a, b):
        self.reg[a] = self.ram[self.reg[7]]
        self.reg[7] += 1
