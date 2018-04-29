# vim: expandtab tabstop=4 shiftwidth=4

from .utils import _html_escape

try:
    from IPython.display import display, HTML
except ImportError:
    pass

def _ipython_html(msg, bgcolor, fgcolor='black'):
    msg = _html_escape(msg)
    style = 'font-family:monospace;background:{bgcolor};color:{fgcolor}'.format(bgcolor=bgcolor, fgcolor=fgcolor)
    htm = '<div style="{style}"><pre>{msg}</pre></div>'.format(style=style, msg=msg)
    display(HTML(htm))

class _IPythonLogger(object):
    def error(self, msg):
        _ipython_html(msg, 'lightpink')

    def warning(self, msg):
        _ipython_html(msg, 'lightyellow')

    def info(self, msg):
        _ipython_html(msg, '#e6fee6')

    def debug(self, msg):
        _ipython_html(msg, '#eee')
