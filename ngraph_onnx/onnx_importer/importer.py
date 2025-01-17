# ******************************************************************************
# Copyright 2018-2019 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ******************************************************************************
import onnx
from typing import List

from google.protobuf.message import DecodeError

from ngraph.impl import Function
from ngraph.impl import onnx_import
from ngraph.exceptions import UserInputError


def import_onnx_model(onnx_protobuf):  # type: (onnx.ModelProto) -> List[Function]
    """
    Import an ONNX Protocol Buffers model and convert it into a list of ngraph Functions.

    :param onnx_protobuf: ONNX Protocol Buffers model (onnx_pb2.ModelProto object)
    :return: list of ngraph Functions representing computations for each output.
    """
    if not isinstance(onnx_protobuf, onnx.ModelProto):
        raise UserInputError('Input does not seem to be a properly formatted ONNX model.')

    return onnx_import.import_onnx_model(onnx_protobuf.SerializeToString())


def import_onnx_file(filename):  # type: (str) -> List[Function]
    """
    Import ONNX model from a Protocol Buffers file and convert to ngraph functions.

    :param filename: path to an ONNX file
    :return: List of imported ngraph Functions (see docs for import_onnx_model).
    """
    try:
        onnx_protobuf = onnx.load(filename)
    except DecodeError:
        raise UserInputError("The provided file doesn't contain a properly formatted ONNX model.")

    return onnx_import.import_onnx_model(onnx_protobuf.SerializeToString())
