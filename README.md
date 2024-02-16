# ipydeps

A friendly way to specify your Jupyter notebook's dependencies right at the top of the notebook.
This helps ensure that other users have the Python packages they need to successfully run your notebook.

It includes features for installation accelerators via centrally-managed overrides, and PKI integration.  It also ensures that packages get installed into the same Python environment that's executing your notebook's code cells, like `%pip install`.

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

If you want more verbose output from pip, just set the `verbose` parameter to `True`.

```python
import ipydeps
ipydeps.pip('scikit-learn', verbose=True)
from sklearn.cluster import KMeans
```

There are also `use_pki`, `use_overrides`, and `config` options that can be passed to `ipydeps.pip()`.  More on that below.

## Configuration Files

The latest version of ipydeps supports multiple configuration files, which can be selected using `ipydeps.pip(['bar', 'baz'], config='repo1.conf')`, which will read the configuration in `~/.config/ipydeps/repo1.conf`.

The configuration files follow the normal ConfigParser format, for example:

```ini
[ipydeps]
dependencies_link="https://some.trusted/overrides/location.json"
dependencies_link_requires_pki=true
```

Note that `dependencies_link_requires_pki` defaults to false.  If set to true, it will get PKI information from pypki3 before reaching out to the `dependencies_link`.

The `dependencies_link` can also point to somewhere local:

```ini
[ipydeps]
dependencies_link="file:///some/local/path.json"
```

### dependencies_link

Sometimes there's a better way to install certain Python packages, such as a pre-built rpm or apk.  For example, maybe you want to install numpy, so you call ipydeps.pip('numpy').  However, numpy can take a while to install from scratch.  If there's a pre-built version of numpy available, it can install in seconds instead of minutes.  

`dependencies_link` contains a URL pointing to a JSON file which maps the original package names to their overrides.

Only use a trusted location in your dependencies_link, since the overrides could contain malicious commands that get executed as you.

If you are managing multiple Jupyter environment deployments, you can have different dependencies_link location pointing at different JSON files for each environment.
For example, Fedora deployments can have a dependencies_link that points to https://trusted.host/dependencies-fedora.json, while FreeBSD deployments can have a dependencies_link that points to https://trusted.host/dependencies-freebsd.json.
This allows multiple environment deployments to be centrally managed by changing their corresponding JSON files.

### Overrides

dependencies_link contains a URL pointing to a JSON file which maps the original package names to their overrides.
The JSON file should look something like this contrived example:

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

Also note that all package names are handled in a case-insensitive manner (just like pip), so ipydeps will output a warning if it finds duplicate packages listed in your JSON file.

If you explicitly *do not* want to use any overrides, simply use `ipydeps.pip(['bar', 'baz'], use_overrides=False)`.

### Windows support

ipydeps now supports Windows as well as Linux.  It will look for your home directory using `pathlib.Path.home()`.  In most cases, this just points to C:\Users\yourname.  You should put your config files in `.config/ipydeps/` within that home directory.

### PKI Support
PKI support is supplied by the pypki3 package.  PKI configuration information will be passed from pypki3 to pip.  This is particularly helpful with encrypted PKI certificates; pip normally prompts for your PKI password multiple times, but with pypki3 you only have to enter the password once.

To enable PKI support, simply use `ipydeps.pip(['bar', 'baz'], use_pki=True)`.
