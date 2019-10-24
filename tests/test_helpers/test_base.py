# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""This module contains the tests for the helper module."""

import sys

from aea.helpers.base import locate


class TestHelpersBase:
    """Test the helper functions."""

    def test_locate(self):
        """Test the locate function."""
        sys.modules["gym_connection"] = locate("packages.connections.gym")
        assert sys.modules['gym_connection'] is not None
        sys.modules["gym_connection"] = locate("packages.connections.weather")
        assert sys.modules['gym_connection'] is None
