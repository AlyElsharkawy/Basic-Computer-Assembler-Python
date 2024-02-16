import sys
import traceback
class Assembler(object):
    def __init__(self, asmpath='', mripath='', rripath='', ioipath='') -> None:
        """
        Assembler class constructor.

        Initializes 7 important properties of the Assembler class:
        -   self.__address_symbol_table (dict): stores labels (scanned in the first pass)
            as keys and their locations as values.
        -   self.__bin (dict): stores locations (or addresses) as keys and the binary 
            representations of the instructions at these locations (job of the second pass) 
            as values.
        -   self.__asmfile (str): the file name of the assembly code file. This property
            is initialized and defined in the read_code() method.
        -   self.__asm (list): list of lists, where each outer list represents one line of 
            assembly code and the inner list is a list of the symbols in that line.
            for example:
                ORG 100
                CLE
            will yiels __asm = [['org', '100'] , ['cle']]
            Notice that all symbols in self.__asm are in lower case.
        -   self.__mri_table (dict): stores memory-reference instructions as keys, and their
            binary representations as values.
        -   self.__rri_table (dict): stores register-reference instructions as keys, and their
            binary representations as values.
        -   self.__ioi_table (dict): stores input-output instructions as keys, and their
            binary representations as values.
        
        Thie constructor receives four optional arguments:
        -   asmpath (str): path to the assembly code file.
        -   mripath (str): path to text file containing the MRI instructions. The file should
            include each intruction and its binary representation separated by a space in a
            separate line. Their must be no empty lines in this file.
        -   rripath (str): path to text file containing the RRI instructions. The file should
            include each intruction and its binary representation separated by a space in a
            separate line. Their must be no empty lines in this file.
        -   ioipath (str): path to text file containing the IOI instructions. The file should
            include each intruction and its binary representation separated by a space in a
            separate line. Their must be no empty lines in this file.
        """
        super().__init__()
        # Address symbol table dict -> {symbol: location}
        self.__address_symbol_table = {}
        # Assembled machine code dict -> {location: binary representation}
        self.__bin = {}
        # Load assembly code if the asmpath argument was provided.
        if asmpath:
            self.read_code(asmpath)
        # memory-reference instructions
        self.__mri_table = self.__load_table(mripath) if mripath else {}
        # register-reference instructions
        self.__rri_table = self.__load_table(rripath) if rripath else {}
        # input-output instructions
        self.__ioi_table = self.__load_table(ioipath) if ioipath else {}
    
        #Any variables I create will be here
        self.locationCounter = 0
        self.pseudoInstructions = ["org","hex","dec","end"]

    def read_code(self, path:str):
        """
        opens .asm file found in path and stores it in self.__asmfile.
        Returns None
        """
        assert path.endswith('.asm') or path.endswith('.S'), \
                        'file provided does not end with .asm or .S'
        self.__asmfile = path.split('/')[-1] # on unix-like systems
        with open(path, 'r') as f:
            # remove '\n' from each line, convert it to lower case, and split
            # it by the whitespaces between the symbols in that line.
            self.__asm = [s.rstrip().lower().split() for s in f.readlines()]


    def assemble(self, inp='') -> dict:
        assert self.__asm or inp, 'no assembly file provided'
        if inp:
            assert inp.endswith('.asm') or inp.endswith('.S'), \
                        'file provided does not end with .asm or .S'
        # if assembly file was not loaded, load it.
        if not self.__asm:
            self.read_code(inp)
        # remove comments from loaded assembly code.
        self.__rm_comments()
        # also remove __rm_comments 

        self.__first_pass()
        # do second pass.
        self.__second_pass()
        # The previous two calls should store the assembled binary
        # code inside self.__bin. So the final step is to return
        # self.__bin
        #self.printDebugInfo()
        outputFile = open("experimentalOutput.txt","w")
        for i in self.__bin.keys():
            outputFile.write(f"{i} {self.__bin[i]}\n")
        outputFile.close()
        return self.__bin


    # PRIVATE METHODS
    def __load_table(self, path) -> dict:
        """
        loads any of ISA tables (MRI, RRI, IOI)
        """
        with open(path, 'r') as f:
            t = [s.rstrip().lower().split() for s in f.readlines()]
        return {opcode:binary for opcode,binary in t}


    def __islabel(self, string) -> bool:
        """
        returns True if string is a label (ends with ,) otherwise False
        """
        return string.endswith(',')


    def __rm_comments(self) -> None:
        """
        remove comments from code
        """
        for i in range(len(self.__asm)):
            for j in range(len(self.__asm[i])):
                if self.__asm[i][j].startswith('/'):
                    del self.__asm[i][j:]
                    break

    def __format2bin(self, num:str, numformat:str, format_bits:int) -> str:
        """
        converts num from numformat (hex or dec) to binary representation with
        max format_bits. If the number after conversion is less than format_bits
        long, the formatted text will be left-padded with zeros.
        Arguments:
            num (str): the number to be formatted as binary. It can be in either
                        decimal or hexadecimal format.
            numformat (str): the format of num; either 'hex' or 'dec'.
            format_bits (int): the number of bits you want num to be converted to
        """
        if numformat == 'dec':
            return '{:b}'.format(int(num)).zfill(format_bits)
        elif numformat == 'hex':
            return '{:b}'.format(int(num, 16)).zfill(format_bits)
        else:
            raise Exception('format2bin: not supported format provided.')
        
    #Function created by me 
    #Checks if the current line is the ORG pseudo instruction 
    def isOrg(self, inputString):
        if inputString == "org":
            return True
        else:
            return False

    def __first_pass(self) -> None:
        """
        Runs the first pass over the assmebly code in self.__asm.
        Should search for labels, and store the labels alongside their locations in
        self.__address_symbol_table. The location must be in binary (not hex or dec).
        Returns None
        """
        #First we shall initailize the location counter 
        #If the first line is ORG, then we will set the LC to that. If not, then leave it as 0
        if self.__asm[0][0] == "org":
            self.locationCounter = hex(int(self.__asm[0][1], 16)) 
        
        #First we shall check for labels and store them self.__address_symbol_table
        for line in self.__asm:
            if self.__islabel(line[0]) == True: #if it is a label 
                self.__address_symbol_table[line[0][0:-1]] = self.locationCounter
                self.locationCounter = hex(int(self.locationCounter,16) + 1)
            elif self.isOrg(line[0]):
                self.locationCounter = hex(int(line[1], 16))
            else:
                self.locationCounter = hex(int(self.locationCounter,16) + 1)



    def __second_pass(self) -> None:
        """
        Runs the second pass on the code in self.__asm.
        Should translate every instruction into its binary representation using
        the tables self.__mri_table, self.__rri_table and self.__ioi_table. It should
        also store the translated instruction's binary representation alongside its 
        location (in binary too) in self.__bin.
        """
        self.locationCounter = 0
        lineCounter = 1
        for line in self.__asm: # looping on each line in the asm input 
            innerCounter = 0
            for obj in line: 
                # first check if its a pseudo instruction 
                if obj in self.pseudoInstructions: 
                    binaryAddress = self.__format2bin(str(self.locationCounter),"hex",12)
                    if self.isOrg(obj): # if its org then change the location counter
                        self.locationCounter = hex(int(line[1], 16)) # this might cause issues
                        break
                    elif obj == "hex":
                        #print(f"PROBLEMATIC VALUE: {str(line[1])}")
                        #print(f"LINE VALUE: {line}")
                        self.__bin[binaryAddress] = self.__format2bin(str(line[1 + innerCounter]),"hex",16)
                        self.locationCounter = hex(int(self.locationCounter, 16) + 1)
                        break
                    elif obj == "dec":  
                        self.__bin[binaryAddress] = self.__format2bin(str(line[1 + innerCounter]),"dec",16)
                        self.locationCounter = hex(int(self.locationCounter, 16) + 1)
                        break
                    elif obj == "end":
                        return 
                    else:
                        continue

                elif obj in self.__mri_table:
                    # The process of assembling a mri instruction is a lot more involved
                    # We first need to know if its a direct or an indirect refrence 
                 
                    opCode = self.__mri_table[obj]
                    tmpIndex = line.index(obj)
                    
                    # If this fails then its because there was no address provided and thus
                    # it is a syntax error
                    adressPart = ""
                    try:
                        if "i" in line:
                            adressingMode = "1"
                            adressPart = self.__format2bin(str(self.__address_symbol_table[line[tmpIndex + 1]]), "hex", 12)
                        else:
                            adressingMode = "0"
                            if line[tmpIndex + 1] == "dec":
                                # tmpIndex + 2 because tmpIndex + 1 is the word itself
                                adressPart = self.__format2bin(line[tmpIndex + 2], "dec", 12)
                            elif line[tmpIndex + 1] == "hex":
                                adressPart = self.__format2bin(line[tmpIndex + 2], "hex", 12)

                            # if its not hex or dec then its a label
                            else:
                                hexAdress = self.__address_symbol_table[line[tmpIndex + 1]]
                                # Now its in binary not hex
                                adressPart = self.__format2bin(str(hexAdress), "hex", 12)
                    except Exception as e:
                        print(f"SYNTAX ERROR AT LINE (NO ADRESS PROVIDED): {lineCounter}")
                        # Get the exception information
                        exc_type, exc_value, exc_traceback = sys.exc_info()

                        # Print the custom error message and line number
                        print(f"An error occurred: {e} at line {exc_traceback.tb_lineno}")

                        # Print the full traceback
                        traceback.print_exc()
                    finalInstruction = adressingMode + opCode + adressPart
                    binaryAddress = self.__format2bin(str(self.locationCounter), "hex", 12)
                    # tr used to not exist and it used to be binaryAddress
                    self.__bin[binaryAddress] = finalInstruction
                    self.locationCounter = hex(int(self.locationCounter, 16) + 1)
                    break
                else:   
                    # then its a RRI or a IOI, so we just put its binary equivlant in the output 
                    binaryAddress = self.__format2bin(str(self.locationCounter), "hex", 12)
                    if obj in self.__rri_table:
                        self.__bin[binaryAddress] = self.__rri_table[obj]
                        self.locationCounter = hex(int(self.locationCounter,16) + 1)
                        break
                    elif obj in self.__ioi_table:
                        self.__bin[binaryAddress] = self.__ioi_table[obj]
                        self.locationCounter = hex(int(self.locationCounter, 16) + 1)
                        break
                    elif self.__islabel(obj):
                        innerCounter += 1
                        continue

                    else:
                        print(f"SYNTAX ERROR AT LINE: {lineCounter}")
                        return
                 
                innerCounter = 0
            lineCounter += 1

    #created by me for debugging
    def printDebugInfo(self) -> None:
        # print ASM for debugging
        print(f"TYPE OF self.locationCounter: {type(self.locationCounter)}")
        print("ASM INPUT: ")
        for line in self.__asm:
            print(line)
        print(f"Type of ASM INPUT: {type(self.__asm)}")
        print("")
        
        print("SELF.BIN CONTENTS")
        for line in self.__bin.items():
            print(line)
        print(f"Type of self.__bin: {type(self.__bin)}")
        print("")

        print("SELF.ADRESS.SYMBOLTABLE contents")
        for line in self.__address_symbol_table.items():
            print(line)
        print(f"Type of self.__address_symbol_table: {type(self.__address_symbol_table)}")
        print("")

        print("MRI TABLE CONTENTS: ")
        for line in self.__mri_table.items():
            print(line)
        print(f"Type of self.__mri_table: {type(self.__mri_table)}")
        print("")

        print("RRI TABLE CONTENTS: ")
        for line in self.__rri_table.items():
            print(line)
        print(f"Type of self.__rri_table: {type(self.__rri_table)}")
        print("")

        print("IOI TABLE CONTENTS: ")
        for line in self.__ioi_table.items():
            print(line)
        print(f" Type of self.__ioi_table: {type(self.__ioi_table)}")
        print("")



