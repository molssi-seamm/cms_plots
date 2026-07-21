=======
History
=======
2026.7.20 -- Internal: development tooling
    * Added an ``update`` make target that syncs ``main`` and ``dev`` after a
      release.
    * Excluded the generated ``_version.py`` from the ``black`` lint/format
      targets in the Makefile, matching the other SEAMM packages, so ``make
      lint`` no longer flags it.

    No effect on the installed package.

2025.5.7 -- Bugfix: removing debug logging
    * Removed some debug logging that was getting output by e.g. the structure step.

2022.8.13 (13 August 2022)
--------------------------

* First release of a working version on PyPI.
