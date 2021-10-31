from cpu import CPU
import constants
import pygame
import time
import argparse


def show_info(cpu, cycle):
    # returns CPU registers, stack, opcodes
    res = []
    res.append(f"CYCLE : {cycle}")
    for i in range(0x10):
        res.append(f"V{i:2} : {hex(cpu.v[i])}")
    res.append(f"OPCODE : {cpu.opcode.hex().lower()}")
    res.append(f"I : {hex(cpu.i)}")
    res.append(f"PC : {hex(cpu.pc)}")
    res.append(f"SP : {hex(cpu.sp)}")
    res.append(f"STACK : {cpu.stack}")
    res.append(f"DELAY : {hex(cpu.delay_timer)}")
    res.append(f"SOUND : {hex(cpu.sound_timer)}\n")
    res.append(f"")
    res.append(f"OPCODES :")
    last_opcodes_proper_order = last_opcodes[::-1]
    for _opcode in last_opcodes_proper_order:
        res.append(_opcode.hex())
    return res


def clear_viewport(screen):
    # Clear CHIP-8 viewport
    pygame.draw.rect(
        screen,
        constants.BLACK,
        (0, 0, constants.DISPLAY_W_SCALED, constants.DISPLAY_H_SCALED)
    )


def compute_byte_coords(b):
    # Compute coordinates at which to draw green highlight
    # in memory view, given memory address
    w = constants.DISPLAY_W_SCALED + constants.DEBUGGER_SCALING * (b % 64)
    h = constants.DEBUGGER_SCALING * int(b / 64)
    return w, h


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("program", type=str,
                        help="path to the program to load")
    parser.add_argument("--cps", type=int,
                        help=f"cycles per second. Default is {constants.CYCLES_PER_SECOND} cps")
    parser.add_argument("--fps", type=int,
                        help=f"window rendering framerate. Default is {constants.FRAMES_PER_SECOND} fps")
    parser.add_argument("-c", "--cpu-view", help="enable visualization of CPU registers, stack, opcodes",
                        action="store_true")
    parser.add_argument("-m", "--memory-view",
                        help="enable memory visualization. Also enables CPU visualization (like --cpu-view)",
                        action="store_true")
    args = parser.parse_args()

    # Use args
    BIN_PATH = args.program
    if args.cps:
        CYCLES_PER_SECOND = args.cps
    else:
        CYCLES_PER_SECOND = constants.CYCLES_PER_SECOND

    if args.fps:
        FRAMES_PER_SECOND = args.fps
    else:
        FRAMES_PER_SECOND = constants.FRAMES_PER_SECOND

    # Set width based on args
    if args.memory_view:
        WIDTH = constants.WIDTH
        HEIGHT = constants.HEIGHT
    elif args.cpu_view:
        WIDTH = constants.DISPLAY_W_SCALED
        HEIGHT = constants.HEIGHT
    else:
        WIDTH = constants.DISPLAY_W_SCALED
        HEIGHT = constants.DISPLAY_H_SCALED

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode(
        (WIDTH, HEIGHT))
    font = pygame.font.SysFont("Courier New", 10, bold=True)
    beep = pygame.mixer.Sound("beep.wav")

    BIN = open(BIN_PATH, "rb").read()
    _cpu = CPU()
    _cpu.load_bin(BIN)

    # list containing the last opcodes to show on debugger
    last_opcodes = []

    cycle = 0
    fps_timer = 0
    beep_playing = False

    previous_time = pygame.time.get_ticks()

    while(True):
        try:

            _cpu.cycle()

            # Decrement timers at 60 Hz
            current_time = pygame.time.get_ticks()
            if current_time - previous_time > 1000 / 60:
                if _cpu.delay_timer > 0:
                    _cpu.delay_timer -= 1
                if _cpu.sound_timer > 0:
                    _cpu.sound_timer -= 1
                previous_time = current_time

            cycle += 1
            fps_timer += 1

            # Beep!
            if _cpu.sound_timer > 0:
                if not beep_playing:
                    beep_playing = True
                    beep.play()
            else:
                beep_playing = False
                beep.stop()

        except Exception:
            print("Exception occurred!")
            for line in show_info(_cpu, cycle):
                print(line)
            raise

        # fps_timer reaches CYCLES_PER_SECOND roughly every second,
        # so it works approximately well for timing
        if fps_timer >= CYCLES_PER_SECOND // FRAMES_PER_SECOND:

            fps_timer = 0

            _cpu.get_key_and_events(halt=False)

            # Draw CHIP-8 screen
            # Clear previous CHIP-8 frame
            clear_viewport(screen)
            for i in range(32):
                for j in range(64):
                    if _cpu.display[64 * i + j] == 1:
                        pygame.draw.rect(
                            screen, constants.WHITE,
                            (j * constants.SCALING, i * constants.SCALING,
                             constants.SCALING, constants.SCALING))

            last_opcode = _cpu.opcode
            last_opcodes.insert(0, last_opcode)
            if len(last_opcodes) > constants.MAX_OPCODE_LIST_LENGTH:
                last_opcodes.pop()

            if args.memory_view:
                # Render memory view
                # Cover previous memory view
                pygame.draw.rect(
                    screen, constants.GRAY,
                    (constants.DISPLAY_W_SCALED,
                     0, WIDTH, HEIGHT)
                )

                # Highlight PC position on memory
                w, h = compute_byte_coords(_cpu.pc)
                pygame.draw.rect(
                    screen, constants.GREEN,
                    (w, h, 2 * constants.DEBUGGER_SCALING,
                     constants.DEBUGGER_SCALING)
                )

                for i in range(constants.MEMORY_SIZE):
                    font_surface = font.render(
                        ("%x" % _cpu.memory[i]).zfill(2),
                        True, constants.WHITE)
                    screen.blit(font_surface, compute_byte_coords(i))

            if args.cpu_view:
                # Render registers and stack
                # Cover previous registers view
                pygame.draw.rect(
                    screen, constants.GRAY,
                    (0, constants.DISPLAY_H_SCALED, constants.DISPLAY_W_SCALED, constants.DEBUGGER_HEIGHT))

                x_pos = constants.FIRST_LINE_X_POS
                n_lines_return = 0
                for i, line in enumerate(show_info(_cpu, cycle)):
                    font_surface = font.render(
                        line, True, constants.WHITE)
                    if line.startswith("OPCODES") and x_pos == constants.FIRST_LINE_X_POS:
                        x_pos = constants.SECOND_LINE_X_POS
                        n_lines_return = i
                    screen.blit(
                        font_surface, (x_pos, constants.DISPLAY_H_SCALED + (i - n_lines_return) * constants.DEBUGGER_SCALING))

            # Show rendered frame
            pygame.display.flip()

        time.sleep(1/CYCLES_PER_SECOND)
