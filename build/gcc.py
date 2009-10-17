# Base Class for GCC Based C/C++ compilers
# Written by:       Tres Walsh <tres.walsh@mnmlstc.com>
# Maintained by:    Tres Walsh <tres.walsh@mnmlstc.com>

from system import System

class GCC(System):
    '''The base GCC class.'''

    def cc(self):
        return which('gcc')

    def cxx(self):
        return which('g++')
