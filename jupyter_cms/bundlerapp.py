# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import sys
import os

try:
    from notebook.nbextensions import (BaseNBExtensionApp, _get_config_dir)
except ImportError:
    sys.exit("Aborted: {} requires notebook>=4.2,<5.0".format(
        os.path.basename(sys.argv[0])))

from ._version import __version__

from traitlets.config.manager import BaseJSONConfigManager
from traitlets.utils.importstring import import_item
from traitlets import Bool

BUNDLER_SECTION = "notebook"
BUNDLER_SUBSECTION = "jupyter_cms_bundlers"

def _get_bundler_metadata(module):
    """Gets the list of bundlers associated with a Python package.

    Returns a tuple of (the module, [{
        'name': 'unique name of the bundler',
        'label': 'file menu item label for the bundler',
        'module_name': 'dotted package/module name containing the bundler',
        'group': 'download or deploy parent menu item'
    }])

    Parameters
    ----------

    module : str
        Importable Python module exposing the
        magic-named `_jupyter_bundler_paths` function
    """
    m = import_item(module)
    if not hasattr(m, '_jupyter_bundler_paths'):
        raise KeyError('The Python module {} does not contain a valid bundler'.format(module))
    bundlers = m._jupyter_bundler_paths()
    return m, bundlers

def _set_bundler_state(name, label, module_name, group, state,
                       user=True, sys_prefix=False, logger=None):
    """Set whether a bundler is enabled or disabled.
    
    Returns True if the final state is the one requested.
    
    Parameters
    ----------
    name : string
        Unique name of the bundler
    label : string
        Human-readable label for the bundler menu item in the notebook UI
    module_name : string
        Dotted module/package name containing the bundler
    group : string
        'download' or 'deploy' indicating the parent menu containing the label
    state : bool
        The state in which to leave the extension
    user : bool [default: True]
        Whether to update the user's .jupyter/nbconfig directory
    sys_prefix : bool [default: False]
        Whether to update the sys.prefix, i.e. environment. Will override
        `user`.
    logger : Jupyter logger [optional]
        Logger instance to use
    """
    user = False if sys_prefix else user
    config_dir = os.path.join(
        _get_config_dir(user=user, sys_prefix=sys_prefix), 'nbconfig')
    cm = BaseJSONConfigManager(config_dir=config_dir)
    
    if logger:
        logger.info("{} {} bundler {}...".format(
            "Enabling" if state else "Disabling",
            name,
            module_name
        ))
    
    if state:
        cm.update(BUNDLER_SECTION, {
            BUNDLER_SUBSECTION: {
                name: {
                    "label": label,
                    "module_name": module_name,
                    "group" : group
                }
            }
        })
    else:
        cm.update(BUNDLER_SECTION, {
            BUNDLER_SUBSECTION: {
                name: None
            }
        })

    return (cm.get(BUNDLER_SECTION)
              .get(BUNDLER_SUBSECTION, {})
              .get(name) is not None) == state
    

def _set_bundler_state_python(state, module, user, sys_prefix, logger=None):
    """Enables or disables bundlers defined in a Python package.
    
    Returns a list of whether the state was achieved for each bundler.
    
    Parameters
    ----------
    state : Bool
        Whether the extensions should be enabled
    module : str
        Importable Python module exposing the
        magic-named `_jupyter_bundler_paths` function
    user : bool
        Whether to enable in the user's nbconfig directory.
    sys_prefix : bool
        Enable/disable in the sys.prefix, i.e. environment
    logger : Jupyter logger [optional]
        Logger instance to use
    """
    m, bundlers = _get_bundler_metadata(module)
    return [_set_bundler_state(name=bundler["name"],
                               label=bundler["label"],
                               module_name=bundler["module_name"],
                               group=bundler["group"],
                               state=state,
                               user=user, sys_prefix=sys_prefix,
                               logger=logger)
            for bundler in bundlers]

def enable_bundler_python(module, user=True, sys_prefix=False, logger=None):
    """Enables bundlers defined in a Python package.
    
    Returns whether each bundle defined in the packaged was enabled or not.
    
    Parameters
    ----------
    module : str
        Importable Python module exposing the
        magic-named `_jupyter_bundler_paths` function
    user : bool [default: True]
        Whether to enable in the user's nbconfig directory.
    sys_prefix : bool [default: False]
        Whether to enable in the sys.prefix, i.e. environment. Will override
        `user`
    logger : Jupyter logger [optional]
        Logger instance to use
    """
    return _set_bundler_state_python(True, module, user, sys_prefix,
                                     logger=logger)
    
def disable_bundler_python(module, user=True, sys_prefix=False, logger=None):
    """Disables bundlers defined in a Python package.
    
    Returns whether each bundle defined in the packaged was enabled or not.
    
    Parameters
    ----------
    module : str
        Importable Python module exposing the
        magic-named `_jupyter_bundler_paths` function
    user : bool [default: True]
        Whether to enable in the user's nbconfig directory.
    sys_prefix : bool [default: False]
        Whether to enable in the sys.prefix, i.e. environment. Will override
        `user`
    logger : Jupyter logger [optional]
        Logger instance to use
    """
    return _set_bundler_state_python(False, module, user, sys_prefix,
                                     logger=logger)

class ToggleNBBundlerApp(BaseNBExtensionApp):
    """A base class for apps that enable/disable bundlers"""
    name = "jupyter bundler enable/disable"
    version = __version__
    description = "Enable/disable a bundler in configuration."

    user = Bool(True, config=True, help="Apply the configuration only for the current user (default)")
    
    _toggle_value = None
    
    def _config_file_name_default(self):
        """The default config file name."""
        return 'jupyter_notebook_config'
    
    def toggle_bundler_python(self, module):
        """Toggle some extensions in an importable Python module.

        Returns a list of booleans indicating whether the state was changed as
        requested.

        Parameters
        ----------
        module : str
            Importable Python module exposing the
            magic-named `_jupyter_bundler_paths` function
        """
        toggle = (enable_bundler_python if self._toggle_value
                  else disable_bundler_python)
        return toggle(module,
                      user=self.user,
                      sys_prefix=self.sys_prefix,
                      logger=self.log)

    def start(self):
        if not self.extra_args:
            sys.exit('Please specify an nbextension/package to enable or disable')
        elif len(self.extra_args) > 1:
            sys.exit('Please specify one nbextension/package at a time')
        if self.python:
            self.toggle_bundler_python(self.extra_args[0])
        else:
            raise NotImplementedError('Cannot install bundlers from non-Python packages')            

class EnableNBBundlerApp(ToggleNBBundlerApp):
    """An App that enables bundlers"""
    name = "jupyter bundler enable"
    description = """
    Enable a bundler in frontend configuration.
    
    Usage
        jupyter bundler enable [--system|--sys-prefix]
    """
    _toggle_value = True
    
class DisableNBBundlerApp(ToggleNBBundlerApp):
    """An App that disables bundlers"""
    name = "jupyter bundler disable"
    description = """
    Disable a bundler in frontend configuration.
    
    Usage
        jupyter bundler disable [--system|--sys-prefix]
    """
    _toggle_value = None

class NBBundlerApp(BaseNBExtensionApp):
    """Base jupyter bundler command entry point"""
    name = "jupyter bundler"
    version = __version__
    description = "Work with Jupyter notebook bundlers"
    examples = """
jupyter bundler enable --py <packagename>     # enable all bundlers in a Python package
jupyter bundler disable --py <packagename>    # disable all bundlers in a Python package
"""

    subcommands = dict(
        enable=(EnableNBBundlerApp, "Enable a bundler"),
        disable=(DisableNBBundlerApp, "Disable a bundler")
    )

    def start(self):
        """Perform the App's functions as configured"""
        super(NBBundlerApp, self).start()

        # The above should have called a subcommand and raised NoStart; if we
        # get here, it didn't, so we should self.log.info a message.
        subcmds = ", ".join(sorted(self.subcommands))
        sys.exit("Please supply at least one subcommand: %s" % subcmds)

main = NBBundlerApp.launch_instance
