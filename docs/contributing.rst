Contributor's Guide
===================

.. contents::
   :local:
   :depth: 2

Introduction
------------

Anyone can contribute to the wasp-os project. Contributions are typically made
via github using the typical fork-and-pull-request approach. Contributors who
do not wish to use github are also welcome to share patches using
``git format-patch --to wasp-os@redfelineninja.org.uk`` and ``git send-email``.

All contributions must include a ``Signed-off-by`` tag added by the contributor
who submits the patch or patches. The ``Signed-off-by`` tag is added at the end
of the patch description and certifies that the contributor either wrote the
patch or has the right to share the code under the open source license
appropriate for the file being modified.

A ``Signed-off-by`` tag is an explicit statement that your contribution comes
under one of (a), (b), (c), or (d) from the list below so please be sure to
read carefully what you are certifying by adding your Signed-off-by.

Additionally please be aware that that contributors, like all other members of
the wasp-os community, are expected to meet the community guidelines described
in the project's code of conduct when interacting within all community spaces
(including the wasp-os github presence).

Developer Certificate of Origin
-------------------------------

.. literalinclude:: dco.txt
   :language: none
   :emphasize-lines: 1-2,13

This procedure is the same one used by the Linux kernel project. To sign off a
patch append an appropriate line at the end of the commit message:

.. code-block:: none

    Signed-off-by: Random Developer <r.developer@example.org>

Please use your real name, anonymous and pseudonymous contributions will not be
accepted.

.. include:: code_of_conduct.rst
