# Base Class for Unix Based C/C++ compilers
# Written by:       Tres Walsh <tres.walsh@mnmlstc.com>
# Maintained by:    Tres Walsh <tres.walsh@mnmlstc.com>

import os
import sys
import shutil
import datetime
import threading
from glob import glob

from utils import *

class System(threading.Thread):
    ''' Base Unix CC/CXX Class'''

    def __init__(self, project_name, unity=False):
        threading.Thread.__init__(self)
        self.unity = unity # For unity builds
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
        self.hash_list = []
        self.hash_write = []


    def run(self):
        start_time = datetime.datetime.now()
        self.pre_build()
        return_value = self.compile_files()
        if not return_value is 0:
            error('\nError: ' + str(return_value))
            sys.exit(return_value)
        return_value = self.link()
        if not return_value is 0:
            error('\nError: ' + str(return_value))
            sys.exit(return_value)
        self.post_build()
        end_time = datetime.datetime.now()
        build_time = end_time - start_time
        cprint(self.platform_name + ': ' + str(build_time), green)

    def pre_build(self):
        ''' Prebuild steps '''
        pass

    def compile_files(self):
        ''' Compiling Step '''
        if self.unity is True:
            cprint('Unity build is in effect', green)
            return_value = self.unity_build()
            return return_value
        cc_list = []
        cxx_list = []
        if len(self.source_directories) > 1:
            warning('Only a central source directory is currently supported')
        source = self.source_directories.pop()
        if len(self.modules) == 0:
            self.add_module_directory('.')
        if not (os.path.exists('HashList') and os.path.isfile('HashList')):
            warning('Could not locate HashList')
            self.hash_file = open('HashList', 'w')
        else:
            self.hash_file = open('HashList', 'r')
            for line in self.hash_list:
                line = line.replace('\n', '')
                line = line.split(':')
                if not len(line[1]) is 128:
                    warning('Corrupt hash detected! Skipping!')
                else:
                    hash_list.append(line)
            self.hash_list = tuple(hash_list)
            self.hash_list = dict(hash_list)
            for module in self.modules:
                file_list = glob('%s/%s/*' % (source, module))
                if system_type() is 'windows':
                    for file in file_list:
                        file_list.remove(file)
                        file = file.replace('\\', '/')
                        file_list.append(file)
                        file_list.sort()
                file_list.sort()
                object_check = file.split('/')
                object_check = object_check.pop() + '.o'
                for file in file_list:
                    if not (file in hash_list and \
                        hash_file(file) is hash_list[file] and \
                        os.path.exists('object/%s/%s' %
                                       (module, object_check)) and \
                        os.path.isfile('object/%s/%s' %
                                      (module, object_check))):
                        if file.endswith('.c'):
                            cc_list.append(file)
                        elif extension in self.cxx_extension is  \
                             file.endswith(extension):
                            self.cxx_list.append(file)
                        else:
                            warning('%s is not currently supported' % file)
                cc_list.sort()
                cxx_list.sort()
                counter = 1
                flags = ''
                for include_directory in self.include_directories:
                    flags += ' -I%s' % include_directory
                for definition in self.defines:
                    flags += ' -D%s' % definition
                for flag in self.additional_flags:
                    flags += ' %s' % flag
                for file in cc_list:
                    out_file = file.split('/')
                    out_file = out_file.pop()
                    percentage = 100 * float(counter)/float(len(cc_list))
                    cprint('[%3.0f%%] CC: %s' % (percentage, out_file),
                           magenta)
                    out_file = '%s_%s.o' % (self.platform_name, out_file)
                    command = '%s -o %s -c %s%s' % \
                              (self.cc, out_file, file, flags)
                    return_value = os.system(command)
                    if not return_value is 0:
                        return return_value
                    try:
                        os.makedirs('object/%s/' % self.platform_name)
                    except:
                        pass
                    dest_file = out_file.replace(self.platform_name + '_', '')
                    try:
                            shutil.copy(out_file, 'object/%s/%s' %
                                (self.platform_name, dest_file))
                    except:
                        return 10
                    try:
                        os.remove(out_file)
                    except:
                        return 20
                    self.hash_write.append(file)
                    counter += 1
                counter = 1
                for file in cxx_list:
                    out_file = file.split('/')
                    out_file = out_file.pop()
                    out_file = self.platform_name = '_' + out_file + '.o'
                    cprint('[%3.0f%%] CXX: %s' %
                           (percentage, out_file), magenta)
                    return_value = os.system('%s -o %s -c %s%s' %
                                             (self.cxx, out_file, file, flags))
                    if not return_value is 0:
                        return return_value
                    else:
                        self.hash_write.append(file)
                    try:
                        os.makedirs('object/%s/' % self.platform_name)
                    except:
                        pass
                    dest_file = out_file.replace(self.platform_name + '_', '')
                    try:
                        shutil.copy(out_file, 'object/%s/%s' %
                                    (self.platform_name, dest_file))
                    except:
                        return 10
                    try:
                        os.remove(out_file)
                    except:
                        return 20
                    self.hash_write.append(file)
                    counter += 1
                try:
                    for item in self.hash_write:
                        self.hash_file.write('%s:%s\n' %
                                             (item, hash_file(item)))
                    self.hash_file.close()
                except:
                    return 40
                return 0

    def link(self):
        ''' Link step '''
        object_string = ''
        libdir_string = ''
        library_string = ''
        link_string = ''
        object_list = glob('object/%s/*' % self.platform_name)
        for object_file in object_list:
            object_string += ' %s' % object_file
        for library in self.libraries:
            library_string += ' -l%s' % library
        for directory in self.library_directories:
            libdir_string += ' -L%s' % directory
        link_string = object_string + libdir_string + library_string
        command = '%s -o %s%s' % (self.cxx, self.binary, link_string)
        cprint('LINK: %s' % self.project_name, magenta)
        os.system(command)
        try:
            os.makedirs('build/%s/' % self.platform_name)
        except:
            pass
        try:
            shutil.copy(self.binary, 'build/%s/' % self.platform_name)
        except:
            return 10
        try:
            os.remove(self.binary)
        except:
            return 20
        return 0 #; I put a semi-colon there, for protection.

    def post_build(self):
        pass

    def unity_build(self):
        return 0

    def cc(self):
        ''' Returns the full path to the utility '''
        return which('cc')

    def cxx(self):
        return which('c++')

    def cxx_extension(self):
        return ['.cpp', '.C', '.cc', '.cxx']

    def ar(self):
        return which('ar')

    def system_name(self):
        x = str(self)
        x = x.split('(')
        x = x.pop(0)
        x = x.replace('<', '')
        x = x.replace('\n', '')
        return x

    def binary(self):
        if system_type() is 'windows':
            ext = '.exe'
        elif system_type() is 'macosx':
            ext = '.mach'
        elif system_type() is 'linux':
            ext = '.elf'
        else:
            error('Something went wrong!')
        return '%s%s' % (self.project_name, ext)

    def strip(self, binary):
        strip_util = which('strip')
        os.system('%s %s' % (strip_util, binary))

    def add_flag(self, flag):
        if isinstance(flag, str):
            self.additional_flags.append(flag)
        elif isinstance(flag, list):
            for item in flag:
                if isinstance(item, str): # No more checking after this!
                    self.additional_flags.append(item)
        else:
            warning('%s is an unsupported datatype!' % flag)

    def add_library(self, library):
        if isinstance(library, str):
           self.libraries.append(library)
        elif isinstance(library, list):
            for lib in library:
                if isinstance(lib, str):
                    self.libraries.append(lib)
        else:
            warning('%s is an unsupported datatype!' % library)

    def add_module_directory(self, directory):
        if isinstance(directory, str):
            self.modules.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                if isinstance(dir, str):
                    self.modules.append(dir)
        else:
            warning('%s is an unsupported datatype!' % directory)

    def add_source_directory(self, directory):
        if isinstance(directory, str):
            self.source_directories.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                if isinstance(dir, str):
                    self.source_directories.append(dir)
        else:
            warning('%s is an unsupported datatype!' % directory)

    def add_include_directory(self, directory):
        if isinstance(directory, str):
            self.include_directories.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                if isinstance(dir, str):
                    self.include_directories.append(dir)
        else:
           warning('%s is an unsupported datatype!' % directory)

    def add_library_directory(self, directory):
        if isinstance(directory, str):
            self.include_directories.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                if isinstance(dir, str):
                    self.include_directories.append(dir)
        else:
            warning('%s is an unsupported datatype!' % directory)

    def add_define(self, define):
        if isinstance(define, str):
            self.define.append(define)
        elif isinstance(define, list):
            for definition in define:
                if isinstance(definition, str):
                    self.define.append(definition)
        else:
            warning('%s is an unsupported datatype!' % directory)
