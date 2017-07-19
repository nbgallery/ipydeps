# ipydeps

A friendly wrapper around pip for installation of packages directly within Jupyter notebooks.

## Usage

You can install individual packages like so.

```python
import ipydeps
ipydeps.pip('numpy')
import numpy as np
```

You can also install multiple packages by passing a list.

```python
import ipydeps
ipydeps.pip(['pymc', 'beautifulsoup4'])
from pymc import DiscreteUniform
from bs4 import BeautifulSoup
```

If you want more verbose output from pip, just set the ```verbose``` parameter to ```True```.

```python
import ipydeps
ipydeps.pip('sklearn', verbose=True)
from sklearn.cluster import KMeans
```

## Configuration Files

### ipydeps.conf
pip options for your particular environment can be placed in ~/.config/ipydeps/ipydeps.conf.  For example, the following ipydeps.conf could be used to specify that you want ipydeps to trust a host, timeout after 30 seconds, and install all packages into user space:

```text
--trusted-host=my.pip.server.com
--user
--timeout=30
```

Some pip options have to be specified per-package.  ipydeps will take care of specifying the option for each package for you.  However, make sure you're working in a fully trusted environment before using these options.  Putting these two lines in your ipydeps.conf will basically turn off any of pip's built-in verification.

```text
--allow-external
--allow-unverified
```

If you were installing packages called "foo" and "bar" that you didn't want verified, then normally you'd have to pass ```--allow-external=foo --allow-external=bar --allow-unverified=foo --allow-unverified=bar```, but ipydeps will just fill these in for each package automatically if you simply put ```--allow-external``` and ```--allow-unverified``` in your ipydeps.conf.

### dependencies.link

Sometimes there's a better way to install certain packages, such as a pre-built rpm or apk.  ~/.config/ipydeps/dependencies.link contains a URL for a file that overrides ipydeps.pip() calls for certain packages.

For example, maybe you want to install numpy, so you call ipydeps.pip('numpy').  However, numpy can take a while to install from scratch.  If there's a pre-built version of numpy available, it can install in seconds instead of minutes.  

dependencies.link points to a dependencies.json file which maps the original package names to their overrides.

Only place a trusted link in your dependencies.link file, since dependencies.json could contain malicious commands that get executed as you.

Also note that all package names are handled in a case-insensitive manner (just like pip), so ipydeps will output a warning if it finds duplicate packages listed in your dependencies.json file.

### Windows support

ipydeps now supports Windows as well as Linux.  It will look for your home directory using `os.path.expanduser('~')`.  In most cases, this just points to C:\Users\yourname.  You should put your .config/ipydeps/ipydeps.conf file in that directory.

### pypki2 support

In some environments, having a PKI-enabled pip server is advantageous.  To that end, pypki2 integration is supported.  Simply add the following to ipydeps.conf:

```text
--use-pypki2
```
