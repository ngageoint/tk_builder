Tk_Builder
==========
The goal encouraging this project was to introduce the capability for fast and simple prototyping 
to enable research. The decision was made to use [tkinter](https://docs.python.org/3/library/tkinter.html)
for this capability. The particulars of this choice are entirely pragmatic. Most
importantly, `tkinter` is well supported for essentially every architecture that
Python is supported, and there are no complicating factors in licensing, configuration,
or installation. 

For better or for worse, `tkinter` will work on essentially any government system with a viable 
Python environment right out of the box. The same cannot generally be said for the other popular 
GUI frameworks like QT, WX, or GTK. This provides a set tools for simple creation of graphical 
user interfaces for Python based on the tkinter library. The main focus for the GUIs is assumed 
to be on overhead imaging applications.

Origins
-------
This was developed to enable simple prototyping of graphical user interfaces useful in conjunction 
with SarPy project, and was developed at the National Geospatial-Intelligence Agency (NGA). 
The software use, modification, and distribution rights are stipulated within the MIT license.

Dependencies
------------
The core library functionality depends only on `numpy >= 1.9.0`, `pillow`, and
`matplotlib`, all of which can (now) be installed using conda or pip.

Python 2.7
----------
The development here has been geared towards Python 3.6 and above, but efforts have
been made towards remaining compatible with Python 2.7. If you are using the library
from Python 2.7, there is an additional dependencies for the `typing` and `future` 
(not to be confused with the more widely known `futures`) packages, easily installed using 
conda or pip.
