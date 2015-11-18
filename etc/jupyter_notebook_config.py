# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import os
c = get_config()
c.NotebookApp.tornado_settings = {
    'autoreload': os.getenv('AUTORELOAD', 'no').lower() in ['yes', 'true']
}
c.NotebookApp.server_extensions = [
    'urth.cms'
]
