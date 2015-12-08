##
# Copyright 2009-2015 Ghent University
#
# This file is part of EasyBuild,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/easybuild
#
# EasyBuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
EasyBuild support for installing the Intel Performance Primitives (IPP) library, implemented as an easyblock

@author: Stijn De Weirdt (Ghent University)
@author: Dries Verdegem (Ghent University)
@author: Kenneth Hoste (Ghent University)
@author: Pieter De Baets (Ghent University)
@author: Jens Timmerman (Ghent University)
@author: Lumir Jasiok (IT4Innovations)
"""

import os
import platform


from distutils.version import LooseVersion
from easybuild.easyblocks.generic.intelbase import INSTALL_MODE_NAME_2015, INSTALL_MODE_2015
from easybuild.easyblocks.generic.intelbase import IntelBase, ACTIVATION_NAME_2012, LICENSE_FILE_NAME_2012


class EB_ipp(IntelBase):
    """
    Support for installing Intel Integrated Performance Primitives library
    """
    def install_step(self):
        """
        Actual installation
        - create silent cfg file
        - execute command
        """

        machine = platform.machine()
        if machine == "i386":
            self.arch = "ia32"
        else:
            self.arch = "intel64"
        
        silent_cfg_names_map = None

        if LooseVersion(self.version) < LooseVersion('8.0'):
            silent_cfg_names_map = {
                'activation_name': ACTIVATION_NAME_2012,
                'license_file_name': LICENSE_FILE_NAME_2012,
            }

        if LooseVersion(self.version) < LooseVersion('9.0'):
            silent_cfg_names_map = {
                'install_mode_name': INSTALL_MODE_NAME_2015,
                'install_mode': INSTALL_MODE_2015,
            }
        # In case of IPP 2016 we have to specify ARCH_SELECTED in silent.cfg
        if LooseVersion(self.version) > LooseVersion('9.0'):
            silent_cfg_extras = {
                'ARCH_SELECTED': self.arch.upper()
            }

        super(EB_ipp, self).install_step(silent_cfg_names_map=silent_cfg_names_map, silent_cfg_extras=silent_cfg_extras)

    def sanity_check_step(self):
        """Custom sanity check paths for IPP."""

        if LooseVersion(self.version) < LooseVersion('8.0'):
            dirs = ["compiler/lib/intel64", "ipp/bin", "ipp/include",
                    "ipp/interfaces/data-compression", "ipp/tools/intel64"]
        elif LooseVersion(self.version) > LooseVersion('9.0'):
            dirs = ["ipp/bin", "ipp/include", "ipp/tools/intel64"]
        else:
            dirs = ["composerxe/lib/intel64", "ipp/bin", "ipp/include",
                    "ipp/tools/intel64"]
        
        if LooseVersion(self.version) >= LooseVersion('9.0'):
            custom_paths = {
                'files': ["ipp/lib/intel64/libipp%s" % y
                    for x in ["cc", "ch", "core", "cv", "dc", "i", "s", "vm"]
                    for y in ["%s.a" % x, "%s.so" % x]],
                'dirs': dirs
            }
 
        else:
            custom_paths = {
                'files': ["ipp/lib/intel64/libipp%s" % y
                    for x in ["ac", "cc", "ch", "core", "cv", "dc", "di",
                              "i", "j", "m", "r", "s", "sc", "vc", "vm"]
                    for y in ["%s.a" % x, "%s.so" % x]],
                'dirs': dirs
            }

        super(EB_ipp, self).sanity_check_step(custom_paths=custom_paths)

    def make_module_req_guess(self):
        """
        A dictionary of possible directories to look for
        """
        guesses = super(EB_ipp, self).make_module_req_guess()

        if LooseVersion(self.version) > LooseVersion('9.0'):
            lib_path = os.path.join('lib', self.arch)
            include_path = 'ipp/include'
 
            guesses.update({
                'LD_LIBRARY_PATH': [lib_path],
                'LIBRARY_PATH': [lib_path],
                'CPATH': [include_path],
                'INCLUDE': [include_path],
            })

        return guesses
