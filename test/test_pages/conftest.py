#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: schorb
"""

import pytest
from dash.testing.application_runners import import_app


@pytest.fixture
def thisdash(dash_duo):
    app = import_app("dashUI.app")
    dash_duo.start_server(app)

    yield dash_duo