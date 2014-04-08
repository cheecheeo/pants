# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (nested_scopes, generators, division, absolute_import, with_statement,
                        print_function, unicode_literals)

from pants.base.build_manual import manual
from pants.targets.jvm_target import JvmTarget


@manual.builddict(tags=["jvm"])
class Benchmark(JvmTarget):
  """A caliper benchmark.

  Run it with the ``bench`` goal.
  """

  # def __init__(self, **kwargs):
  #   """
  #   :param string name: The name of this target, which combined with this
  #     build file defines the target :class:`pants.base.address.Address`.
  #   :param sources: A list of filenames representing the source code
  #     this library is compiled from.
  #   :type sources: list of strings
  #   :param java_sources:
  #     :class:`pants.targets.java_library.JavaLibrary` or list of
  #     JavaLibrary targets this library has a circular dependency on.
  #     Prefer using dependencies to express non-circular dependencies.
  #   :param dependencies: List of :class:`pants.base.target.Target` instances
  #     this target depends on.
  #   :type dependencies: list of targets
  #   :param excludes: List of :class:`pants.targets.exclude.Exclude` instances
  #     to filter this target's transitive dependencies against.
  #   :param resources: An optional list of ``resources`` targets containing text
  #     file resources to place in this module's jar.
  #   :param exclusives: An optional map of exclusives tags. See CheckExclusives for details.
  #   """
  #   super(Benchmark, self).__init__(**kwargs)
