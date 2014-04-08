# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

import os
import unittest
from contextlib import contextmanager
from textwrap import dedent

import pytest
from twitter.common.contextutil import pushd, temporary_dir
from twitter.common.dirutil import touch

from pants.base.address import BuildFileAddress, SyntheticAddress
from pants.base.build_environment import set_buildroot
from pants.base.build_file import BuildFile
from pants.base.build_file_parser import BuildFileParser
from pants.base.target import Target
from pants.graph.build_graph import BuildGraph


class BuildGraphTest(unittest.TestCase):
  @contextmanager
  def workspace(self, *buildfiles):
    with temporary_dir() as root_dir:
      set_buildroot(root_dir)
      with pushd(root_dir):
        for buildfile in buildfiles:
          touch(os.path.join(root_dir, buildfile))
        yield os.path.realpath(root_dir)

  def test_transitive_closure_spec(self):
    class FakeTarget(Target):
      def __init__(self, *args, **kwargs):
        super(FakeTarget, self).__init__(*args, payload=None, **kwargs)

    with self.workspace('./BUILD', 'a/BUILD', 'a/b/BUILD') as root_dir:
      with open(os.path.join(root_dir, './BUILD'), 'w') as build:
        build.write(dedent('''
          fake(name="foo",
               dependencies=[
                 'a',
               ])
        '''))

      with open(os.path.join(root_dir, 'a/BUILD'), 'w') as build:
        build.write(dedent('''
          fake(name="a",
               dependencies=[
                 'a/b:bat',
               ])
        '''))

      with open(os.path.join(root_dir, 'a/b/BUILD'), 'w') as build:
        build.write(dedent('''
          fake(name="bat")
        '''))

      parser = BuildFileParser(root_dir=root_dir,
                               exposed_objects={},
                               path_relative_utils={},
                               target_alias_map={'fake': FakeTarget})

      build_graph = BuildGraph()
      parser.inject_spec_closure_into_build_graph(':foo', build_graph)
      self.assertEqual(len(build_graph.dependencies_of(SyntheticAddress(':foo'))), 1)
      print build_graph.sorted_targets()
