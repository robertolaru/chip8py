import random
import constants
import pygame


class CPU:
    def __init__(self) -> None:

        self.memory = bytearray(constants.MEMORY_SIZE)
        self.display = bytearray(constants.DISPLAY_SIZE)

        self.key = None

        # Create registers
        self.v = [0x0 for i in range(16)]
        self.i = 0
        self.pc = 0
        self.sp = 0

        self.stack = []

        self.delay_timer = 0
        self.sound_timer = 0

        # Initialize PC at entry point
        self.pc = 0x200

        # Draw flag
        self.draw_flag = False

        # Keys
        self.KEYS = {
            pygame.K_1: 0x1,
            pygame.K_2: 0x2,
            pygame.K_3: 0x3,
            pygame.K_4: 0xc,
            pygame.K_q: 0x4,
            pygame.K_w: 0x5,
            pygame.K_e: 0x6,
            pygame.K_r: 0xd,
            pygame.K_a: 0x7,
            pygame.K_s: 0x8,
            pygame.K_d: 0x9,
            pygame.K_f: 0xe,
            pygame.K_z: 0xa,
            pygame.K_x: 0x0,
            pygame.K_c: 0xb,
            pygame.K_v: 0xf
        }

        # Opcodes
        self.CODES = (
            # (pattern, self.function)
            ("1000", self.jmp),
            ("2000", self.call),
            ("3000", self.skip_equ_val),
            ("4000", self.skip_not_val),
            ("5000", self.skip_equ_reg),
            ("6000", self.set_val),
            ("7000", self.add_val),
            ("8001", self.set_or),
            ("8002", self.set_and),
            ("8003", self.set_xor),
            ("8004", self.add_reg),
            ("8005", self.sub_reg),
            ("8006", self.rshift),
            ("8007", self.diff),
            ("800e", self.lshift),
            ("8000", self.set_reg),
            ("9000", self.skip_not_reg),
            ("a000", self.set_i_addr),
            ("b000", self.jmp_v0),
            ("c000", self.rand),
            ("d000", self.draw),
            ("e09e", self.skip_key_pressed),
            ("e0a1", self.skip_key_not_pressed),
            ("f015", self.set_delay),
            ("f018", self.set_sound_t),
            ("f01e", self.add_i_reg),
            ("f029", self.set_i_sprite),
            ("f033", self.bcd),
            ("f055", self.save),
            ("f065", self.load),
            ("f007", self.get_delay),
            ("f00a", self.get_key)
        )

        self.FONT = (
            # (char_sprite_data, offset)
            (0xf0909090f0, 0),   # 0
            (0x2060202070, 5),   # 1
            (0xf010f080f0, 10),  # 2
            (0xf010f010f0, 15),  # 3
            (0x9090f01010, 20),  # 4
            (0xf080f010f0, 25),  # 5
            (0xf080f090f0, 30),  # 6
            (0xf010204040, 35),  # 7
            (0xf090f090f0, 40),  # 8
            (0xf090f010f0, 45),  # 9
            (0xf090f09090, 50),  # A
            (0xe090e090e0, 55),  # B
            (0xf0808080f0, 60),  # C
            (0xe0909090e0, 65),  # D
            (0xf080f080f0, 70),  # E
            (0xf080f08080, 75)   # F
        )

        # Load font in memory
        cursor = constants.FONT_ADDRESS   # Starting position for font data
        for code in self.FONT:
            self.memory[cursor: cursor + 5] = code[0].to_bytes(5, "big")
            cursor += 5

    # Convert bytearray to int
    def get_int(self, _int):
        return int.from_bytes(_int, "big")

    # Skip next instruction
    def skip(self):
        self.pc += 2

    # Don't skip next instruction.
    # Decreases PC to cancel cycle skip
    def prevent_skip(self):
        self.pc -= 2

    def load_bin(self, data):
        self.memory[0x200: 0x200 + len(data)] = data

    def load_opcode(self):
        this_opcode = self.opcode.hex().lower()

        # opcodes with exact match
        if this_opcode == "00e0":
            self.clear()
        elif this_opcode == "00ee":
            self.ret()
        # opcodes where partial match with pattern is expected
        else:
            for _opcode, function in self.CODES:
                all_match = True
                for i, ch in enumerate(_opcode.lower()):
                    if ch == "0":
                        pass
                    elif not all_match:
                        break
                    elif ch != this_opcode[i]:
                        all_match = False
                if all_match:
                    function()
                    break

    def __get_key(self, halt=False):
        key_acquired = False
        while (not key_acquired):
            events = pygame.event.get()
            if events != []:
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        key_acquired = True
                        key = self.KEYS.get(event.key)
                        self.key = key
            if not halt:
                break

    # Methods to fetch values from opcodes, depending on opcode pattern

    def get_addr(self):
        # _NNN
        return self.get_int(self.opcode) & 0x0fff

    def get_reg(self):
        # _X___
        return (self.get_int(self.opcode) & 0x0f00) >> 8

    def get_reg_val(self):
        # _XNN
        return self.get_reg(), self.get_int(self.opcode) & 0x00ff

    def get_regs(self):
        # _XY_
        return self.get_reg(), (self.get_int(self.opcode) & 0x00f0) >> 4

    def get_regs_val(self):
        # _XYN
        return *self.get_regs(), self.get_int(self.opcode) & 0x000f

    # Opcode methods

    def clear(self):
        self.display = bytearray(constants.DISPLAY_SIZE)
        self.draw_flag = True

    def ret(self):
        _pop = self.stack.pop()
        self.pc = _pop + 2
        self.prevent_skip()

    def jmp(self, v0=0):
        self.pc = self.get_addr() + v0
        self.prevent_skip()

    def call(self):
        self.stack.append(self.pc & 0xfff)
        self.pc = self.get_addr()   # called address
        self.prevent_skip()

    def skip_equ_val(self):
        vx, nn = self.get_reg_val()
        if self.v[vx] == nn:
            self.skip()

    def skip_not_val(self):
        vx, nn = self.get_reg_val()
        if self.v[vx] != nn:
            self.skip()

    def skip_equ_reg(self):
        vx, vy = self.get_regs()
        if self.v[vx] == self.v[vy]:
            self.skip()

    def set_val(self):
        vx, nn = self.get_reg_val()
        self.v[vx] = nn

    def add_val(self):
        vx, nn = self.get_reg_val()
        res = (self.v[vx] + nn) & 0xff
        self.v[vx] = res

    def set_reg(self):
        vx, vy = self.get_regs()
        self.v[vx] = self.v[vy]

    def set_or(self):
        vx, vy = self.get_regs()
        self.v[vx] |= self.v[vy]

    def set_and(self):
        vx, vy = self.get_regs()
        self.v[vx] &= self.v[vy]

    def set_xor(self):
        vx, vy = self.get_regs()
        self.v[vx] ^= self.v[vy]

    def add_reg(self):
        vx, vy = self.get_regs()
        res = (self.v[vx] + self.v[vy]) & 0xff
        self.v[vx] = res
        if res > 0xff:
            self.v[0xf] = 1  # set to 1 if carry
        else:
            self.v[0xf] = 0

    def sub_reg(self):
        vx, vy = self.get_regs()
        res = (self.v[vx] - self.v[vy]) & 0xff
        self.v[vx] = res
        if res < 0:
            self.v[0xf] = 0  # set to 0 if borrow
        else:
            self.v[0xf] = 1

    def rshift(self):
        vx, vy = self.get_regs()
        self.v[0xf] = self.v[vy] & 0x1  # least significant bit
        self.v[vx] = self.v[vy] >> 1

    def diff(self):
        vx, vy = self.get_regs()
        res = (self.v[vy] - self.v[vx]) & 0xff
        self.v[vx] = res
        if res < 0:
            self.v[0xf] = 0  # borrow flag
        else:
            self.v[0xf] = 1

    def lshift(self):
        vx, vy = self.get_regs()
        self.v[0xf] = self.v[vy] & 0x80  # most significant bit
        self.v[vx] = self.v[vy] << 1

    def skip_not_reg(self):
        vx, vy = self.get_regs()
        if self.v[vx] != self.v[vy]:
            self.skip()

    def set_i_addr(self):
        self.i = self.get_addr() & 0xfff

    def jmp_v0(self):
        self.jmp(v0=self.v[0])

    def rand(self):
        vx, mask = self.get_reg_val()
        rnd = random.randint(0, 255)
        self.v[vx] = rnd & mask

    def draw(self):
        vx, vy, height = self.get_regs_val()
        x, y = self.v[vx], self.v[vy]
        sprite_data = [format(self.memory[self.i + h], "b").zfill(8)
                       for h in range(height)]

        collision = False

        for h in range(height):
            start_pixel = x + (y + h) * 64
            for i, pixel in enumerate(sprite_data[h]):
                pos = (start_pixel + i) & 0x7ff
                prev = self.display[pos]
                if int(pixel) == 1:
                    if prev == 1:
                        collision = True
                        self.display[pos] = 0
                    else:
                        self.display[pos] = 1

        if collision:
            self.v[0xf] = 1
        else:
            self.v[0xf] = 0

        self.draw_flag = True

    def skip_key_pressed(self):
        self.__get_key(halt=False)
        vx = self.get_reg()
        if self.key == self.v[vx]:
            self.skip()

    def skip_key_not_pressed(self):
        self.__get_key(halt=False)
        vx = self.get_reg()
        if self.key != self.v[vx]:
            self.skip()

    def get_delay(self):
        vx = self.get_reg()
        self.v[vx] = self.delay_timer

    def get_key(self):
        self.__get_key(halt=True)
        vx = self.get_reg()
        self.v[vx] = self.key
        pass

    def set_delay(self):
        vx = self.get_reg()
        self.delay_timer = self.v[vx]

    def set_sound_t(self):
        vx = self.get_reg()
        self.sound_timer = self.v[vx]

    def add_i_reg(self):
        vx = self.get_reg()
        self.i += self.v[vx]
        self.i &= 0xfff

    def set_i_sprite(self):
        vx = self.get_reg()
        char = self.v[vx]
        # Set i to font address + char offset
        self.i = (constants.FONT_ADDRESS + self.FONT[char][1]) & 0xfff

    def bcd(self):
        vx = self.get_reg()
        x = self.v[vx]
        # Obtain digits
        digits = str(x).zfill(3)
        # Store each digit back as int in I + i
        for i in range(3):
            self.memory[self.i + i] = int(digits[i])

    def save(self):
        vx = self.get_reg()
        for i in range(vx + 1):  # vx included
            self.memory[self.i + i] = self.v[i]

    def load(self):
        vx = self.get_reg()
        for i in range(vx + 1):  # vx included
            self.v[i] = self.memory[self.i + i]

    def cycle(self):
        # Turn off draw flag. It will be enabled by the appropriate functions
        # if needed
        self.draw_flag = False

        # Fetch
        self.opcode = self.memory[self.pc: self.pc + 2]

        # Decode & execute
        self.load_opcode()

        # Increment PC for the next instruction
        self.pc += 2
