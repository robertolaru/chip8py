SCALING = 10
DEBUGGER_SCALING = 12

DEBUGGER_WIDTH = DEBUGGER_SCALING * 64
DEBUGGER_HEIGHT = DEBUGGER_SCALING * 64

DISPLAY_W = 64
DISPLAY_H = 32

DISPLAY_W_SCALED = SCALING * DISPLAY_W
DISPLAY_H_SCALED = SCALING * DISPLAY_H

WIDTH = DISPLAY_W_SCALED + DEBUGGER_WIDTH
HEIGHT = DEBUGGER_HEIGHT

BLACK = (0, 0, 0)
GRAY = (25, 25, 25)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

MEMORY_SIZE = 4096
DISPLAY_SIZE = DISPLAY_W * DISPLAY_H
FONT_ADDRESS = 0x50

CYCLES_PER_SECOND = 500
FRAMES_PER_SECOND = 30
MAX_OPCODE_LIST_LENGTH = 22
FIRST_LINE_X_POS = 10
SECOND_LINE_X_POS = 250
