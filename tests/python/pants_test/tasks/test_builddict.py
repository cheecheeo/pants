# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from contextlib import closing
from StringIO import StringIO

from pants.backend.core.tasks import builddictionary
from pants.backend.core.register import build_file_aliases as register_core
from pants.backend.jvm.register import build_file_aliases as register_jvm
from pants.backend.python.register import build_file_aliases as register_python
from pants.base.build_configuration import BuildConfiguration
from pants.base.build_file_parser import BuildFileParser
from pants_test.tasks.test_base import BaseTest, TaskTest, prepare_task

OUTDIR = "/tmp/dist"

sample_ini_test_1 = """
[DEFAULT]
outdir: %s
""" % OUTDIR


class BaseBuildBuildDictionaryTest(TaskTest):
  def execute_task(self, config=sample_ini_test_1):
    with closing(StringIO()) as output:
      task = prepare_task(builddictionary.BuildBuildDictionary, config=config)
      task.execute()
      return output.getvalue()


class BuildBuildDictionaryTestEmpty(BaseBuildBuildDictionaryTest):
  def test_builddict_empty(self):
    """Execution should be silent."""
    # We don't care _that_ much that execution be silent. Nice if at least
    # one test executes the task and doesn't explode, tho.
    self.assertEqual('', self.execute_task())


class ExtractedContentSanityTests(BaseTest):
  @property
  def alias_groups(self):
    return register_core().merge(register_jvm().merge(register_python()))

  def setUp(self):
    super(ExtractedContentSanityTests, self).setUp()
    self._syms = builddictionary.assemble(build_file_parser=self.build_file_parser)

  def test_exclude_unuseful(self):
    # These symbols snuck into old dictionaries, make sure they don't again:
    for unexpected in ['__builtins__', 'Target']:
      self.assertTrue(unexpected not in self._syms.keys(), "Found %s" % unexpected)

  def test_sub_tocls(self):
    python_symbols = builddictionary.python_sub_tocl(self._syms).e

    # python_requirements goes through build_file_aliases.curry_context.
    # It's in the "Python" sub_tocl, but tenuously
    self.assertTrue("python_requirements" in python_symbols)

    # Some less-tenuous sanity checks
    for sym in ["python_library", "python_tests"]:
      self.assertTrue(sym in python_symbols)

    jvm_symbols = builddictionary.jvm_sub_tocl(self._syms).e
    for sym in ["java_library", "scala_library"]:
      self.assertTrue(sym in jvm_symbols)
