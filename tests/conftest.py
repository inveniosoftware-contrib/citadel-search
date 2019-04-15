# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

def pytest_addoption(parser):
    parser.addoption("--endpoint", action="store",
                     default="https://dev-cern-search.web.cern.ch/")
    parser.addoption("--api_key", action="store",
                     default="XXXXKKKKKZZZZWWWW")


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    endpoint_value = metafunc.config.option.endpoint
    if 'endpoint' in metafunc.fixturenames and endpoint_value is not None:
        metafunc.parametrize("endpoint", [endpoint_value])
    api_key_value = metafunc.config.option.api_key
    if 'api_key' in metafunc.fixturenames and api_key_value is not None:
        metafunc.parametrize("api_key", [api_key_value])