# Epsilon
# Copyright (C) 2018
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import itertools
import pprint
import requests
import sys
import epsilon.util

ucd = "https://www.unicode.org/Public/10.0.0/ucd"

def fetch(path):
    properties = {}
    response = requests.get(path)
    response.raise_for_status()
    for line in response.text.splitlines():
        line = line.partition("#")[0]
        fields = [s.strip() for s in line.split(";")]
        if len(fields) > 1:
            codepoints, name = fields[:2]
            first, _, last = codepoints.partition("..")
            first, last = int(first, 16), int(last, 16) if last else None
            if name not in properties:
                properties[name] = []
            properties[name].append((first, last) if last else first)

    # canonicalize
    for name in properties:
        properties[name] = epsilon.util.IntegerSet(properties[name])

    return properties

print('''# This file is derived from the Unicode Data Files, and is licensed
# under the UNICODE, INC. LICENSE AGREEMENT - DATA FILES AND SOFTWARE.
# A copy of the licence is shipped with this software and may also be
# found online at http://unicode.org/copyright.html.
#
# This file is automatically generated. *** DO NOT EDIT ***

"""
Unicode 10.0.0 codepoint properties.
"""
''')
print("general_categories =\\")
pprint.pprint(fetch(ucd + "/extracted/DerivedGeneralCategory.txt"))