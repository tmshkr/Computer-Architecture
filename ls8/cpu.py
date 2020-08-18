"""CPU functionality."""

import sys
import re

# Instruction Set
# https://github.com/tmshkr/Computer-Architecture/blob/master/LS8-spec.md#instruction-set
HLT = 0b00000001
LDI = 0b10000010
NOP = 0b00000000
PRN = 0b01000111


class CPU:
    """Main CPU class."""

    def __init__(self):
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0

        # Set up the branch table
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn

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

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
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
            self.operand_a = self.ram_read(self.pc + 1)
            self.operand_b = self.ram_read(self.pc + 2)

            self.branchtable[ir]()

            instruction_size = ir >> 6
            self.pc += 1 + instruction_size

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, value, address):
        self.ram[address] = value

    def handle_hlt(self):
        self.running = False

    def handle_ldi(self):
        self.reg[self.operand_a] = self.operand_b

    def handle_prn(self):
        print(self.reg[self.operand_a])
