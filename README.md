pyubic a.k.a. uPy
=================

- is a general abstract layer we developp for easy UI making in Blender, C4D and Maya. pyubic is intend to be a universal API for creating buttons and layout for theses three software. 
- is an abstract layer for creating/editing geometry using the same API inside the previous cited three software.
- is pure python and doesn't require compilation.
- Currently supports:
    * Blender2.49b
    * Cinema4D R12
    * Maya 2011


Installation
------------

#### Download the archive and extract it:

```
tar -xzvf corredD-pyubic-5f91079.tar.gz
mv corredD-pyubic-5f91079 pyubic
```


#### Or clone the git repository:

```
git clone https://corredD@github.com/corredD/pyubic.git
cd pyubic
sudo python setup.py install
```

This will install pyubic in the site-package of your python distribution.  
Alternatively you can manually copy the pyubic directory in the directory of your choice and add it in your python path manually (ie see the examples).


Getting Started
---------------

- Check the example
- Open the 3d software python console and type:

```
import pyubic
helperClass = pyubic.getHelperClass()
helper = helperClass()
sp = helper.Sphere('mySphere',res = 12)
```


To Do
-----

- [ ] API documentation
- [ ] Possible Names
    - biq
    - ecumenic
    - omnis
    - biApi
    - ubic
    - pyubic

