# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

python_library(
  name = 'engine_test_base',
  sources = ['base_engine_test.py'],
  dependencies = [
    pants('tests/python/pants_test:base_test'),
    pants('tests/python/pants_test/base:context_utils'),
    pants('src/python/pants/goal'),
  ]
)

python_test_suite(
  name = 'engine',
  dependencies = [
    pants(':test_engine'),
    pants(':test_round_engine'),
  ]
)

python_tests(
  name = 'test_engine',
  sources = ['test_engine.py'],
  dependencies = [
    pants(':engine_test_base'),
    pants('3rdparty/python:mox'),
    pants('src/python/pants/engine'),
  ],
)

python_tests(
  name = 'test_round_engine',
  sources = ['test_round_engine.py'],
  dependencies = [
    pants(':engine_test_base'),
    pants('src/python/pants/engine'),
    pants('src/python/pants/backend/core/tasks:common'),
  ],
)
