# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Converters for ONNX operators.
"""

import numpy as np
import torch

from onnxconverter_common.registration import register_converter

from . import constants
from ._base_operator import BaseOperator


class Cast(BaseOperator, torch.nn.Module):
    def __init__(self, to_type):
        super(Cast, self).__init__()

        assert to_type is not None

        self.to_type = to_type

    def forward(self, x):
        if self.to_type == 7:  # Cast to long
            return x.long()


class Concat(BaseOperator, torch.nn.Module):
    def __init__(self):
        super(Concat, self).__init__()

    def forward(self, *x):
        return torch.cat(x, dim=1)


class Reshape(BaseOperator, torch.nn.Module):
    def __init__(self, shape):
        super(Reshape, self).__init__()

        self.shape = shape

    def forward(self, x):
        return torch.reshape(x, self.shape)


def convert_onnx_cast(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Cast`.

    Args:
        operator: An operator wrapping a `ai.onnx.Cast` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    to_type = None

    for attr in operator.raw_operator.origin.attribute:
        if attr.name == "to":
            to_type = attr.i

    # Generate the model.
    return Cast(to_type)


def convert_onnx_concat(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Concat`.

    Args:
        operator: An operator wrapping a `ai.onnx.Concat` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    # Generate the model.
    return Concat()


def convert_onnx_reshape(operator, device=None, extra_config={}):
    """
    Converter for `ai.onnx.Reshape`.

    Args:
        operator: An operator wrapping a `ai.onnx.Reshape` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    assert operator is not None

    shape = []
    initializers = extra_config[constants.ONNX_INITIALIZERS]
    shape = list(initializers[operator.raw_operator.origin.input[1]].int64_data)

    # Generate the model.
    return Reshape(shape)


register_converter("ONNXMLCast", convert_onnx_cast)
register_converter("ONNXMLConcat", convert_onnx_concat)
register_converter("ONNXMLReshape", convert_onnx_reshape)
