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

The `ImagePanel` and `ImageCanvas` classes contain functionality to save figures to numpy arrays
and to disk.  For many user facing applications this would be accomplished by using the `save canvas`
button provided in an `ImagePanel`.  This features saved all image and vector data displayed within
an image panel.  If a user wishes to save figures this way, then it will be saved as a `postscript` 
or `.ps` file, which will probably be sort of useless without the `ghostscript` application.

Origins
-------
This was developed to enable simple prototyping of graphical user interfaces useful in conjunction 
with SarPy project, and was developed at the National Geospatial-Intelligence Agency (NGA). 
The software use, modification, and distribution rights are stipulated within the MIT license.

Dependencies
------------
The core library functionality depends only on `tkinter`, `numpy`, `pillow`,
`matplotlib`, `scipy`, and minor dependence on `sarpy`, all of which can be 
installed using conda or pip. Note that `tkinter` is part of the standard distribution 
on some platforms, and has to be installed separately on others.

Installation
------------
From PyPI, install using pip (may require escalated privileges e.g. sudo):
```bash
pip install tk_builder
```
Note that here `pip` represents the pip utility for the desired Python environment.

From the top level of a cloned version of this repository, install for all users of 
your environment (may require escalated privileges, e.g. sudo):
```bash
python setup.py install
```
Again, `python` here represents the executible associated with the desired Python 
environment.

For more verbose instructions for installing from source, such as how to perform an 
install applicable for your user only and requiring no escalated privileges, 
see [here](https://docs.python.org/3/install/index.html).
