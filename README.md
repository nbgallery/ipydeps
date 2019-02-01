# ipydeps

A friendly way to specify your Jupyter notebook's dependencies right at the top of the notebook.
This helps ensure that other users have the Python packages they need to successfully run your notebook.

Unlike `!pip install`, ipydeps makes sure that the packages get installed into the same Python environment that's executing your notebook's code cells.
No more `!pip`, `!pip3`, `!pip -V` frustrations for you and your users.

It also includes features for installation accelerators via centrally-managed overrides, and PKI integration.

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

dependencies.link contains a URL pointing to a dependencies.json file which maps the original package names to their overrides.

Only place a trusted link in your dependencies.link file, since dependencies.json could contain malicious commands that get executed as you.

If you are managing multiple Jupyter environment deployments, you can have different dependencies.link files pointing at different dependencies.json files for each environment.
For example, Fedora deployments can have a dependencies.link that points to https://trusted.host/dependencies-fedora.json, while FreeBSD deployments can have a dependencies.link that points to https://trusted.host/dependencies-freebsd.json.
This allows multiple environment deployments to be centrally managed by changing their corresponding dependencies.json files.

### dependencies.json

dependencies.link contains a URL pointing to a dependencies.json file which maps the original package names to their overrides.
The dependencies.json file should look something like this contrived example:

```json
{
  "python-3": {
    "numpy": [
      [ "yum", "install", "python3-numpy" ]
    ],
    "labsetup": [
      [ "yum", "install", "python3-numpy" ],
      [ "yum", "install", "python3-scikitlearn" ],
      [ "yum", "install", "python3-pandas" ],
      [ "yum", "install", "python3-pymc3" ]
    ]
  },
  "python-3.5": {
    "numpy": [
      [ "yum", "install", "special-prerequisite-for-python-3.5" ],
      [ "yum", "install", "python3-numpy" ]
    ]
  },
  "python-2.7": {
    "foo": [
      [ "echo", "Why", "are", "you", "still", "using", "python", "2.7?" ]
    ]
  }
}
```

Note that ipydeps will use the most specific override it can find.
In the example above, a Python 3.5 environment will use the python-3.5 override for numpy.  The python-3 override for numpy will be ignored.

Also note that all package names are handled in a case-insensitive manner (just like pip), so ipydeps will output a warning if it finds duplicate packages listed in your dependencies.json file.

### Windows support

ipydeps now supports Windows as well as Linux.  It will look for your home directory using `os.path.expanduser('~')`.  In most cases, this just points to C:\Users\yourname.  You should put your .config/ipydeps/ipydeps.conf file in that directory.

### pypki2 support

In some environments, having a PKI-enabled pip server is advantageous.  To that end, pypki2 integration is supported.  Simply add the following to ipydeps.conf:

```text
--use-pypki2
```
