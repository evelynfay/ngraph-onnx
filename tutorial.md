# How to use nGraph Compiler with ONNX\* 

Use nGraph to accelerate... run ONNX files (to run/execute models or run
inference on models). Each ONNX file contains a NN model.

This tutorial...

* [Requirements](#requirements)
* [Install nGraph using pre-built packages](#install-pre-built-packages)
* [Build nGraph from source](#build-from-source)
* [Use nGraph with ONNX](#use-ngraph-with-onnx)
    * [Run inference on a model](#run-inference-on-a-model)
    * [Add a GPU backend](#add-a-gpu-backend)
* [Debugging](#debugging)
* [Support](#support)
* [How to contribute](#how-to-contribute)

## Requirements

* Python 3.4 or higher
* Protocol Buffers (protobuf) `v.2.6.1` or higher 

Install protobuf for Ubuntu:

    # apt update
    # apt install protobuf-compiler libprotobuf-dev

## Install pre-built packages

The easiest way to install `ngraph` and `ngraph-onnx` is to use our pre-built
packages from PyPI.

**Note**: Currently, we do not have pre-built packages (binaries) for macOS.

Install `ngraph-core`:

    pip install ngraph-core 

Install `ngraph-onnx`:

    pip install ngraph-onnx 
 

## Build from source

Complete the following steps to build nGraph with Python bindings from source.

These steps have been tested on Ubuntu 18.04.

1. Prepare your system:

 ```
# apt update
# apt install python3 python3-pip python3-dev python-virtualenv
# apt install build-essential cmake curl clang-3.9 git zlib1g zlib1g-dev libtinfo-dev unzip autoconf automake libtool
 ```

2. Clone nGraph's `master` branch. Build and install it into `$HOME/ngraph_dist`:
 
 ```
$ cd # Change directory to where you would like to clone nGraph sources
$ git clone -b master --single-branch --depth 1 https://github.com/NervanaSystems/ngraph.git
$ mkdir ngraph/build && cd ngraph/build
$ cmake ../ -DCMAKE_INSTALL_PREFIX=$HOME/ngraph_dist -DNGRAPH_ONNX_IMPORT_ENABLE=TRUE -DNGRAPH_USE_PREBUILT_LLVM=TRUE 
$ make
$ make install
 ```

3. Prepare a Python virtual environment for nGraph (recommended):
 
 ```
$ mkdir -p ~/.virtualenvs && cd ~/.virtualenvs
$ virtualenv -p $(which python3) nGraph
$ source nGraph/bin/activate
(nGraph) $ 
 ```

 `(nGraph)` indicates that you have created and activated a Python virtual 
 environment called `nGraph`.

4. Build a Python package (Binary wheel) for nGraph:
 
 ```
(nGraph) $ cd # Change directory to where you have cloned nGraph sources
(nGraph) $ cd ngraph/python
(nGraph) $ git clone --recursive https://github.com/jagerman/pybind11.git
(nGraph) $ export PYBIND_HEADERS_PATH=$PWD/pybind11
(nGraph) $ export NGRAPH_CPP_BUILD_PATH=$HOME/ngraph_dist
(nGraph) $ export NGRAPH_ONNX_IMPORT_ENABLE=TRUE
(nGraph) $ pip install numpy
(nGraph) $ python setup.py bdist_wheel
 ```
For additional information how to build nGraph Python bindings see:

https://github.com/NervanaSystems/ngraph/blob/master/python/README.md

4. Once the Python binary wheel file `ngraph-*.whl` is prepared, install it
using pip. For example:

 ```
(nGraph) $ pip install -U dist/ngraph_core-0.0.0.dev0-cp36-cp36m-linux_x86_64.whl
 ```
5. Check that nGraph is properly installed in your Python shell:

```python
>>> import ngraph as ng
>>> ng.abs([[1, 2, 3], [4, 5, 6]])
<Abs: 'Abs_1' ([2, 3])>
```

6. Additionally, check that nGraph and nGraph's Python wheel were both built
with  the `NGRAPH_ONNX_IMPORT_ENABLE` option:

```python
from ngraph.impl import onnx_import
```

If you don't see any errors, nGraph should be installed correctly.

### Install ngraph-onnx

`ngraph-onnx` is an additional Python library that provides a Python API for
running ONNX models using nGraph.  You can install `ngraph-onnx` using the
following commands.

Clone `ngraph-onnx` sources to the same directory where you cloned `ngraph` 
sources.

    (nGraph) $ cd # Change directory to where you have cloned nGraph sources
    (nGraph) $ git clone -b master --single-branch --depth 1 https://github.com/NervanaSystems/ngraph-onnx.git
    (nGraph) $ cd ngraph-onnx

In your Python virtual environment, install the required packages and 
`ngraph-onnx`:

    (nGraph) $ pip install -r requirements.txt
    (nGraph) $ pip install -r requirements_test.txt
    (nGraph) $ pip install -e .

To verify that `ngraph-onnx` installed correctly, you can run our test suite using:

    (nGraph) $ pytest tests/ --backend=CPU -v
    (nGraph) $ NGRAPH_BACKEND=CPU TOX_INSTALL_NGRAPH_FROM=../ngraph/python tox

## Use nGraph with ONNX

After installing `ngraph-onnx` from source, you can run inference on an ONNX
model. The model is a file which contains a graph representing a mathematical
formula (e.g., a function such as y = f(x)). Run a computation contained within
the model.

### Run inference on a model 

Lorem ipsum. Accelerate inference using nGraph. Describe how nGraph is speeding
up inference.

#### Import an ONNX model

Download models from the [ONNX model zoo][onnx_model_zoo]. For example
ResNet-50:

    $ wget https://s3.amazonaws.com/download.onnx/models/opset_8/resnet50.tar.gz
    $ tar -xzvf resnet50.tar.gz

Use the following Python commands to convert the downloaded model to an nGraph
model:

```python
# Import ONNX and load an ONNX file from disk
>>> import onnx
>>> onnx_protobuf = onnx.load('resnet50/model.onnx')

# Convert ONNX model to an ngraph model
>>> from ngraph_onnx.onnx_importer.importer import import_onnx_model
>>> ng_function = import_onnx_model(onnx_protobuf)

# The importer returns a list of ngraph models for every ONNX graph output:
>>> print(ng_function)
<Function: 'resnet50' ([1, 1000])>
```

This creates an nGraph `Function` object, which can be used to execute a
computation on a chosen backend.

#### Run a computation

An ONNX model usually contains a trained neural network. To run inference on
this model, you execute the computation contained in the model.

After importing an ONNX model, you will have an nGraph `Function` object.  Now
you can create an nGraph `Runtime` backend and use it to compile your `Function`
to a backend-specific `Computation` object.

Execute your model by calling the created `Computation` object with input data.

```python
# Using an ngraph runtime (CPU backend) create a callable computation object
>>> import ngraph as ng
>>> runtime = ng.runtime(backend_name='CPU')
>>> resnet_on_cpu = runtime.computation(ng_function)

# Load an image (or create a mock as in this example)
>>> import numpy as np
>>> picture = np.ones([1, 3, 224, 224], dtype=np.float32)

# Run computation on the picture:
>>> resnet_on_cpu(picture)
[array([[2.16105007e-04, 5.58412226e-04, 9.70510227e-05, 5.76671446e-05,
         7.45318757e-05, 4.80892748e-04, 5.67404088e-04, 9.48728994e-05,
         ...
```
### Add a GPU backend
Lorem ipsum
## Debugging
Lorem ipsum

## Support
Lorem ipsum

## How to contribute

[onnx]: http://onnx.ai/
[onnx_model_zoo]: https://github.com/onnx/models
[ngraph_github]: https://github.com/NervanaSystems/ngraph
[building]: https://github.com/NervanaSystems/ngraph-onnx/blob/master/BUILDING.md
