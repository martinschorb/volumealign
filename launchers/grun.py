#! /usr/bin/env python
#
"""
This simple SessionBasedScript allows you to run a generic command and
will allow you to execute it in a sequential or in a parallel task
collection.

This is mainly used for testing and didactic purpouses, don't use it
on a production environment!
"""
# Copyright (C) 2012-2014, 2019 S3IT, Zentrale Informatik, University of Zurich. All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
from __future__ import absolute_import, print_function

import os
import os.path
import shlex

import gc3libs
import gc3libs.exceptions
from gc3libs import Application
from gc3libs.cmdline import SessionBasedScript


## main: run command-line

if "__main__" == __name__:
    import grun
    grun.GRunScript().run()


## aux application classes

class GRunApplication(Application):
    """
    An `Application` wrapper which will execute the arguments as a
    shell script command. This application will also check if some of
    the argument is a file, and in that case it will add it to the
    files to upload as input.
    """
    def __init__(self, arguments, **extra_args):
        # Fix path of the executable
        inputs = extra_args.get('inputs', [])
        shellargs = []
        
        for arg in arguments:
            shellargs.extend(shlex.split(arg))
            argpath = os.path.expandvars(os.path.expanduser(arg))
            if os.path.exists(argpath):
                inputs.append(argpath)
                
        Application.__init__(self,
                             arguments = ["bash", "-c", str.join(' ', shellargs)],
                             inputs = inputs,
                             outputs = gc3libs.ANY_OUTPUT,
                             stdout = "stdout.txt",
                             stderr = "stderr.txt",
                             **extra_args)


## the script definition

class GRunScript(SessionBasedScript):
    """
    Simple GC3Pie script to run a command.

    Allows also to run it multiple times, in parallel or sequentially.
    To be mainly used for testing purposes; for "production" runs,
    consider writing a specialized script.
    """
    version = '1.1.1'


    def new_tasks(self, extra):
        appextra = extra.copy()
        del appextra['output_dir']

        task = GRunApplication(self.params.args, **extra)

        return [task]

    def after_main_loop(self):
        print("")
        tasks = self.session.tasks.values()
        for app in tasks:
            if isinstance(app, TaskCollection):
                tasks.extend(app.tasks)
            if not isinstance(app, Application):
                continue
            print("===========================================")
            print("Application     %s" % app.jobname)
            print("  state:        %s" % app.execution.state)
            print("  command line: %s" % str.join(" ", app.arguments))
            print("  return code:  %s" % app.execution._exitcode)
            print("  output dir:   %s" % app.output_dir)