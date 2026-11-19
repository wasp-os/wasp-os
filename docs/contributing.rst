Contributor's Guide
===================

.. contents::
   :local:
   :depth: 2

Introduction
------------

Anyone can contribute to the wasp-os project. Contributions are typically made
via github using the typical fork-and-pull-request approach. Contributors who
do not wish to use github are welcome to share patches using ``git
format-patch --to wasp-os@redfelineninja.org.uk`` and ``git send-email``. In
both cases, the code will be reviewed by a project maintainer, so please
anticipate review comments and requests for changes. Typically pull
requests will not be merged if there are open questions or requests for
changes that have not been acted on.

All contributions are expected to pass the continuous-integration tests
before they can be accepted. Currently there are two checks:

1. The code is compiled for all supported devices. If you have been developing
   your code in the simulator it is a good idea to compile wasp-os for at least
   one of the supported devices before submitting a pull-request.

2. Automatic testing is performed using the simulator. The automatic tests
   include a mixture to static QA checks, self-test code and simple "does it
   run" tests on all applications. It is strongly recommended to run
   ``uv run make check`` and fix any reported problems before submitting a
   pull request. Alternatively, if you have your own github fork of wasp-os,
   then github can run these tests for you automatically every time you push
   a new branch to your fork.

By contributing you agree that your contribution is licensed under the same
license as the file it changes, which for most of wasp-os is the GNU Lesser
General Public License, version 3 or later. Only contribute code that you
wrote yourself or have the right to share under that license.

Additionally please be aware that that contributors, like all other members of
the wasp-os community, are expected to meet the community guidelines described
in the project's code of conduct when interacting within all community spaces
(including the wasp-os github presence).

Coding Style
------------

wasp-os uses a similar coding style as micropython and, in particular, Python
code is expected to follow :pep:`8`.

Git Hints and Tricks
--------------------

Updating a pull request
~~~~~~~~~~~~~~~~~~~~~~~

Review feedback is best folded into the original commits rather than added
as fix-up commits on top. For a single patch at the head of the current
branch (and shared as a github pull request) this can be handled fairly
easily:

.. code-block:: sh

    git commit --amend
    git push --force-with-lease <myfork> HEAD

Additionally, please be aware that github will not send out automatic
notifications to let the maintainer know that you have pushed an update to the
pull request. Follow up the above with a comment on the pull request thread
saying that your contribution has been updated and is ready for another look.

Code of Conduct
---------------

.. include:: code_of_conduct.rst
