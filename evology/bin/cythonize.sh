#!/usr/bin/env bash
import sys

if sys.platform == "darwin":
    python3 compile_cython_files.py build_ext --inplace

if sys.platform == "win32":
    python compile_cython_files.py build_ext --inplace

