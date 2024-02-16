# Basic Computer Assembler (Python)
A simple 2 phase assembler created as a project for my computer organization class. **Simple, Robust, Efficient.**

## Features:
1) Error Handling: syntax errors are detected by the program and reported as an error
2) Stability: The assembler has been extensively tested and is guaranteed to produce correct assembly

## Installation:
Installing this is as simple as git cloning the repository. There are no external dependenices.
```bash
git clone https://github.com/AlyElsharkawy/Basic-Computer-Assembler-Python
```
Inside the newly created Basic-Computer-Assembler-Python folder, you will find `assembler.py` along with three files called `rri.txt`, `mri.txt`, and `ioi.txt`. `assembler.py` is the file that you will need to import into your projects to use.

## Usage:
First, import `assembler.py`. Then, create you must screate an instance of the `Assembler` class. The `Assembler` class takes 4 parameters in this order:
- Location of the assembly input file
- Location of mri.txt
- Location of rri.txt
- Location of ioi.txt
After that, it is as simple as calling the `.assemble()` method of your `Assembler` class object and storing the output in a variable. A demonstration is below:
```python
from assembler import Assembler

INPUT_FILE = 'testcode.asm'
OUT_FILE = 'testcode.mc'
MRI_FILE = 'mri.txt'
RRI_FILE = 'rri.txt'
IOI_FILE = 'ioi.txt'

asm = Assembler(asmpath=INPUT_FILE, \
                mripath=MRI_FILE, \
                rripath=RRI_FILE, \
                ioipath=IOI_FILE)
binaries = asm.assemble()
for line in binaries.keys():
    print(f"{line} {binaries[line]}")
```

## Issues:
If you find any issues with the assembler, please open an issue in the issues tab.

## Note:
An update is planned where it will be possible to use the assembler with arguments from terminal instead of as a class.
