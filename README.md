# chip8py

<div align="center">
<img style="width: 50%; image-rendering: pixelated; margin: 0 auto;" src="logo.PNG"></img>
<p><i>CHIP-8 interpreter written in Python</i></p>
</div>

## Contents

- [About](#about)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## About

CHIP-8 is an interpreted language developed during the 1970s.

chip8py is an interpreter that can run any program originally designed for the CHIP-8 platform.

## Installation

The project uses `pygame` to render the window:

```
python -m pip install pygame
```

Clone this repository into a folder:

```
git clone https://github.com/robertolaru/chip8py.git
```

## Usage

To run the program, you need to provide the path to the rom file to load in the interpreter:

```
python main.py /path/to/file
```

Originally, user input was done through a 16-key hex keyboard.

The interpreter maps the original keys to the leftmost portion of QWERTY keyboards:

```
 1 2 3 C         \       1 2 3 4
 4 5 6 D     -----\       Q W E R
 7 8 9 E     -----/        A S D F
 A 0 B F         /          Z X C V

(original)              (interpreter)
```

## License

chip8py is licensed under the MIT license.
