# Base Class for Unix Based C/C++ Compilers
# Written by:       Tres Walsh <tres.walsh@mnmlstc.com>
# Maintained by:    Tres Walsh <tres.walsh@mnmlstc.com>

import os
import sys
import shutil
import datetime
import threading 
import subprocess
from glob import glob

from utils import *

class System(threading.Thread):
    ''' Base Unix CC/CXX Class '''

    def __init__(self, project_name, unity=False):
        threading.Thread.__init__(self)
        self.unity = unity # For unity builds
        self.project_name = project_name
        self.platform_name = self.system_name()
        self.cxx_extension = self.cxx_extension()
        self.binary = self.binary()
        self.cxx = self.cxx()
        self.cc = self.cc()
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
        if self.unity == True:
            cprint('Unity build is in effect', green)
            return_value = self.unity_build()
            if not return_value == 0:
                error('\nError: %s' % return_value)
            sys.exit(return_value)
        return_value = self.compile_files()
        if not return_value == 0:
            error('\nError: %s' % return_value)
            sys.exit(return_value)
        return_value = self.link()
        if not return_value == 0:
            error('\nError: %s' % return_value)
            sys.exit(return_value)
        self.post_build()
        end_time = datetime.datetime.now()
        build_time = end_time - starttime
        cprint('%s: %s' % (self.platform_name, build_time), green)

    def pre_build(self):
        ''' Prebuild steps '''

    def compile_files(self):
        ''' Compiling Step '''
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
            self.hash_file.close()
        self.hash_file = open('HashList', 'r')
        for line in self.hash_list:
            line = line.replace('\n', '')
            line = line.split(':')
            if not len(line[1]) == 128:
                warning('Corrupt hash detected!')
            else:
                hash_list.append(line)
        self.hash_list = tuple(hash_list)
        self.hash_list = dict(hash_list)
        for module in self.modules:
            file_list = glob('%s/%s/*' % (source, module))
            if system_type() == 'windows':
                for file in file_list:
                    file_list.remove(file)
                    file = file.replace('\\', '/')
                    file_list.append(file)
                    file_list.sort()
            else:
                file_list.sort()
            object_check = file.split('/')
            object_check = object_check.pop() + '.o'
            for file in file_list:
                if not (file in hash_list and \
                        hash_file(file) == hash_list[file] and \
                        os.path.exists('object/%s/%s/%s' %
                                       (self.platform_name,
                                        module, object_check)) and \
                        os.path.isfile('object/%s/%s/%s' %
                                       (self.platform_name,
                                        module, object_check))):
                    if file.endswith('.c'):
                        cc_list.append(file)
                    [cxx_list.append(file) \
                     for extension in self.cxx_extension \
                     if file.endswith(extension)]
        cc_list.sort()
        cxx_list.sort()
        counter = 1
        flags = ''
        flags += format_options(self.include_directories, '-I')
        flags += format_options(self.defines, '-D')
        flags += format_options(self.additional_flags)
        for file in cc_list:
            module = ''
            out_file = file.split('/')
            if source in out_file:
                out_file.remove(source)
            module_list = out_file
            out_file = out_file.pop()
            module_list.pop()
            if not len(module_list) == 1:
                module = '/'.join(module_list)
            else:
                module = module_list.pop()
            percentage = 100 * float(counter)/float(len(cc_list))
            cprint('[%3.0f%%] CC: %s' % (percentage, out_file), magenta)
            out_file = '%s_%s.o' % (self.platform_name, out_file)
            command = '%s -o %s -c %s%s' % (self.cc, out_file, file, flags)
            return_value = subprocess.call(command)
            if not return_value == 0:
                return return_value
            try:
                os.makedirs('object/%s/%s/' % (self.platform_name, module))
            except OSError:
                pass
            dest_file = out_file.replace(self.platform_name + '_', '')
            try:
                shutil.copy(out_file, 'object/%s/%s/%s' %
                            (self.platform_name, dest_file))
            except IOError:
                return 10
            try:
                os.remove(out_file)
            except OSError:
                return 20
            self.hash_write.append(file)
            counter += 1
        counter = 1
        for file in cxx_list:
            module = ''
            out_file = file.split('/')
            if source in out_file:
                out_file.remove(source)
            module_list = out_file
            out_file = out_file.pop()
            module_list.pop()
            if not len(module_list) == 1:
                module = '/'.join(module_list)
            else:
                mdoule = module_list.pop()
            percentage = 100 * float(counter)/float(len(cxx_list))
            cprint('[%3.0f%%] CC: %s' % (percentage, out_file), magenta)
            out_file = '%s_%s.o' % (self.platform_name, out_file)
            command = '%s -o %s -c %s%s' % (self.cxx, out_file, file, flags)
            return_value = subprocess.call(command)
            if not return_value == 0:
                return return_value
            try:
                os.makedirs('object/%s/%s/' % (self.platform_name, module))
            except OSError:
                pass
            dest_file = out_file.replace(self.platform_name + '_', '')
            try:
                shutil.copy(out_file, 'object/%s/%s/%s' %
                            (self.platform_name, dest_file))
            except IOError:
                return 10
            try:
                os.remove(out_file)
            except OSError:
                return 20
            self.hash_write.append(file)
            counter += 1
        try:
            for item in self.hash_write:
                self.hash_file.write('%s:%s\n' % (item, hash_file(item)))
            self.hash_file.close()
        except IOError:
            return 40
        return 0

    def link(self):
        ''' Link step '''
        object_string = ''
        libdir_string = ''
        library_string = ''
        link_string = ''
        for module in self.modules:
            object_list = glob('object/%s/%s/*' % (self.platform_name, module))
            object_string += format_options(object_list)
        library_string = format_options(self.libraries, '-l')
        libdir_string = format_options(self.library_directories, '-L')
        link_string = object_string + libdir_string + library_string
        command = '%s -o %s%s' % (self.cxx, self.binary, link_string)
        cprint('LINK: %s' % self.project_name, magenta)
        subprocess.call(command)
        try:
            os.makedirs('build/%s/' % self.platform_name)
        except OSError:
            pass
        try:
            shutil.copy2(self.binary, 'build/%s/' % self.platform_name)
        except IOError:
            return 10
        try:
            os.remove(self.binary)
        except OSError:
            return 20
        return 0 #; A semi-colon, for protection :D

    def post_build(self):
        pass

    def unity_build(self):
        pass

    def cc(self):
        return which('cc')

    def cxx(self):
        return which('c++')

    def cxx_extension(self):
        return ['.cpp', '.C', '.cc', '.cxx']

    def system_name(self):
        x = str(self)
        x = x.split('(')
        x = x.pop(0)
        x = x.replace('<', '')
        x = x.replace('\n', '')
        return x

    def binary(self):
        if system_type() == 'windows':
            exe_extension = '.exe'
        elif system_type() == 'macosx':
            exe_extension = '.mach'
        elif system_type() == 'linux':
            exe_extension = '.elf'
        else:
            error('Something went wrong!')
        return '%s%s' % (self.preject_name, exe_extension)

    def strip(self, binary):
        strip_util = which('strip')
        subprocess.call('%s %s' % (strip_util, binary))

    def add_flag(self, flag):
        if isinstance(flag, basestring):
            self.additional_flags.append(flag)
        elif isinstance(flag, list):
            for item in flag:
                if isinstance(item, basestring):
                    self.additional_flags.append(item)
        elif isinstance(flag, tuple):
            for item in flag:
                if isinstance(item, basestring):
                    self.additional_flags.append(item)
        else:
            warning('%s is an unsupported datatype!' % flag)

    def add_library(self, library):
        if isinstance(library, basestring):
           self.libraries.append(library)
        elif isinstance(library, list):
            for lib in library:
                if isinstance(lib, basestring):
                    self.libraries.append(lib)
        elif isinstance(library, tuple):
            for lib in library:
                if isinstance(lib, basestring):
                    self.libraries.append(lib)
        else:
            warning('%s is an unsupported datatype!' % library)

    def add_module_directory(self, directory):
        if isinstance(directory, basestring):
            self.modules.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                if isinstance(dir, basestring):
                    self.modules.append(dir)
        elif isinstance(directory, tuple):
            for dir in directory:
                if isinstance(dir, basestring):
                    self.modules.append(dir)
        else:
            warning('%s is an unsupported datatype!' % directory)

    def add_source_directory(self, directory):
        if isinstance(directory, basestring):
            self.source_directories.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                if isinstance(dir, basestring):
                    self.source_directories.append(dir)
        elif isinstance(directory, tuple):
            for dir in directory:
                if isinstance(dir, basestring):
                    self.source_directories.append(dir)
        else:
            warning('%s is an unsupported datatype!' % directory)

    def add_include_directory(self, directory):
        if isinstance(directory, basestring):
            self.include_directories.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                if isinstance(dir, basestring):
                    self.include_directories.append(dir)
        elif isinstance(directory, tuple):
            for dir in directory:
                if isinstance(dir, basestring):
                    self.include.directories.append(dir)
        else:
           warning('%s is an unsupported datatype!' % directory)

    def add_library_directory(self, directory):
        if isinstance(directory, basestring):
            self.include_directories.append(directory)
        elif isinstance(directory, list):
            for dir in directory:
                if isinstance(dir, basestring):
                    self.include_directories.append(dir)
        elif isinstance(directory, tuple):
            for dir in directory:
                if isinstance(dir, basestring):
                    self.include_directories.append(dir)
        else:
            warning('%s is an unsupported datatype!' % directory)

    def add_define(self, define):
        if isinstance(define, basestring):
            self.define.append(define)
        elif isinstance(define, list):
            for definition in define:
                if isinstance(definition, basestring):
                    self.define.append(definition)
        elif isinstance(define, tuple):
            for definition in define:
                if isinstance(definition, basestring):
                    self.define.append(definition)
        else:
            warning('%s is an unsupported datatype!' % directory)


