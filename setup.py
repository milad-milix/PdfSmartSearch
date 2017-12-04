'''
Created on Dec 3, 2017

@author: Milad
'''

import os
import sys
import datetime

from cx_Freeze import setup, Executable

# This is ugly. I don't even know why I wrote it this way.
def files_under_dir(dir_name):
    file_list = []
    for root, dirs, files in os.walk(dir_name):
        for name in files:
            file_list.append(os.path.join(root, name))
    return file_list


includefiles = []
for directory in ('static', 'templates', 'data'):
    includefiles.extend(files_under_dir(directory))

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

dt = datetime.datetime.now()

main_executable = Executable("api.py", base=base, icon="pdf.ico")
setup(name="Example",
      version="0.3." + dt.strftime('%m%d.%H%m'),
      description="Example Web Server",
      options={
          'build_exe': {
              'packages': ['jinja2.ext', 'email'],
              'include_files': includefiles,
              'include_msvcr': True}},
      executables=[main_executable], requires=['flask', 'wtforms'])