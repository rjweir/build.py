# Base class for updating a repository
# Written by:       Tres Walsh <tres.walsh@mnmlstc.com>
# Maintained by:    Tres Walsh <tres.walsh@mnmlstc.com>

import os
import sys

from utils import *

class Repository:

    def __init__(self, repository_type):
        self.repository_type = repository_type
    
    def update(self):
        pass

    def check_revision(self):
        pass

