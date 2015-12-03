[![PyPI version](https://badge.fury.io/py/jupyter_cms.svg)](https://badge.fury.io/py/jupyter_cms) [![Google Group](https://img.shields.io/badge/-Google%20Group-lightgrey.svg)](https://groups.google.com/forum/#!forum/jupyter)

# Jupyter Content Management Extensions

Content management extensions for Jupyter / IPython Notebook.

## What It Gives You

The content management extensions provide the following:

* Search dialog on dashboard, editor, and notebook screens to search over filenames and `.ipynb` content in the notebook directory
* IPython kernel extension to make notebooks importable, and notebook cells injectable via `# <api>` and `# <help>` annotations (see included example notebooks)
* Full-page drag-and-drop upload target
* Pop-over table of contents navigation for notebooks

Watch the first 15-20 minutes of the [September 1st Jupyter meeting video recording](https://www.youtube.com/watch?v=SJiezXPhVv8) for demonstrations of each content management feature.

## What it Lacks

* Tests (they exist, just not ported to the open source yet)
* User docs
* Snippets in search hits (requires Whoosh unicode fixes for Python3)

## Prerequisites

* Jupyter Notebook 4.0.x running on Python 3.x or Python 2.7.x
* Edge Chrome, Firefox, or Safari

Note: If you're running IPython Notebook 3.2.x, you can install the older 0.1.x version of the extension.

# Try It

If you want to try the extension and demos without installing it yourself, visit the [jupyter-incubator/showcase binder](http://mybinder.org/repo/jupyter-incubator/showcase). If the binder site is full, try the tmpnb instance at [http://jupyter.cloudet.xyz](http://jupyter.cloudet.xyz).

# Install It

`pip install jupyter_cms` and then restart your Notebook server if it was running during the install.

# Develop

This repository is setup for a Dockerized development environment.  These instructions assume the Docker client is running natively on the local host, and that it is configured to point to a Docker daemon running on a Linux virtual machine.

## Mac OS X

Do this one-time setup if you do not have a local Docker environment yet.

Download and install [VirtualBox](https://www.virtualbox.org/wiki/Downloads).

Download and install Docker.

```
brew update

# make sure you're on Docker >= 1.7
brew install docker-machine docker

# create a VirtualBox virtual machine called 'dev' on local host, with Docker daemon installed
docker-machine create -d virtualbox dev

# point Docker client to virtual machine
eval "$(docker-machine env dev)"
```

Clone this repository into a local directory that Docker can volume mount.

```
mkdir -p ~/projects/contentmanagement
cd !$
git clone https://github.com/jupyter-incubator/contentmanagement.git
```

Pull a base Docker image and build a subimage from it that includes [scandir](https://github.com/benhoyt/scandir) and [whoosh](http://whoosh.readthedocs.org/en/latest/) (runtime requirements usually installed by setuptools).

```
make build
```

Run the notebook server in a Docker container.

```
make dev
```

The final `make` command starts a Docker container on your VM with the critical pieces of the source tree mounted where they need to be to get picked up by the notebook server within the container.  Most code changes on your Mac host will have immediate effect within the container.

To see the Jupyter instance with extensions working:

1. Run `docker-machine ip dev` and note the IP of the dev machine.
2. Visit http://THAT_IP:9500 in your browser

See the Makefile for other dev, test, build commands as well as options for each command.
