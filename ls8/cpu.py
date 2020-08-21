"""CPU functionality."""

import sys
import re

# Instruction Set
# https://github.com/tmshkr/Computer-Architecture/blob/master/LS8-spec.md#instruction-set
CALL = 0b01010000
HLT = 0b00000001
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100
LDI = 0b10000010
NOP = 0b00000000
PUSH = 0b01000101
POP = 0b01000110
PRN = 0b01000111
RET = 0b00010001

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
        self.fl = 0  # flags register for CMP op

        # Set up the branch table
        self.branchtable = {}
        self.branchtable[CALL] = self.handle_call
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JMP] = self.handle_jmp
        self.branchtable[JNE] = self.handle_jne
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[RET] = self.handle_ret

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
        elif op == ADD:
            self.reg[a] += self.reg[b] & 0xFF
        elif op == CMP:
            if self.reg[a] < self.reg[b]:
                self.fl = 0b00000100
            elif self.reg[a] > self.reg[b]:
                self.fl = 0b00000010
            elif self.reg[a] == self.reg[b]:
                self.fl = 0b00000001
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

            # AABCDDDD
            # if bit B is 1, it's an ALU op
            is_alu_op = ir >> 5 & 0b1
            if is_alu_op:
                self.alu(ir, operand_a, operand_b)
            else:
                self.branchtable[ir](ir, operand_a, operand_b)

            # if bit C is 1, it sets the PC
            sets_pc = ir >> 4 & 0b1
            if not sets_pc:
                # bits AA contain the number
                # of operands for a given instruction
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

    def handle_call(self, op, a, b):
        # push the address to continue at
        # after returning from the call
        self.reg[7] -= 1
        self.ram[self.reg[7]] = self.pc + 2

        # set the PC to the address stored in given register
        self.pc = self.reg[a]

    def handle_ret(self, op, a, b):
        # pop off and return to the address
        # previously pushed
        self.pc = self.ram[self.reg[7]]
        self.reg[7] += 1

    def handle_jmp(self, op, a, b):
        # set the PC to the address stored in given register
        self.pc = self.reg[a]

    def handle_jeq(self, op, a, b):
        if (self.fl & 1):
            self.pc = self.reg[a]
        else:
            self.pc += 2

    def handle_jne(self, op, a, b):
        if not (self.fl & 1):
            self.pc = self.reg[a]
        else:
            self.pc += 2
