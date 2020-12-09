#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# This file is part of CERN Search.
# Copyright (C) 2018-2019 CERN.
#
# CERN Search is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

env_file="$1"
cmd="${@:2}"
bash -c "source $env_file && $cmd"