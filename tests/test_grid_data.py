#!/usr/bin/env python3

# Copyright (C) 2020 Gabriele Bozzola
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, see <https://www.gnu.org/licenses/>.

"""Tests for postcactus.grid_data
"""

import unittest

import numpy as np

from postcactus import grid_data as gd


class TestUniformGrid(unittest.TestCase):
    def test__check_dims(self):

        # Test multidimensional shape
        with self.assertRaises(ValueError):
            gd.UniformGrid(np.array([[1, 2], [3, 4]]), np.array([1, 2]))

        # Test different len between shape and origin
        with self.assertRaises(ValueError):
            gd.UniformGrid(np.array([100, 200]), np.array([1, 2, 3]))

    def test_init_getters(self):

        # Test error neither of dx and x1 provided
        with self.assertRaises(ValueError):
            geom = gd.UniformGrid([101, 101], [1, 1])

        # Test dx
        geom = gd.UniformGrid([101, 101], [1, 1], x1=[101, 51])

        self.assertTrue(np.allclose(geom.dx, [1, 0.5]))
        self.assertIs(geom.delta, geom.dx)
        self.assertIs(geom.origin, geom.x0)

        # Test x1 and dx given, but incompatible
        with self.assertRaises(ValueError):
            geom = gd.UniformGrid([101, 51], [1, 1], x1=[4, 4], dx=[1, 1])

        # Test x1 not upper corner
        with self.assertRaises(ValueError):
            geom = gd.UniformGrid([101, 51], [1, 1], x1=[-1, -1])

        # Test x1
        geom2 = gd.UniformGrid([101, 101], [1, 1], dx=[1, 0.5])

        self.assertTrue(np.allclose(geom2.x1, [101, 51]))

        # Test num_ghost
        self.assertCountEqual(geom.num_ghost, np.zeros(2))

        geom3 = gd.UniformGrid(
            [101, 101], [1, 1], dx=[1, 0.5], num_ghost=[3, 3]
        )

        self.assertCountEqual(geom3.num_ghost, 3 * np.ones(2))

        # Test other attributes
        self.assertEqual(geom3.ref_level, -1)
        self.assertEqual(geom3.component, -1)

        geom4 = gd.UniformGrid(
            [101, 101],
            x0=[1, 1],
            dx=[1, 0.5],
            num_ghost=[3, 3],
            time=1,
            iteration=1,
        )

        self.assertEqual(geom4.time, 1)
        self.assertEqual(geom4.iteration, 1)

        # Test properties
        self.assertEqual(geom4.num_dimensions, 2)
        self.assertAlmostEqual(geom4.dv, 0.5)
        self.assertAlmostEqual(geom4.volume, 0.5 * 101 * 101)

        geom5 = gd.UniformGrid(
            [101, 101, 1],
            x0=[1, 1, 0],
            dx=[1, 0.5, 0],
            num_ghost=[3, 3, 3],
            time=1,
            iteration=1,
        )

        self.assertCountEqual(geom5.extended_dimensions, [True, True, False])
        self.assertEqual(geom5.num_extended_dimensions, 2)

        # Test case with shape with ones and given x1
        geom6 = gd.UniformGrid(
            [101, 101, 1],
            x0=[1, 1, 0],
            x1=[101, 51, 1],
            num_ghost=[3, 3, 3],
            time=1,
            iteration=1,
        )

        self.assertEqual(geom5, geom6)

    def test_coordinate_to_indices(self):
        geom = gd.UniformGrid([101, 51], x0=[1, 2], dx=[1, 0.5])
        # Scalar input
        self.assertCountEqual(geom.indices_to_coordinates([1, 3]), [2, 3.5])
        self.assertCountEqual(geom.coordinates_to_indices([2, 3.5]), [1, 3])
        # Vector input
        self.assertTrue(
            np.allclose(
                geom.indices_to_coordinates([[1, 3], [2, 4]]),
                [[2, 3.5], [3, 4]],
            )
        )
        self.assertTrue(
            np.allclose(
                geom.coordinates_to_indices([[2, 3.5], [3, 4]]),
                [[1, 3], [2, 4]],
            )
        )

    def test__in__(self):

        # We test __in__ testing contains, which calls in
        geom4 = gd.UniformGrid(
            [101, 101],
            x0=[1, 1],
            x1=[101, 51],
            num_ghost=[3, 3],
            time=1,
            iteration=1,
        )

        self.assertTrue(geom4.contains([50, 50]))
        self.assertTrue(geom4.contains([1, 1]))
        self.assertFalse(geom4.contains([1, 0]))
        self.assertFalse(geom4.contains([102, 102]))
        self.assertFalse(geom4.contains([102, 51]))

    def test__str(self):

        geom4 = gd.UniformGrid(
            [101, 101],
            x0=[1, 1],
            dx=[1, 0.5],
            num_ghost=[3, 3],
            time=1,
            iteration=1,
        )

        self.assertIn("Num ghost zones  = [3 3]", geom4.__str__())

    def test_coordinates(self):

        geom4 = gd.UniformGrid(
            [11, 15],
            x0=[1, 2],
            dx=[1, 0.5],
            num_ghost=[3, 3],
            time=1,
            iteration=1,
        )

        x = np.linspace(1, 11, 11)
        y = np.linspace(2, 9, 15)

        c0 = geom4.coordinates(as_meshgrid=True)

        X, Y = np.meshgrid(x, y)

        self.assertTrue(np.allclose(c0[0], X))
        self.assertTrue(np.allclose(c0[1], Y))

        c1 = geom4.coordinates()

        self.assertTrue(np.allclose(c1[0], x))
        self.assertTrue(np.allclose(c1[1], y))

        with self.assertRaises(ValueError):
            geom4.coordinates(as_meshgrid=True, as_same_shape=True)

        # Here the output is a list of coordinates shaped like the array itself
        shaped_array = geom4.coordinates(as_same_shape=True)
        self.assertCountEqual(shaped_array[0].shape, geom4.shape)
        # We check that the first column is the same as the coordinates
        self.assertTrue(
            np.allclose(shaped_array[0][:, 0], geom4.coordinates()[0])
        )

    def test__getitem__(self):

        geom4 = gd.UniformGrid(
            [11, 15],
            x0=[1, 1],
            dx=[1, 0.5],
            num_ghost=[3, 3],
            time=1,
            iteration=1,
        )

        with self.assertRaises(ValueError):
            geom4[1]

        self.assertCountEqual(geom4[1, 3], [2, 2.5])

    def test_flat_dimensions_removed(self):

        geom = gd.UniformGrid(
            [101, 101, 1],
            x0=[1, 1, 0],
            dx=[1, 0.5, 0],
            num_ghost=[3, 3, 3],
            time=1,
            iteration=1,
        )

        geom2 = gd.UniformGrid(
            [101, 101],
            x0=[1, 1],
            dx=[1, 0.5],
            num_ghost=[3, 3],
            time=1,
            iteration=1,
        )

        self.assertEqual(geom.flat_dimensions_removed(), geom2)

    def test_flat_ghost_zones_removed(self):

        geom = gd.UniformGrid(
            [101, 101], x0=[1, 1], dx=[1, 0.5], num_ghost=[3, 0]
        )

        geom2 = gd.UniformGrid(
            [95, 101], x0=[4, 1], dx=[1, 0.5], num_ghost=[0, 0]
        )

        self.assertEqual(geom.ghost_zones_removed(), geom2)

    def test_shifted(self):

        geom = gd.UniformGrid(
            [101, 101],
            x0=[1, 0],
            x1=[3, 10],
            num_ghost=[3, 3],
            time=1,
            iteration=1,
        )

        geom2 = gd.UniformGrid(
            [101, 101],
            x0=[3, -2],
            x1=[5, 8],
            num_ghost=[3, 3],
            time=1,
            iteration=1,
        )

        self.assertEqual(geom.shifted([2, -2]), geom2)

        # Error incompatible dimensions
        with self.assertRaises(ValueError):
            geom.shifted(2)

    def test_copy(self):

        geom = gd.UniformGrid(
            [101, 101, 1],
            x0=[1, 1, 0],
            dx=[1, 0.5, 0],
            num_ghost=[3, 3, 3],
            time=1,
            iteration=1,
        )

        geom2 = geom.copy()

        self.assertEqual(geom, geom2)
        self.assertIsNot(geom, geom2)

    def test_common_bounding_box(self):

        # Test error for not passing a list
        with self.assertRaises(TypeError):
            gd.common_bounding_box(1)

        # Test error for not passing a list of UniformGrid
        with self.assertRaises(TypeError):
            gd.common_bounding_box([1, 2])

        geom1 = gd.UniformGrid([101, 101], x0=[1, 1], x1=[3, 5])
        geom2 = gd.UniformGrid([101], x0=[1], x1=[3])

        # Different dimensions
        with self.assertRaises(ValueError):
            gd.common_bounding_box([geom1, geom2])

        geom3 = gd.UniformGrid([11, 11], x0=[0, 0], x1=[5, 5])
        geom4 = gd.UniformGrid([11, 11], x0=[0, -2], x1=[1, 5])

        self.assertCountEqual(
            gd.common_bounding_box([geom1, geom3, geom4])[0], [0, -2]
        )
        self.assertCountEqual(
            gd.common_bounding_box([geom1, geom3, geom4])[1], [5, 5]
        )

        # Test that the function returns the same element when called with one
        # element
        self.assertCountEqual(gd.common_bounding_box([geom1])[0], geom1.x0)
        self.assertCountEqual(gd.common_bounding_box([geom1])[1], geom1.x1)

        # All the dimensions are different
        geom5 = gd.UniformGrid([11, 11], x0=[0, 0], x1=[5, 5])
        geom6 = gd.UniformGrid([21, 121], x0=[-3, -2], x1=[19, 20])

        self.assertCountEqual(
            gd.common_bounding_box([geom5, geom6])[0], [-3, -2]
        )
        self.assertCountEqual(
            gd.common_bounding_box([geom5, geom6])[1], [19, 20]
        )

    def test_merge_uniform_grids(self):

        # Test error for not passing a list
        with self.assertRaises(TypeError):
            gd.merge_uniform_grids(1)

        # Test error for not passing a list of UniformGrid
        with self.assertRaises(TypeError):
            gd.merge_uniform_grids([1, 2])

        geom1 = gd.UniformGrid([101, 101], x0=[1, 1], x1=[3, 5], ref_level=1)
        geom2 = gd.UniformGrid([101, 101], x0=[1, 1], x1=[10, 5], ref_level=2)

        # Different ref levels
        with self.assertRaises(ValueError):
            gd.merge_uniform_grids([geom1, geom2])

        geom3 = gd.UniformGrid([101, 101], x0=[1, 1], x1=[10, 5], ref_level=1)

        # Different dx
        with self.assertRaises(ValueError):
            gd.merge_uniform_grids([geom1, geom3])

        geom4 = gd.UniformGrid(
            [101, 101], x0=[0, -2], dx=geom1.dx, ref_level=1
        )

        expected_geom = gd.UniformGrid(
            [151, 176], x0=[0, -2], x1=[3, 5], dx=geom1.dx, ref_level=1
        )

        self.assertEqual(gd.merge_uniform_grids([geom1, geom4]), expected_geom)

    def test__eq__(self):

        # The tricky part is the time and iteration
        geom0 = gd.UniformGrid([11, 11], x0=[0, 0], x1=[5, 5])
        geom1 = gd.UniformGrid([11, 11], x0=[0, 0], x1=[5, 5])

        self.assertEqual(geom0, geom1)

        geom2 = gd.UniformGrid([11, 11], x0=[0, 0], x1=[5, 5], time=1)

        self.assertNotEqual(geom0, geom2)

        geom3 = gd.UniformGrid([11, 11], x0=[0, 0], x1=[5, 5], time=1)

        self.assertEqual(geom3, geom2)

        geom4 = gd.UniformGrid([11, 11], x0=[0, 0], x1=[5, 5], iteration=1)

        self.assertNotEqual(geom0, geom4)

        geom5 = gd.UniformGrid([11, 11], x0=[0, 0], x1=[5, 5], iteration=1)

        self.assertEqual(geom5, geom4)

        self.assertNotEqual(geom5, 2)


class TestUniformGridData(unittest.TestCase):
    def setUp(self):
        self.geom = gd.UniformGrid([101, 51], x0=[0, 0], x1=[1, 0.5])

    def test_init(self):

        # Test invalid input
        with self.assertRaises(TypeError):
            gd.UniformGridData(1, 0)

        # Test invalid input
        with self.assertRaises(ValueError):
            gd.UniformGridData(self.geom, np.array([2]))

        data = np.array([i * np.linspace(1, 5, 51) for i in range(101)])

        ug_data = gd.UniformGridData(self.geom, data)

        self.assertEqual(ug_data.grid, self.geom)
        self.assertIsNot(ug_data.grid, self.geom)

        self.assertTrue(np.array_equal(ug_data.data, data))
        self.assertIsNot(ug_data.data, data)

        # Test from_grid_structure
        ug_data_from_grid_structure = gd.UniformGridData.from_grid_structure(
            data, x0=[0, 0], x1=[1, 0.5]
        )

        self.assertEqual(ug_data, ug_data_from_grid_structure)

        # Test not equal of UniformGridData
        self.assertNotEqual(ug_data, 2)

        # Test num_dimensions
        self.assertEqual(ug_data.num_dimensions, 2)
        self.assertEqual(ug_data.num_extended_dimensions, 2)

    def test_is_complex(self):

        data = np.array([i * np.linspace(1, 5, 51) for i in range(101)])

        ug_data = gd.UniformGridData(self.geom, data)

        self.assertFalse(ug_data.is_complex())

        ug_data_c = gd.UniformGridData(self.geom, 1j * data)

        self.assertTrue(ug_data_c.is_complex())

    def test_flat_dimensions_remove(self):

        geom = gd.UniformGrid([101, 1], x0=[0, 0], x1=[1, 0])

        data = np.array([i * np.linspace(1, 5, 1) for i in range(101)])
        ug_data = gd.UniformGridData(geom, data)

        ug_data.flat_dimensions_remove()

        flat_geom = gd.UniformGrid([101], x0=[0], x1=[1])

        self.assertEqual(
            ug_data, gd.UniformGridData(flat_geom, np.linspace(0, 100, 101))
        )

        # Check invalidation of spline
        self.assertTrue(ug_data.invalid_spline)

    def test_partial_derive(self):

        geom = gd.UniformGrid([8001, 3], x0=[0, 0], x1=[2 * np.pi, 1])

        sin_wave = gd.sample_function_from_uniformgrid(
            lambda x, y: np.sin(x), geom
        )
        original_sin = sin_wave.copy()

        # Error dimension not found
        with self.assertRaises(ValueError):
            sin_wave.partial_derived(5)

        # Second derivative should still be a -sin
        sin_wave.partial_derive(0, order=2)

        self.assertTrue(
            np.allclose(-sin_wave.data, original_sin.data, atol=1e-3)
        )

        gradient = original_sin.gradient(order=2)
        self.assertTrue(
            np.allclose(-gradient[0].data, original_sin.data, atol=1e-3)
        )

    def test_ghost_zones_remove(self):

        geom = gd.UniformGrid(
            [101, 201], x0=[0, 0], x1=[100, 200], num_ghost=[1, 3]
        )

        data = np.array([i * np.linspace(0, 200, 201) for i in range(101)])
        ug_data = gd.UniformGridData(geom, data)

        ug_data.ghost_zones_remove()

        expected_data = np.array(
            [i * np.linspace(3, 197, 195) for i in range(1, 100)]
        )
        expected_grid = gd.UniformGrid(
            [99, 195], x0=[1, 3], x1=[99, 197], num_ghost=[0, 0]
        )
        expected_ug_data = gd.UniformGridData(expected_grid, expected_data)

        self.assertEqual(ug_data, expected_ug_data)

        # Check invalidation of spline
        self.assertTrue(ug_data.invalid_spline)

        self.assertCountEqual(ug_data.num_ghost, [0, 0])

        # Check with num_ghost = 0
        ug_data.ghost_zones_remove()
        self.assertEqual(ug_data, ug_data.copy())

    def test__apply_reduction(self):

        data = np.array([i * np.linspace(1, 5, 51) for i in range(101)])

        ug_data = gd.UniformGridData(self.geom, data)

        self.assertAlmostEqual(ug_data.min(), 0)
        self.assertAlmostEqual(ug_data.max(), 500)

    def test__apply_binary(self):

        data1 = np.array([i * np.linspace(1, 5, 51) for i in range(101)])
        data2 = np.array([i ** 2 * np.linspace(1, 5, 51) for i in range(101)])
        ug_data1 = gd.UniformGridData(self.geom, data1)
        ug_data2 = gd.UniformGridData(self.geom, data2)

        expected_ug_data = gd.UniformGridData(self.geom, data1 + data2)

        self.assertEqual(ug_data1 + ug_data2, expected_ug_data)

        # Test incompatible grids

        geom = gd.UniformGrid([101, 1], x0=[0, 0], x1=[1, 0])

        data3 = np.array([i * np.linspace(1, 5, 1) for i in range(101)])

        ug_data3 = gd.UniformGridData(geom, data3)

        with self.assertRaises(ValueError):
            ug_data1 + ug_data3

        # Add number
        self.assertEqual(
            ug_data1 + 1, gd.UniformGridData(self.geom, data1 + 1)
        )

        # Incompatible objects
        with self.assertRaises(TypeError):
            ug_data1 + geom

    def test__apply_unary(self):

        data1 = np.array([i * np.linspace(1, 5, 51) for i in range(101)])
        ug_data1 = gd.UniformGridData(self.geom, data1)

        self.assertEqual(
            np.sin(ug_data1), gd.UniformGridData(self.geom, np.sin(data1))
        )

    def test_sample_function(self):

        # Test not grid as input
        with self.assertRaises(TypeError):
            gd.sample_function_from_uniformgrid(np.sin, 0)

        # Test 1d
        geom = gd.UniformGrid(100, x0=0, x1=2 * np.pi)
        data = np.sin(np.linspace(0, 2 * np.pi, 100))

        self.assertEqual(
            gd.sample_function(np.sin, 100, 0, 2 * np.pi),
            gd.UniformGridData(geom, data),
        )

        # Test with additional arguments
        geom_ref_level = gd.UniformGrid(100, x0=0, x1=2 * np.pi, ref_level=0)
        self.assertEqual(
            gd.sample_function(np.sin, 100, 0, 2 * np.pi, ref_level=0),
            gd.UniformGridData(geom_ref_level, data),
        )

        # Test 2d
        geom2d = gd.UniformGrid([100, 200], x0=[0, 1], x1=[1, 2])

        def square(x, y):
            return x * y

        # Test function takes too few arguments
        with self.assertRaises(TypeError):
            gd.sample_function_from_uniformgrid(lambda x: x, geom2d)

        # Test function takes too many arguments
        with self.assertRaises(TypeError):
            gd.sample_function_from_uniformgrid(square, geom)

        # Test other TypeError
        with self.assertRaises(TypeError):
            gd.sample_function_from_uniformgrid(np.sin, geom2d)

        data2d = np.vectorize(square)(*geom2d.coordinates(as_same_shape=True))

        self.assertEqual(
            gd.sample_function(square, [100, 200], [0, 1], [1, 2]),
            gd.UniformGridData(geom2d, data2d),
        )

        self.assertEqual(
            gd.sample_function_from_uniformgrid(square, geom2d),
            gd.UniformGridData(geom2d, data2d),
        )

    def test_splines(self):

        # Let's start with 1d.
        sin_data = gd.sample_function(np.sin, 12000, 0, 2 * np.pi)
        sin_data_complex = sin_data + 1j * sin_data

        # Test unknown ext
        with self.assertRaises(ValueError):
            sin_data.evaluate_with_spline(1, ext=3)

        # Test k!=0!=1
        with self.assertRaises(ValueError):
            sin_data._make_spline(k=3)

        self.assertAlmostEqual(
            sin_data_complex.evaluate_with_spline([np.pi / 3]),
            (1 + 1j) * np.sin(np.pi / 3),
        )

        # Test __call__

        self.assertAlmostEqual(
            sin_data_complex([np.pi / 3]),
            (1 + 1j) * np.sin(np.pi / 3),
        )

        # Vector input
        self.assertTrue(
            np.allclose(
                sin_data_complex.evaluate_with_spline([np.pi / 3, np.pi / 4]),
                np.array(
                    [
                        (1 + 1j) * np.sin(np.pi / 3),
                        (1 + 1j) * np.sin(np.pi / 4),
                    ]
                ),
            )
        )

        # Vector input in, vector input out
        self.assertEqual(sin_data_complex([[1]]).shape, (1,))

        # Now 2d
        def product(x, y):
            return x * (y + 2)

        prod_data = gd.sample_function(product, [101, 101], [0, 0], [3, 3])
        prod_data_complex = (1 + 1j) * prod_data

        self.assertAlmostEqual(
            prod_data_complex.evaluate_with_spline((2, 3)),
            (1 + 1j) * 10,
        )

        # Vector input
        self.assertTrue(
            np.allclose(
                prod_data_complex.evaluate_with_spline([(1, 0), (2, 3)]),
                np.array([(1 + 1j) * 2, (1 + 1j) * 10]),
            )
        )

        self.assertTrue(
            np.allclose(
                prod_data_complex.evaluate_with_spline(
                    [[(1, 0), (2, 3)], [(3, 1), (0, 0)]]
                ),
                np.array([[(1 + 1j) * 2, (1 + 1j) * 10], [(1 + 1j) * 9, 0]]),
            )
        )

        # Real data
        self.assertAlmostEqual(
            prod_data.evaluate_with_spline((2, 3)),
            10,
        )

        # Extrapolate outside
        self.assertAlmostEqual(
            prod_data.evaluate_with_spline((20, 20), ext=1), 0
        )

        self.assertAlmostEqual(
            prod_data_complex.evaluate_with_spline((20, 20), ext=1), 0
        )

        self.assertTrue(prod_data_complex.spline_real.bounds_error)
        self.assertTrue(prod_data_complex.spline_imag.bounds_error)

        # Test on a UniformGrid
        sin_data = gd.sample_function(np.sin, 12000, 0, 2 * np.pi)
        linspace = gd.UniformGrid(101, x0=0, x1=3)
        output = sin_data(linspace)
        self.assertTrue(
            np.allclose(output.data, np.sin(linspace.coordinates()))
        )

    def test_copy(self):

        sin_data = gd.sample_function(np.sin, 1000, 0, 2 * np.pi)

        sin_data2 = sin_data.copy()

        self.assertEqual(sin_data, sin_data2)
        self.assertIsNot(sin_data.data, sin_data2.data)
        self.assertIsNot(sin_data.grid, sin_data2.grid)

    def test_histogram(self):

        # There should be no reason why the histogram behaves differently for
        # different dimensions, so let's test it with 1d
        sin_data = gd.sample_function(np.sin, 1000, 0, 2 * np.pi)
        sin_data_complex = sin_data + 1j * sin_data

        # Test error weights
        with self.assertRaises(TypeError):
            sin_data.histogram(weights=1)

        # Test error complex
        with self.assertRaises(ValueError):
            sin_data_complex.histogram()

        hist = sin_data.histogram()
        expected_hist = np.histogram(sin_data.data, range=(-1, 1), bins=400)

        self.assertTrue(np.allclose(expected_hist[0], hist[0]))
        self.assertTrue(np.allclose(expected_hist[1], hist[1]))

        # Test with weights
        weights = sin_data.copy()
        weights **= 2

        hist = sin_data.histogram(weights)
        expected_hist = np.histogram(
            sin_data.data, range=(-1, 1), bins=400, weights=weights.data
        )

        self.assertTrue(np.allclose(expected_hist[0], hist[0]))
        self.assertTrue(np.allclose(expected_hist[1], hist[1]))

    def test_percentiles(self):

        # There should be no reason why the histogram behaves differently for
        # different dimensions, so let's test it with 1d
        lin_data = gd.sample_function(lambda x: 1.0 * x, 1000, 0, 2 * np.pi)

        # Scalar input
        self.assertAlmostEqual(lin_data.percentiles(0.5), np.pi)

        # Vector input
        self.assertTrue(
            np.allclose(
                lin_data.percentiles([0.25, 0.5]), np.array([np.pi / 2, np.pi])
            )
        )

        # Not normalized
        self.assertTrue(
            np.allclose(
                lin_data.percentiles([250, 500], relative=False),
                np.array([np.pi / 2, np.pi]),
            )
        )

    def test_mean_integral_norm1_norm2(self):

        data = np.array([i ** 2 * np.linspace(1, 5, 51) for i in range(101)])
        ug_data = gd.UniformGridData(self.geom, data)

        self.assertAlmostEqual(ug_data.integral(), np.sum(data) * self.geom.dv)
        self.assertAlmostEqual(
            ug_data.norm1(), np.sum(np.abs(data)) * self.geom.dv
        )
        self.assertAlmostEqual(
            ug_data.norm2(),
            np.sum(np.abs(data) ** 2 * self.geom.dv) ** 0.5,
        )
        self.assertAlmostEqual(
            ug_data.norm_p(3),
            np.sum(np.abs(data) ** 3 * self.geom.dv) ** (1 / 3),
        )
        self.assertAlmostEqual(ug_data.average(), np.mean(data))

    def test_resampled(self):
        def product(x, y):
            return x * (y + 2)

        def product_complex(x, y):
            return (1 + 1j) * x * (y + 2)

        prod_data = gd.sample_function(product, [101, 201], [0, 1], [3, 4])
        prod_data_complex = gd.sample_function(
            product_complex, [3001, 2801], [0, 1], [3, 4]
        )
        # Check error
        with self.assertRaises(TypeError):
            prod_data.resampled(2)

        # Check same grid
        self.assertEqual(prod_data.resampled(prod_data.grid), prod_data)

        new_grid = gd.UniformGrid([51, 101], x0=[1, 2], x1=[2, 3])

        resampled = prod_data_complex.resampled(new_grid)
        exp_resampled = gd.sample_function_from_uniformgrid(
            product_complex, new_grid
        )

        self.assertEqual(resampled.grid, new_grid)
        self.assertTrue(np.allclose(resampled.data, exp_resampled.data))

        # Check that the method of the spline is linear
        self.assertEqual(prod_data_complex.spline_imag.method, "linear")

        # Test using nearest interpolation
        resampled_nearest = prod_data_complex.resampled(
            new_grid, piecewise_constant=True
        )

        self.assertTrue(
            np.allclose(resampled_nearest.data, exp_resampled.data, atol=1e-3)
        )

        # Check that the method of the spline hasn't linear
        self.assertEqual(prod_data_complex.spline_imag.method, "linear")

        # Check single number
        self.assertAlmostEqual(resampled_nearest((2, 2.5)), 9 * (1 + 1j))

        # Check with one point
        prod_data_1 = gd.sample_function(product, [101, 1], [0, 1], [3, 1])
        new_grid2 = gd.UniformGrid([51, 1], x0=[1, 1], x1=[2, 1])
        resampled2 = prod_data_complex.resampled(new_grid2)
        self.assertEqual(resampled2.grid, new_grid2)

    def test_dx_change(self):
        def product_complex(x, y):
            return (1 + 1j) * x * (y + 2)

        prod_data_complex = gd.sample_function(
            product_complex, [301, 401], [0, 1], [3, 4]
        )

        prod_data_complex_copy = prod_data_complex.copy()

        # Test invalid new dx
        # Not a list
        with self.assertRaises(TypeError):
            prod_data_complex.dx_change(0)

        # Not a with the correct dimensions
        with self.assertRaises(ValueError):
            prod_data_complex.dx_change([0])

        # Not a integer multiple/factor
        with self.assertRaises(ValueError):
            prod_data_complex.dx_change(prod_data_complex.dx * np.pi)

        # Same dx
        self.assertEqual(
            prod_data_complex.dx_changed(prod_data_complex.dx),
            prod_data_complex,
        )

        # Half dx
        prod_data_complex.dx_change(prod_data_complex.dx / 2)
        self.assertCountEqual(
            prod_data_complex.dx, prod_data_complex_copy.dx / 2
        )
        self.assertCountEqual(
            prod_data_complex.shape, prod_data_complex_copy.shape * 2 - 1
        )
        # The data part should be tested with testing resample

        # Twice of the dx, which will bring us back to same dx,
        # so, same object we started with
        prod_data_complex.dx_change(prod_data_complex.dx * 2)
        self.assertEqual(prod_data_complex, prod_data_complex_copy)

    def test_coordinates(self):
        def square(x, y):
            return x * (y + 2)

        grid_data = gd.sample_function_from_uniformgrid(square, self.geom)

        self.assertTrue(
            np.allclose(
                grid_data.coordinates_from_grid()[0],
                self.geom.coordinates()[0],
            )
        )

        # This is a list of UniformGridData
        grids = grid_data.coordinates()
        # Here we check that they agree on two coordinates
        for dim in range(len(grids)):
            self.assertAlmostEqual(
                grids[dim](self.geom[2, 3]), self.geom[2, 3][dim]
            )

        # Here we test coordiantes_meshgrid()
        self.assertTrue(
            np.allclose(
                grid_data.coordinates_meshgrid()[0], self.geom.coordinates()[0]
            )
        )

    def test_properties(self):
        def square(x, y):
            return x * (y + 2)

        grid_data = gd.sample_function_from_uniformgrid(square, self.geom)

        self.assertCountEqual(grid_data.x0, self.geom.x0)
        self.assertCountEqual(grid_data.origin, self.geom.x0)
        self.assertCountEqual(grid_data.shape, self.geom.shape)
        self.assertCountEqual(grid_data.x1, self.geom.x1)
        self.assertCountEqual(grid_data.dx, self.geom.dx)
        self.assertCountEqual(grid_data.delta, self.geom.dx)
        self.assertCountEqual(grid_data.num_ghost, self.geom.num_ghost)
        self.assertEqual(grid_data.ref_level, self.geom.ref_level)
        self.assertEqual(grid_data.component, self.geom.component)
        self.assertEqual(grid_data.time, self.geom.time)
        self.assertEqual(grid_data.iteration, self.geom.iteration)

    def test__getitem__(self):
        def square(x, y):
            return x * (y + 2)

        # These are just integers
        prod_data = gd.sample_function(square, [11, 21], [0, 10], [10, 30])

        self.assertAlmostEqual(prod_data[2, 2], 2 * 14)


class TestHierarchicalGridData(unittest.TestCase):
    def setUp(self):
        # Here we split the rectangle with x0 = [0, 1], x1 = [14, 26]
        # and shape [14, 26] in 4 pieces
        grid1 = gd.UniformGrid([4, 5], x0=[0, 1], x1=[3, 5], ref_level=0)
        grid2 = gd.UniformGrid([11, 21], x0=[4, 6], x1=[14, 26], ref_level=0)
        grid3 = gd.UniformGrid([11, 5], x0=[4, 1], x1=[14, 5], ref_level=0)
        grid4 = gd.UniformGrid([4, 21], x0=[0, 6], x1=[3, 26], ref_level=0)

        self.grids0 = [grid1, grid2, grid3, grid4]
        # self.grids1 are not to be merged because they do not fill the space
        self.grids1 = [grid1, grid2]

        def product(x, y):
            return x * (y + 2)

        self.grid_data = [
            gd.sample_function_from_uniformgrid(product, g)
            for g in self.grids0
        ]

        self.grid_data_two_comp = [
            gd.sample_function_from_uniformgrid(product, g)
            for g in self.grids1
        ]

        self.expected_grid = gd.UniformGrid(
            [15, 26], x0=[0, 1], x1=[14, 26], ref_level=0
        )

        self.expected_data = gd.sample_function_from_uniformgrid(
            product, self.expected_grid
        )

        # We also consider one grid data with a different refinement level
        self.expected_grid_level2 = gd.UniformGrid(
            [15, 26], x0=[0, 1], x1=[14, 26], ref_level=2
        )

        self.expected_data_level2 = gd.sample_function_from_uniformgrid(
            product, self.expected_grid_level2
        )

    def test_init(self):

        # Test incorrect arguments
        # Not a list
        with self.assertRaises(TypeError):
            gd.HierarchicalGridData(0)

        # Empty list
        with self.assertRaises(ValueError):
            gd.HierarchicalGridData([])

        # Not a list of UniformGridData
        with self.assertRaises(TypeError):
            gd.HierarchicalGridData([0])

        # Inconsistent number of dimensions
        def product1(x):
            return x

        def product2(x, y):
            return x * y

        prod_data1 = gd.sample_function(product1, [101], [0], [3])
        prod_data2 = gd.sample_function(product2, [101, 101], [0, 0], [3, 3])

        with self.assertRaises(ValueError):
            gd.HierarchicalGridData([prod_data1, prod_data2])

        # Only one component
        one = gd.HierarchicalGridData([prod_data1])
        # Test content
        self.assertDictEqual(
            one.grid_data_dict, {-1: prod_data1.ghost_zones_removed()}
        )

        grid = gd.UniformGrid([101], x0=[0], x1=[3], ref_level=2)

        # Two components at two different levels
        prod_data1_level2 = gd.sample_function_from_uniformgrid(product1, grid)
        two = gd.HierarchicalGridData([prod_data1, prod_data1_level2])
        self.assertDictEqual(
            two.grid_data_dict,
            {
                -1: prod_data1.ghost_zones_removed(),
                2: prod_data1_level2.ghost_zones_removed(),
            },
        )

        # Test a good grid
        hg_many_components = gd.HierarchicalGridData(self.grid_data)
        self.assertEqual(
            hg_many_components.grid_data_dict[0], self.expected_data
        )

        # Test a grid with two separate components
        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)
        self.assertEqual(hg3.grid_data_dict[0], self.grid_data_two_comp)

    def test__getitem__(self):
        hg_many_components = gd.HierarchicalGridData(self.grid_data)
        self.assertEqual(hg_many_components[0], self.expected_data)

    def test_properties(self):

        # len
        hg = gd.HierarchicalGridData(
            self.grid_data + [self.expected_data_level2]
        )
        self.assertEqual(len(hg), 2)

        # iter_level
        self.assertEqual(next(hg.iter_level()), self.expected_data)

        # refinement levels
        self.assertCountEqual(hg.refinement_levels, [0, 2])

        # grid_data
        self.assertCountEqual(
            hg.grid_data, [self.expected_data, self.expected_data_level2]
        )

        # first component
        self.assertEqual(hg.first_component, hg[0])

        # finest level
        self.assertEqual(hg.finest_level, 2)

        # max refinement_level
        self.assertEqual(hg.max_refinement_level, 2)

        # coarsest level
        self.assertEqual(hg.coarsest_level, 0)

        # dtype
        self.assertEqual(hg.dtype, np.float)

        # x0, x1
        self.assertCountEqual(hg.x0, self.expected_data.x0)
        self.assertCountEqual(hg.x1, self.expected_data.x1)
        # For multiple components there should be an error
        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)
        with self.assertRaises(ValueError):
            hg3.x0
        with self.assertRaises(ValueError):
            hg3.x1

        # dx_at_level, dx coarsest, fines
        self.assertCountEqual(hg.dx_at_level(0), [1, 1])
        self.assertCountEqual(hg3.dx_at_level(0), [1, 1])
        self.assertCountEqual(hg.coarsest_dx, [1, 1])
        self.assertCountEqual(hg.finest_dx, [1, 1])

        # num dimensions
        self.assertEqual(hg.num_dimensions, 2)
        self.assertEqual(hg.num_extended_dimensions, 2)

        # time and iteration
        self.assertIs(hg.time, None)
        self.assertIs(hg.iteration, None)

    def test__eq__(self):

        hg1 = gd.HierarchicalGridData(self.grid_data)
        hg2 = gd.HierarchicalGridData([self.expected_data_level2])
        hg3 = gd.HierarchicalGridData([self.expected_data])

        self.assertNotEqual(hg1, hg2)
        self.assertEqual(hg1, hg3)

        # Not same type
        self.assertNotEqual(hg1, 2)

        hg4 = gd.HierarchicalGridData(
            [self.expected_data, self.expected_data_level2]
        )
        # Not same number of refinement levels
        self.assertNotEqual(hg1, hg4)

        # Multiple components
        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)
        self.assertEqual(hg3, hg3)

    def test_copy(self):

        hg1 = gd.HierarchicalGridData(self.grid_data)
        hg2 = hg1.copy()
        self.assertEqual(hg1, hg2)
        self.assertIsNot(hg1, hg2)

        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)
        hg4 = hg3.copy()
        self.assertEqual(hg3, hg4)

    def test_iter(self):

        hg1 = gd.HierarchicalGridData(self.grid_data)

        for ref_level, comp, data in hg1:
            self.assertTrue(isinstance(data, gd.UniformGridData))
            self.assertEqual(ref_level, 0)
            self.assertEqual(comp, -1)

        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)

        comp_index = 0
        for ref_level, comp, data in hg3:
            self.assertEqual(ref_level, 0)
            self.assertEqual(comp, comp_index)
            self.assertTrue(isinstance(data, gd.UniformGridData))
            comp_index += 1

        # Test from finest
        geom = gd.UniformGrid(
            [81, 3], x0=[0, 0], x1=[2 * np.pi, 1], ref_level=0
        )
        geom2 = gd.UniformGrid(
            [11, 3], x0=[0, 0], x1=[2 * np.pi, 1], ref_level=1
        )

        sin_wave1 = gd.sample_function_from_uniformgrid(
            lambda x, y: np.sin(x), geom
        )
        sin_wave2 = gd.sample_function_from_uniformgrid(
            lambda x, y: np.sin(x), geom2
        )

        sin_wave = gd.HierarchicalGridData([sin_wave1] + [sin_wave2])

        index = 1
        for ref_level, comp, data in sin_wave.iter_from_finest():
            self.assertEqual(ref_level, index)
            self.assertEqual(comp, -1)
            self.assertTrue(isinstance(data, gd.UniformGridData))
            index -= 1

    def test__apply_reduction(self):

        hg1 = gd.HierarchicalGridData(self.grid_data)

        self.assertAlmostEqual(hg1.min(), 0)

        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)

        self.assertAlmostEqual(hg3.min(), 0)

    def test__apply_unary(self):

        hg1 = gd.HierarchicalGridData(self.grid_data)

        def neg_product(x, y):
            return -x * (y + 2)

        neg_data = gd.sample_function_from_uniformgrid(
            neg_product, self.expected_grid
        )

        hg2 = gd.HierarchicalGridData([neg_data])

        self.assertEqual(-hg1, hg2)

        # Test with multiple components
        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)

        hg4 = hg3.copy()
        hg4[0][0] *= -1
        hg4[0][1] *= -1

        self.assertEqual(-hg3, hg4)

    def test__apply_binary(self):

        hg1 = gd.HierarchicalGridData(self.grid_data)

        # Test incompatible types
        with self.assertRaises(TypeError):
            hg1 + "hey"

        def neg_product(x, y):
            return -x * (y + 2)

        neg_data = gd.sample_function_from_uniformgrid(
            neg_product, self.expected_grid
        )

        hg2 = gd.HierarchicalGridData([neg_data])

        zero = hg1 + hg2
        zero += 0

        # To check that zero is indeed zero we check that the abs max of the
        # data is 0
        self.assertEqual(np.amax(np.abs(zero[0].data)), 0)

        # Test incompatible refinement levels

        neg_data_level2 = gd.sample_function_from_uniformgrid(
            neg_product, self.expected_grid_level2
        )

        with self.assertRaises(ValueError):
            hg1 + gd.HierarchicalGridData([neg_data_level2])

        # Test with multiple components
        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)

        hg4 = hg3.copy()
        hg4[0][0] *= -1
        hg4[0][1] *= -1

        zero2 = hg3 + hg4
        self.assertEqual(np.amax(np.abs(zero2[0][0].data)), 0)
        self.assertEqual(np.amax(np.abs(zero2[0][1].data)), 0)

    def test_finest_level_component_at_point(self):

        hg = gd.HierarchicalGridData(
            self.grid_data + [self.expected_data_level2]
        )

        # Input is not a valid point
        with self.assertRaises(TypeError):
            hg.finest_level_component_at_point(0)

        # Dimensionality mismatch
        with self.assertRaises(ValueError):
            hg.finest_level_component_at_point([0])

        # Point outside the grid
        with self.assertRaises(ValueError):
            hg.finest_level_component_at_point([1000, 200])

        self.assertEqual(hg.finest_level_component_at_point([3, 4]), 2)

        # Test with multiple components
        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)
        self.assertCountEqual(
            hg3.finest_level_component_at_point([3, 4]), (0, 0)
        )

    def test_evaluate_at_point(self):

        hg = gd.HierarchicalGridData(self.grid_data)

        self.assertAlmostEqual(hg._evaluate_at_one_point((2, 3)), 10)

        # Test with multiple components
        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)

        self.assertAlmostEqual(hg3._evaluate_at_one_point((2, 3)), 10)

    def test_call_evalute_with_spline(self):

        # Teting call is the same as evalute_with_spline

        hg = gd.HierarchicalGridData(self.grid_data)
        # Test with multiple components
        hg3 = gd.HierarchicalGridData(self.grid_data_two_comp)

        # Scalar input
        self.assertAlmostEqual(hg((2, 3)), 10)
        self.assertAlmostEqual(hg3((2, 3)), 10)

        # Vector input in, vector input out
        self.assertEqual(hg([(2, 3)]).shape, (1,))

        # Scalar input that pretends to be vector
        self.assertAlmostEqual(hg([(2, 3)]), 10)
        self.assertAlmostEqual(hg3([(2, 3)]), 10)

        # Vector input
        self.assertCountEqual(hg([(2, 3), (3, 2)]), [10, 12])
        self.assertCountEqual(hg3([(2, 3), (3, 2)]), [10, 12])

        def product(x, y):
            return x * (y + 2)

        # Uniform grid as input
        grid = gd.UniformGrid([3, 5], x0=[0, 1], x1=[2, 5])
        grid_data = gd.sample_function_from_uniformgrid(product, grid)
        self.assertTrue(np.allclose(hg3(grid), grid_data.data))

    def test_merge_refinement_levels(self):
        # This also tests to_UniformGrid

        # We redefine this to be ref_level=1
        grid1 = gd.UniformGrid([4, 5], x0=[0, 1], x1=[3, 5], ref_level=1)
        grid2 = gd.UniformGrid([11, 21], x0=[4, 6], x1=[14, 26], ref_level=1)

        grids = [grid1, grid2]

        # Here we use the same data with another big refinement level sampled
        # from the same function
        big_grid = gd.UniformGrid(
            [16, 26], x0=[0, 1], x1=[30, 51], ref_level=0
        )

        def product(x, y):
            return x * (y + 2)

        grid_data_two_comp = [
            gd.sample_function_from_uniformgrid(product, g) for g in grids
        ]

        grid_data = gd.sample_function_from_uniformgrid(product, big_grid)
        hg = gd.HierarchicalGridData(grid_data_two_comp + [grid_data])
        # When I merge the data I should just get big_grid at the resolution
        # of self.grid_data_two_comp
        expected_grid = gd.UniformGrid(
            [31, 51], x0=[0, 1], x1=[30, 51], ref_level=-1
        )

        expected_data = gd.sample_function_from_uniformgrid(
            product, expected_grid
        )
        self.assertEqual(hg.merge_refinement_levels(), expected_data)

    def test_coordinates(self):

        hg_coord = gd.HierarchicalGridData(self.grid_data).coordinates()
        # Test with multiple components
        hg2_coord = gd.HierarchicalGridData(
            self.grid_data_two_comp
        ).coordinates()

        self.assertAlmostEqual(hg_coord[0]((2, 3)), 2)
        self.assertAlmostEqual(hg2_coord[0]((2, 3)), 2)
        self.assertAlmostEqual(hg_coord[1]((2, 3)), 3)
        self.assertAlmostEqual(hg2_coord[1]((2, 3)), 3)

    def test_str(self):

        hg = gd.HierarchicalGridData(self.grid_data_two_comp)
        expected_str = "Available refinement levels (components):\n"
        expected_str += "0 (2)\n"
        expected_str += "Spacing at coarsest level (0): [1. 1.]\n"
        expected_str += "Spacing at finest level (0): [1. 1.]"
        self.assertEqual(expected_str, hg.__str__())

    def test_partial_derivated(self):
        # Here we are also testing _call_component_method

        geom = gd.UniformGrid(
            [8001, 3], x0=[0, 0], x1=[2 * np.pi, 1], ref_level=0
        )
        geom2 = gd.UniformGrid(
            [10001, 3], x0=[0, 0], x1=[2 * np.pi, 1], ref_level=1
        )

        sin_wave1 = gd.sample_function_from_uniformgrid(
            lambda x, y: np.sin(x), geom
        )
        sin_wave2 = gd.sample_function_from_uniformgrid(
            lambda x, y: np.sin(x), geom2
        )
        original_sin1 = sin_wave1.copy()
        original_sin2 = sin_wave2.copy()

        sin_wave = gd.HierarchicalGridData([sin_wave1] + [sin_wave2])
        sin_copy = sin_wave.copy()

        # Second derivative should still be a -sin
        sin_wave.partial_derive(0, order=2)

        self.assertTrue(
            np.allclose(-sin_wave[0].data, original_sin1.data, atol=1e-3)
        )
        self.assertTrue(
            np.allclose(-sin_wave[1].data, original_sin2.data, atol=1e-3)
        )

        # Test _call_component_method with non-string name
        with self.assertRaises(TypeError):
            sin_wave._call_component_method(sin_wave)

        # Test _call_component_method with non existing method
        with self.assertRaises(ValueError):
            sin_wave._call_component_method("lol")

        gradient = sin_copy.gradient(order=2)

        self.assertTrue(
            np.allclose(-gradient[0][0].data, original_sin1.data, atol=1e-3)
        )
        self.assertTrue(
            np.allclose(-gradient[0][1].data, original_sin2.data, atol=1e-3)
        )
