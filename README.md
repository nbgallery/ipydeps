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
