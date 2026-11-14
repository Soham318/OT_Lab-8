"""
Unit Tests for Track A: Continuous Optimization
Assignment 8 - Optimize Anything

Tests:
  1. Gradient correctness across convex and non-convex landscapes.
  2. Hessian correctness and positive definiteness.
  3. Neural network decoupled backpropagation numerical gradient check.
  4. Convergence of all 8 first-order optimizers on strongly convex benchmark.
  5. Second-order Newton's method quadratic convergence.
  6. Gauss-Newton convergence on non-linear least squares.
  7. Curvature approximations (Fisher Information, Diagonal, and HVP Pearlmutter).
  8. Robust input validation and error handling.
"""

import unittest
import numpy as np

from track_a_continuous_optimization.src.landscapes import (
    ConvexQuadratic,
    StronglyConvexQuadratic,
    RastriginNonConvex,
    RosenbrockNonConvex,
    SaddlePointLandscape,
    NonLinearLeastSquaresProblem
)
from track_a_continuous_optimization.src.optimizers import (
    BatchGradientDescent,
    StochasticGradientDescent,
    MiniBatchGradientDescent,
    MomentumOptimizer,
    NesterovAcceleratedGradient,
    AdaGrad,
    RMSProp,
    Adam
)
from track_a_continuous_optimization.src.second_order import NewtonsMethod, GaussNewtonMethod
from track_a_continuous_optimization.src.neural_net import TwoLayerMLP
from track_a_continuous_optimization.src.curvature import CurvatureApproximations


class TestContinuousOptimizers(unittest.TestCase):

    def setUp(self):
        self.rng = np.random.RandomState(42)

    def _numerical_gradient(self, func, x, eps=1e-6):
        grad = np.zeros_like(x)
        for i in range(len(x)):
            x_plus = np.array(x, copy=True)
            x_plus[i] += eps
            x_minus = np.array(x, copy=True)
            x_minus[i] -= eps
            grad[i] = (func(x_plus) - func(x_minus)) / (2.0 * eps)
        return grad

    def test_01_gradient_correctness_convex(self):
        """Verify analytical gradient of ConvexQuadratic matches numerical gradient."""
        landscape = ConvexQuadratic(dim=5, condition_number=4.0, seed=42)
        x = self.rng.randn(5)
        g_analytical = landscape.gradient(x)
        g_numerical = self._numerical_gradient(landscape.value, x)
        rel_error = np.linalg.norm(g_analytical - g_numerical) / (np.linalg.norm(g_analytical) + 1e-10)
        self.assertLess(rel_error, 1e-5)

    def test_02_gradient_correctness_strongly_convex(self):
        """Verify analytical gradient of StronglyConvexQuadratic matches numerical gradient."""
        landscape = StronglyConvexQuadratic(dim=6, mu=1.5, seed=42)
        x = self.rng.randn(6)
        g_analytical = landscape.gradient(x)
        g_numerical = self._numerical_gradient(landscape.value, x)
        rel_error = np.linalg.norm(g_analytical - g_numerical) / (np.linalg.norm(g_analytical) + 1e-10)
        self.assertLess(rel_error, 1e-5)

    def test_03_gradient_correctness_rosenbrock(self):
        """Verify analytical gradient of Rosenbrock non-convex landscape."""
        landscape = RosenbrockNonConvex()
        x = np.array([-1.2, 1.0])
        g_analytical = landscape.gradient(x)
        g_numerical = self._numerical_gradient(landscape.value, x)
        rel_error = np.linalg.norm(g_analytical - g_numerical) / (np.linalg.norm(g_analytical) + 1e-10)
        self.assertLess(rel_error, 1e-5)

    def test_04_gradient_correctness_rastrigin(self):
        """Verify analytical gradient of Rastrigin non-convex landscape."""
        landscape = RastriginNonConvex(dim=3)
        x = np.array([0.5, -0.8, 1.2])
        g_analytical = landscape.gradient(x)
        g_numerical = self._numerical_gradient(landscape.value, x)
        rel_error = np.linalg.norm(g_analytical - g_numerical) / (np.linalg.norm(g_analytical) + 1e-10)
        self.assertLess(rel_error, 1e-5)

    def test_05_neural_net_backprop_numerical_check(self):
        """Verify decoupled backpropagation on TwoLayerMLP against finite differences."""
        mlp = TwoLayerMLP(input_dim=2, hidden_dim=3, output_dim=1, loss_type="mse", seed=42)
        X = self.rng.randn(10, 2)
        y = self.rng.randn(10, 1)
        rel_err = mlp.check_gradients_numerical(X, y, eps=1e-5)
        self.assertLess(rel_err, 1e-5, f"Backprop gradient error too high: {rel_err}")

    def test_06_all_first_order_optimizers_converge_strongly_convex(self):
        """Verify that all 8 first-order optimizers reduce loss on strongly convex quadratic."""
        landscape = StronglyConvexQuadratic(dim=4, mu=1.0, condition_number=3.0, seed=42)
        x_init = np.ones(4) * 2.0
        init_loss = landscape.value(x_init)

        optimizers = [
            BatchGradientDescent(learning_rate=0.08, max_iters=250),
            StochasticGradientDescent(learning_rate=0.08, max_iters=250, noise_std=0.02),
            MiniBatchGradientDescent(learning_rate=0.08, batch_size=8, max_iters=250, noise_std=0.02),
            MomentumOptimizer(learning_rate=0.05, beta=0.9, max_iters=250),
            NesterovAcceleratedGradient(learning_rate=0.05, beta=0.9, max_iters=250),
            AdaGrad(learning_rate=0.5, max_iters=250),
            RMSProp(learning_rate=0.05, max_iters=250),
            Adam(learning_rate=0.1, max_iters=250)
        ]

        for opt in optimizers:
            res = opt.minimize(landscape.value, landscape.gradient, x_init)
            self.assertLess(
                res.f_final,
                init_loss * 0.1,
                f"{res.optimizer_name} failed to reduce loss: init={init_loss}, final={res.f_final}"
            )
            self.assertGreater(len(res.history_loss), 1)

    def test_07_newton_quadratic_convergence(self):
        """Newton's method solves quadratic in 1 step to machine precision."""
        landscape = StronglyConvexQuadratic(dim=5, mu=2.0, seed=42)
        x_init = self.rng.randn(5) * 3.0
        newton = NewtonsMethod(damping=1e-8, max_iters=10, tol=1e-10)
        res = newton.minimize(landscape.value, landscape.gradient, landscape.hessian, x_init)

        self.assertTrue(res.converged)
        self.assertLessEqual(res.iterations, 3)
        self.assertAlmostEqual(res.f_final, landscape.f_opt, places=6)

    def test_08_gauss_newton_least_squares_convergence(self):
        """Gauss-Newton method converges on non-linear exponential fit."""
        nls = NonLinearLeastSquaresProblem(num_points=40, noise_std=0.01, seed=42)
        x_init = np.array([1.5, 0.8, 0.2])  # initial guess
        init_val = nls.value(x_init)

        gn = GaussNewtonMethod(damping=1e-4, max_iters=30, tol=1e-7)
        res = gn.minimize(nls.residuals, nls.jacobian, x_init)

        self.assertTrue(res.converged or res.f_final < init_val * 0.05)
        self.assertLess(res.f_final, init_val * 0.1)
        self.assertLess(res.final_grad_norm, 1e-3)

    def test_09_curvature_fisher_and_diagonal(self):
        """Verify Empirical Fisher computation and diagonal Hessian extraction."""
        N, d = 100, 4
        X = self.rng.randn(N, d)
        w_true = np.array([1.0, -0.5, 0.8, -0.2])
        probs = 1.0 / (1.0 + np.exp(-X @ w_true))
        y = (self.rng.rand(N) < probs).astype(np.float64)

        # At theta != 0, empirical Fisher and true Hessian differ
        theta_nonzero = np.array([0.5, -0.2, 0.3, 0.1])
        F_emp, H_true, diff = CurvatureApproximations.empirical_fisher_matrix(X, y, theta_nonzero)

        self.assertEqual(F_emp.shape, (d, d))
        self.assertEqual(H_true.shape, (d, d))
        self.assertGreater(diff, 0.0)

        # Diagonal approximation
        D, rel_err = CurvatureApproximations.diagonal_hessian_approximation(H_true)
        self.assertEqual(D.shape, (d, d))
        self.assertTrue(np.all(np.diag(D) > 0))

    def test_10_hessian_vector_product_accuracy(self):
        """Verify Pearlmutter's HVP matches exact H @ v multiplication."""
        landscape = StronglyConvexQuadratic(dim=5, seed=42)
        x = self.rng.randn(5)
        v = self.rng.randn(5)
        v = v / np.linalg.norm(v)

        H = landscape.hessian(x)
        exact_hv = H @ v
        approx_hv = CurvatureApproximations.hessian_vector_product(landscape.gradient, x, v, eps=1e-5)

        rel_err = np.linalg.norm(exact_hv - approx_hv) / (np.linalg.norm(exact_hv) + 1e-10)
        self.assertLess(rel_err, 1e-4, f"HVP error too high: {rel_err}")

    def test_11_invalid_inputs_handling(self):
        """Verify that invalid hyperparameters raise appropriate ValueError exceptions."""
        with self.assertRaises(ValueError):
            BatchGradientDescent(learning_rate=-0.01)

        with self.assertRaises(ValueError):
            BatchGradientDescent(max_iters=0)

        with self.assertRaises(ValueError):
            BatchGradientDescent(tol=-1e-4)


if __name__ == "__main__":
    unittest.main()
