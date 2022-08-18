#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

import pytest

@pytest.fixture
def thisdash(dash_br):
    dash_br.server_url = "https://localhost:8050"

    yield dash_br
