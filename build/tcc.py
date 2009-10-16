# Base Class for Tiny C Compiler
# Written by:       Tres Walsh <tres.walsh@mnmlstc.com>
# Maintained by:    Tres Walsh <tres.walsh@mnmlstc.com>

from system import System

class TCC(System):
    '''Tiny C Compiler Class'''

    def cc(self):
        return 'tcc'

    def cxx_extension(self):
        return 'no_cpp_extension'
