#!/usr/bin/env python
#     Copyright 2015, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Python test originally created or extracted from other peoples work. The
#     parts from me are licensed as below. It is at least Free Softwar where
#     it's copied from other people. In these cases, that will normally be
#     indicated.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#

from __future__ import print_function

import os, sys, tempfile, subprocess

search_mode = len( sys.argv ) > 1 and sys.argv[1] == "search"

start_at = sys.argv[2] if len(sys.argv) > 2 else None

if start_at:
    active = False
else:
    active = True

os_path = os.path.normcase(os.path.dirname(os.__file__))

print("Using standard library path", os_path)

try:
    import numpy

    extra_path = os.path.normcase(
        os.path.dirname(
            os.path.dirname(
                numpy.__file__
            )
        )
    )

    print("Using extra library path", extra_path)
except ImportError:
    extra_path = os_path

try:
    import matplotlib

    extra_path2 = os.path.normcase(
        os.path.dirname(
            os.path.dirname(
                matplotlib.__file__
            )
        )
    )

    print("Using extra2 library path", extra_path2)
except ImportError:
    extra_path2 = os_path

os_path = os.path.normpath(os_path)
extra_path = os.path.normpath(extra_path)

tmp_dir = tempfile.gettempdir()

# Try to avoid RAM disk /tmp and use the disk one instead.
if tmp_dir == "/tmp" and os.path.exists("/var/tmp"):
    tmp_dir = "/var/tmp"

stage_dir = os.path.join(tmp_dir, "compile_library")

blacklist = (
    "__phello__.foo.py", # Triggers error for "." in module name
)

def compilePath(path):
    global active

    for root, _dirnames, filenames in os.walk(path):
        filenames = [
            filename
            for filename in filenames
            if filename.endswith(".py")
            if filename not in blacklist
        ]

        for filename in sorted(filenames):
            if "(" in filename:
                continue

            path = os.path.join(root, filename)

            if not active and start_at in ( filename, path ):
                active = True

            if not active:
                continue

            command = [
                sys.executable,
                os.path.join(
                    os.path.dirname( __file__ ),
                    "..",
                    "..",
                    "bin",
                    "nuitka"
                ),
                "--module",
                "--output-dir",
                stage_dir,
                "--recurse-none",
                "--remove-output"
            ]

            command += os.environ.get("NUITKA_EXTRA_OPTIONS", "").split()

            command.append(path)
            print(path, ":", end = " ")
            sys.stdout.flush()

            subprocess.check_call(command)

            print("OK")

            if os.name == "nt":
                suffix = "pyd"
            else:
                suffix = "so"

            target_filename = os.path.basename(path).replace(".py","."+suffix)
            target_filename = target_filename.replace("(","").replace(")","")

            os.unlink(
                os.path.join(
                    stage_dir, target_filename
                )
            )

compilePath(os_path)

if extra_path != os_path:
    compilePath(extra_path)

if extra_path2 not in (os_path, extra_path):
    compilePath(extra_path2)
