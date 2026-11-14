"""
Track A: Continuous Optimization
Package Exports
"""

from .landscapes import (
    ConvexQuadratic,
    StronglyConvexQuadratic,
    RastriginNonConvex,
    RosenbrockNonConvex,
    SaddlePointLandscape,
    NonLinearLeastSquaresProblem
)
from .optimizers import (
    OptimizerResult,
    BaseOptimizer,
    BatchGradientDescent,
    StochasticGradientDescent,
    MiniBatchGradientDescent,
    MomentumOptimizer,
    NesterovAcceleratedGradient,
    AdaGrad,
    RMSProp,
    Adam
)
from .second_order import NewtonsMethod, GaussNewtonMethod
from .neural_net import TwoLayerMLP, sigmoid, sigmoid_derivative
from .curvature import CurvatureApproximations

__all__ = [
    "ConvexQuadratic",
    "StronglyConvexQuadratic",
    "RastriginNonConvex",
    "RosenbrockNonConvex",
    "SaddlePointLandscape",
    "NonLinearLeastSquaresProblem",
    "OptimizerResult",
    "BaseOptimizer",
    "BatchGradientDescent",
    "StochasticGradientDescent",
    "MiniBatchGradientDescent",
    "MomentumOptimizer",
    "NesterovAcceleratedGradient",
    "AdaGrad",
    "RMSProp",
    "Adam",
    "NewtonsMethod",
    "GaussNewtonMethod",
    "TwoLayerMLP",
    "sigmoid",
    "sigmoid_derivative",
    "CurvatureApproximations"
]

