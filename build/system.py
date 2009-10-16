# Base Class for Unix Based C/C++ compilers
# Written by:       Tres Walsh <tres.walsh@mnmlstc.com>
# Maintained by:    Tres Walsh <tres.walsh@mnmlstc.com>

import os
import sys
import shutil
import hashlib
import datetime
import threading
from glob import glob

from utils import * 

class System(threading.Thread):
    '''
        The base Unix build class. Named system because it is assumed that most
        projects will use a unix style compiler (such as gcc)
    '''

    def __init__(self, project_name):
        threading.Thread.__init__(self)
        self.failure = 0
        self.project_name = project_name
        self.platform_name = self.system_name()
        self.cxx_extension = self.cxx_extension()
        self.binary = self.binary()
        self.cxx = self.cxx()
        self.cc = self.cc()
        self.ar = self.ar()
        self.include_directories = []
        self.library_directories = []
        self.platform_libraries = []
        self.source_directories = []
        self.additional_flags = []
        self.libraries = []
        self.defines = []
        self.modules = []
        self.hash_list = [] # So we can access it from anywhere in the class

    def run(self):
        start_time = datetime.datetime.now()
        self.pre_build()
        return_value = self.compile_files()
        if not return_value == 0:
            error('\nError: ' + str(return_value))
            sys.exit(return_value)
        return_value = self.link()
        if not return_value == 0:
            error('\nError: ' + str(return_value))
            sys.exit(return_value)
        self.post_build()
        end_time = datetime.datetime.now()
        build_time = end_time - start_time
        cprint(self.platform_name + ': ' + str(build_time), green)

    def pre_build(self):
        '''
            This is where you set your project data
        '''
        pass

    def compile_files(self):
        '''
            Compiling step
        '''
        cprint('Compiling...', cyan)
        cc_list = []
        cxx_list = []
        if len(self.source_directories) > 1:
            warning('Only a central source directory is currently supported')
        source = self.source_directories.pop()
        if len(self.modules) == 0:
            self.add_module_directory('.')
        for module in self.modules:
            file_list = glob(source + '/' + module + '/*')
            file_list.sort()
            if not os.exists('HashList'):
                warning('Could not locate HashList')
            for file in file_list:
                if sys.platform == 'win32':
                    file = file.replace('\\', '/')
                if file.endswith(self.cxx_extension):
                    cxx_list.append(file)
                elif file.endswith('.c'):
                    cc_list.append(file)
                else:
                    warning(file + ' is not currently supported')
            cc_list.sort()
            cxx_list.sort()
            counter = 1
            flags = ''
            for include_directory in self.include_directories:
                flags += ' -I' + include_directory
            for definition in self.defines:
                flags += ' -D' + definition
            for flag in self.additional_flags:
                flags += ' ' + flag
            for file in cc_list:
                out_file = file.split('/')
                out_file = out_file.pop()
                percentage = 100 * float(counter)/float(len(cc_list))
                percentage = str(percentage)
                percentage = percentage.split('.')
                percentage.reverse()
                percentage = percentage.pop()
                if len(percentage) == 1:
                    percentage = ' 0' + percentage
                elif len(percentage) == 2:
                    percentage = ' ' + percentage
                cprint('[' + percentage + '%] CC: ' + out_file, magenta)
                out_file = self.platform_name + '_' + out_file + '.o'
                command = self.cc + ' -o ' + out_file + ' -c ' + file + flags
                return_value = os.system(command)
                if not return_value == 0:
                    return return_value
                try:
                    os.makedirs('object/' + self.platform_name + '/')
                except:
                    pass
                dest_file = out_file.replace(self.platform_name + '_', '')
                try:
                    shutil.copy(out_file, 'object/' +
                                self.platform_name + '/' + dest_file)
                except:
                    pass
                try:
                    os.remove(out_file)
                except:
                    pass
                counter += 1
            counter = 1
            for file in cxx_list:
                out_file = file.split('/')
                out_file = out_file.pop()
                out_file = self.platform_name + '_' + out_file + '.o'
                percentage = 100 * float(counter)/float(len(cxx_list))
                percentage = str(percentage)
                percentage = percentage.split('.')
                percentage.reverse()
                percentage = percentage.pop()
                if len(percentage) == 1:
                    percentage = ' 0' + percentage
                elif len(percentage) == 2:
                    percentage = ' ' + percentage
                cprint('[' + percentage + '%] CXX: ' + out_file, magenta)
                command = self.cxx + ' -o ' + out_file + ' -c ' + file + flags
                return_value = os.system(command)
                if not return_value == 0:
                   return return_value
                try:
                    os.makedirs('object/' + self.platform_name + '/')
                except:
                    pass
                dest_file = out_file.replace(self.platform_name + '_', '')
                try:
                    shutil.copy(out_file, 'object/' +
                                self.platform_name + '/' + dest_file)
                except:
                    pass
                try:
                    os.remove(out_file)
                except:
                    pass
                counter += 1
        return 0
            
    def link(self):
        '''
            Link Step
        '''
        cprint('Linking...', cyan)
        object_string = ''
        libdir_string = ''
        library_string = ''
        link_string = ''
        object_list = glob('object/' + self.platform_name + '/*')
        for object_file in object_list:
            object_string += ' ' + object_file
        for library in self.libraries:
            library_string += ' -l' + library
        for directory in self.library_directories:
            libdir_string += ' -L' + directory
        link_string = object_string + libdir_string + library_string
        command = self.cc + ' -o ' + self.binary + link_string
        cprint('LINK: ' + self.project_name, magenta)
        os.system(command)
        try:
            os.makedirs('build/' + self.platform_name + '/')
        except:
            pass
        try:
            shutil.copy(self.binary, 'build/' + self.platform_name + '/')
        except:
            return 1
        try:
            os.remove(self.binary)
        except:
            return 1
        return 0 # DON'T FORGET THE SEMI-COLON :V

    def post_build(self):
        pass

    def cc(self):
        return 'cc'

    def cxx(self):
        return 'cpp'

    def cxx_extension(self):
        return '.cpp'

    def ar(self):
        return 'ar'

    def hash_file(self, file):
        try:
            f = open(file, 'rb')
            h = hashlib.sha512()
            h.update(f.read())
            f.close()
            return h.hexdigest()
        
        except IOError:
            error('Could not open: ' + file)

    def system_name(self):
        x = str(self)
        x = x.split('(')
        x.reverse()
        x = x.pop()
        x = x.replace('<', '')
        x = x.replace('\n', '')
        return x

    def strip(self, binary):
        strip_util = which('strip')
        os.system(strip_util + ' ' + binary)

    def binary(self):
        return self.platform_name

    def add_flag(self, flag):
        if isinstance(flag, str):
            self.additional_flags.append(flag)
        elif isinstance(flag, list):
            for item in flag:
                self.additional_flags.append(item)
        else:
            warning(flag + ' is an unsupported datatype!')

    def add_library(self, library):
        if isinstance(library, str):
            self.libraries.append(library)
        elif isinstance(library, list):
            for lib in library:
                self.libraries.append(lib)
        else:
            warning(library + ' is an unsupported datatype!')

    def add_module_directory(self, directory):
        if isinstance(directory, str):
            self.modules.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                self.modules.append(dir)
        else:
            warning(directory + 'is an unsupported datatype!')

    def add_source_directory(self, directory):
        if isinstance(directory, str):
            self.source_directories.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                self.source_directories.append(dir)
        else:
            warning(directory + ' is an unsupported datatype!')

    def add_include_directory(self, directory):
        if isinstance(directory, str):
            self.include_directories.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                self.include_directories.append(dir)
        else:
            warning(directory + ' is an unsupported datatype!')

    def add_library_directory(self, directory):
        if isinstance(directory, str):
            self.library_directories.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                self.library_directories.append(dir)
        else:
            warning(define + ' is an unsupported datatype!')

    def add_define(self, define):
        if isinstance(define, str):
            self.define.append(define)
        elif isinstance(define, list):
            for definition in define:
                self.define.append(definition)
        else:
            warning(define + ' is an unsupported datatype!')
