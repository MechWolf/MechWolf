Installation
============

From PyPI (recommended)
-----------------------

On your computer
****************

MechWolf is available from `PyPI <https://pypi.org>`_, the Python Package Index.
Installation is a breeze. In your :ref:`virtualenv <virtualenv_instructions>`,
use the ``pip3`` command to install MechWolf::

    $ sudo pip3 install mechwolf[vis]

If you're just getting started, this is the installation we recommend.

On your client
**************

The previous command installs the the modules needed to visualize apparatuses
and protocols. These modules are heavy and require compilation if being run on
Raspberry Pis. In addition, it does not include the Python serial drivers, which
are only needed on the clients that will be physically connected to devices. To
install MechWolf with the serial drivers, run this command::

    $ sudo pip3 install mechwolf[client]

On your hub
***********

Similarly, the client variant does not include the code needed to run the hub.
To get the hub variant, run this command on your hub::

    $ sudo pip3 install mechwolf[hub]

Everything
**********

If you want to get all of the modules needed for *every* MechWolf function, run this command::

    $ sudo pip3 install mechwolf[client,hub,vis]

.. note::

    This will take a **long** time to compile on a Raspberry Pi.

If all these options are scaring you, go for this install since you'll have
every possible package. As the note above points out, don't try to do this
install on a computer with limited resources if you aren't comfortable waiting a
long time (on the order of hours) while the code needed to make graphs compiles.

Just the basics
***************

If you want the bare minimum for some reason (we're not sure why you would, though), run::

    $ sudo pip3 install mechwolf

What's with the brackets?
*************************

The brackets tell ``pip`` to install optional extras. Note that you can mix and
match the extras. If you want to get the code needed to run the hub and client
on the same device, you would use ``[hub,client]``.

From source
-----------

If you would like to use the development version of MechWolf, which is **not
guaranteed to be safe or stable**, you can install MechWolf directly from the
GitHub repository using the following command::

    $ git clone https://github.com/Benjamin-Lee/MechWolf.git

Change directory into MechWolf with::

    $ cd mechwolf

And run the installation command::

    $  sudo pip3 install -e .[client,hub,vis]
