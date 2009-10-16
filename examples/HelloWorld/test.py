from build.system import System
from build.utils import *

project_name = 'test'

class Windows(System):

    def pre_build(self):
        self.add_source_directory('src')
        self.add_include_directory('inc')

    def cxx(self):
        return 'g++'

    def binary(self):
        return self.project_name + '.exe'

if __name__ == '__main__':
    Windows(project_name).start()
    wait()
