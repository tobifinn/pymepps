#!/bin/env python
# -*- coding: utf-8 -*-
#
# Created on 06.07.17
#
# Created for pymepps
#
# @author: Tobias Sebastian Finn, tobias.sebastian.finn@studium.uni-hamburg.de
#
#    Copyright (C) {2017}  {Tobias Sebastian Finn}
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# System modules
import os
import unittest
import logging
import datetime

# External modules
import xarray as xr
import numpy as np
import pandas.util.testing as pdt

# Internal modules
import pymepps.accessor
from pymepps.loader.datasets.spatialdataset import SpatialDataset
from pymepps.loader.filehandler.netcdfhandler import NetCDFHandler
from pymepps.grid import GridBuilder


BASE_PATH = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.realpath(__file__))))),
    'data')

logging.basicConfig(level=logging.DEBUG)

logging.info(BASE_PATH)


class TestSpatial(unittest.TestCase):
    def setUp(self):
        file = os.path.join(BASE_PATH, 'model', 'GFS_Global_0p25deg_20161219_0600.nc')
        ds = SpatialDataset(NetCDFHandler(file),)
        self.array = xr.open_dataarray(file)
        self.grid = ds.get_grid(
            'Maximum_temperature_height_above_ground_Mixed_intervals_Maximum',
            data_array=self.array)

    def tearDown(self):
        try:
            os.remove('test.nc')
        except FileNotFoundError:
            pass

    def test_array_has_accessor(self):
        self.assertTrue(hasattr(self.array, 'pp'))

    def test_accessor_has_array_as_data(self):
        self.assertEqual(id(self.array.pp.data), id(self.array))

    def test_grid_returns_grid(self):
        self.array.pp.grid = self.grid
        self.assertEqual(self.array.pp._grid, self.array.pp.grid)

    def test_str_returns_right(self):
        name = "{0:s}({1:s})".format(self.array.pp.__class__.__name__,
                                     self.array.name)
        test_str = "{0:s}\n{1:s}\nGrid: {1:s}".format(
            name, '-'*len(name), str(None))
        self.assertEqual(test_str, str(self.array.pp))

    def test_grid_could_set(self):
        self.assertEqual(self.array.pp._grid, None)
        self.array.pp.grid = self.grid
        self.assertEqual(self.array.pp._grid, self.grid)

    def test_grid_set_raises_type_error_if_wrong_type(self):
        with self.assertRaises(TypeError):
            self.array.pp.grid = self.array

    def test_check_data_coords_raises_typeerror_if_no_grid(self):
        with self.assertRaises(TypeError):
            self.array.pp.check_data_coordinates(self.array)

    def test_check_data_coords_returns_item(self):
        self.array.pp.grid = self.grid
        return_item = self.array.pp.check_data_coordinates(self.array)
        xr.testing.assert_identical(return_item, self.array)

    def test_check_data_coords_raises_valueerror_if_wrong_coords(self):
        self.array.pp.grid = self.grid
        test_array = self.array[:, :, :5, :5]
        with self.assertRaises(ValueError):
            self.array.pp.check_data_coordinates(test_array)

    def test_merge_checks_input(self):
        test_array = self.array[:, :, :5, :5]
        test_array.pp._grid = self.grid
        with self.assertRaises(ValueError):
            test_array.pp.merge(self.array)
        self.array.pp.grid = self.grid
        self.array.pp.merge()
        with self.assertRaises(ValueError):
            self.array.pp.merge(test_array)

    def test_merge_returns_merged_array(self):
        test_array = self.array.copy()
        test_array.name = 'test'
        test_dataset = xr.merge([test_array, self.array])
        merged_array = test_dataset.to_array(name='merged_array')
        self.array.pp.grid = self.grid
        returned_array = self.array.pp.merge(test_array)
        np.testing.assert_equal(merged_array.values, returned_array.values)

    def test_merge_merged_array_has_same_grid(self):
        test_array = self.array.copy()
        test_array.name = 'test'
        self.array.pp.grid = self.grid
        merged_array = self.array.pp.merge(test_array)
        self.assertIsNotNone(merged_array.pp.grid)
        self.assertEqual(id(self.grid), id(merged_array.pp.grid))

    def test_update_checks_input(self):
        test_array = self.array[:, :, :5, :5]
        test_array.pp._grid = self.grid
        with self.assertRaises(ValueError):
            test_array.pp.update(self.array)
        self.array.pp.grid = self.grid
        self.array.pp.update()
        with self.assertRaises(ValueError):
            self.array.pp.update(test_array)

    def test_update_add_data_to_coords(self):
        test_array = self.array.copy()
        test_array['time'] = [datetime.datetime.utcnow(), ]
        concatenated_array = xr.concat([self.array, test_array], dim='time')
        self.array.pp.grid = self.grid
        updated_array = self.array.pp.update(test_array)
        np.testing.assert_equal(updated_array.values, concatenated_array.values)

    def test_update_updates_data(self):
        test_array = self.array.copy()
        test_array[:] = 5
        self.array.pp.grid = self.grid
        updated_array = self.array.pp.update(test_array)
        self.assertTrue(np.all(updated_array == 5))

    def test_update_raises_error_if_concat_is_not_working(self):
        test_array = self.array.copy()
        test_array[:] = 5
        del test_array['time']
        self.array.pp.grid = self.grid
        with self.assertRaises(TypeError):
            _ = self.array.pp.update(test_array)

    def test_update_updated_array_has_same_grid(self):
        test_array = self.array.copy()
        test_array[:] = 5
        self.array.pp.grid = self.grid
        updated_array = self.array.pp.update(test_array)
        self.assertIsNotNone(updated_array.pp.grid)
        self.assertEqual(id(self.grid), id(updated_array.pp.grid))

    def test_set_grid_cooordinates_returns_grid_array(self):
        returned_array = self.array.pp.set_grid(self.grid)
        self.assertEqual(id(returned_array.pp.grid), id(self.grid))

    def test_set_grid_coordinates_sets_names(self):
        self.array = self.array.rename({'lat': 'y', 'lon': 'x'})
        old_dim_names = np.array(self.array.dims)
        true_dim_names = list(old_dim_names[:-2]) + ['lat', 'lon']
        np.testing.assert_equal(np.array(self.array.dims), old_dim_names)
        gridded_array = self.array.pp.set_grid(self.grid)
        np.testing.assert_equal(np.array(gridded_array.dims), true_dim_names)

    def test_set_grid_sets_values(self):
        coord_values = self.grid.raw_dim
        self.array['lat'] = np.arange(self.array['lat'].size)
        self.array['lon'] = np.arange(self.array['lon'].size)
        self.assertFalse(any([
            np.all(np.equal(self.array[dim].values, coord_values[num]))
            for num, dim in enumerate(self.array.dims[-2:])])
        )
        self.array = self.array.pp.set_grid(self.grid)
        self.assertTrue(all([
            np.all(np.equal(self.array[dim].values, coord_values[num]))
            for num, dim in enumerate(self.array.dims[-2:])])
        )

    def test_set_grid_raises_value_error_if_no_grid_given_and_set(self):
        with self.assertRaises(ValueError):
            self.array.pp.set_grid()

    def test_set_grid_uses_own_grid_if_no_grid_given(self):
        self.array.pp._grid = self.grid
        gridded_array = self.array.pp.set_grid()
        self.assertEqual(gridded_array.pp._grid, self.array.pp._grid)

    def test_merge_analysis_timedelta_merges_times(self):
        test_array = self.array.copy()
        test_array = test_array.expand_dims('runtime')
        test_array.coords['runtime'] = [datetime.datetime.now(), ]
        test_array = test_array.rename({'time': 'validtime'})
        test_array['validtime'] = test_array['validtime'].values - \
                                  test_array['runtime'].values
        merged_array = test_array.pp.merge_analysis_timedelta()
        np.testing.assert_equal(merged_array.dims, self.array.dims)
        np.testing.assert_equal(merged_array.values, self.array.values)

    def test_merge_analysis_timedelta_returns_grid_if_grid(self):
        test_array = self.array.copy()
        test_array = test_array.expand_dims('runtime')
        test_array.coords['runtime'] = [datetime.datetime.now(), ]
        test_array = test_array.rename({'time': 'validtime'})
        test_array['validtime'] = test_array['validtime'].values - \
                                  test_array['runtime'].values
        test_array.pp.grid = self.grid
        merged_array = test_array.pp.merge_analysis_timedelta()
        self.assertEqual(merged_array.pp.grid, test_array.pp.grid)

    def test_merge_analysis_timedelta_returns_no_grid_if_no_grid(self):
        test_array = self.array.copy()
        test_array = test_array.expand_dims('runtime')
        test_array.coords['runtime'] = [datetime.datetime.now(), ]
        test_array = test_array.rename({'time': 'validtime'})
        test_array['validtime'] = test_array['validtime'].values - \
                                  test_array['runtime'].values
        merged_array = test_array.pp.merge_analysis_timedelta()
        with self.assertRaises(TypeError):
            merged_array.pp.grid

    def test_to_pandas_no_lonlat_given_returns_stacked_dataframe(self):
        stacked_array = self.array.stack(col=self.array.dims[1:])
        target_df = stacked_array.to_pandas()
        returned_df = self.array.pp.to_pandas()
        # Trick to speed up the whole thing
        pdt.assert_frame_equal(target_df.T, returned_df.T, check_dtype=False)

    def test_to_pandas_lonlat_given_returns_point_dataframe(self):
        self.array.pp.grid = self.grid
        returned_df = self.array.pp.to_pandas((10, 53.5))
        self.array = self.array.sel(lat=53.5).sel(lon=10)
        stacked_array = self.array.stack(col=self.array.dims[1:])
        target_df = stacked_array.to_pandas()
        pdt.assert_frame_equal(target_df, returned_df, check_dtype=False)

    def test_remapnn_interpolates_with_nearest_neighbour_approach(self):
        file = os.path.join(BASE_PATH, 'grids', 'gaussian_y')
        builder = GridBuilder(file)
        gaussian_grid = builder.build_grid()
        self.array.pp.grid = self.grid
        returned_array = self.array.pp.remapnn(gaussian_grid)
        remapped_array = self.grid.interpolate(self.array, gaussian_grid, 0)
        remapped_array.pp.grid = gaussian_grid
        xr.testing.assert_equal(returned_array, remapped_array)

    def test_remapbil_interpolates_with_nearest_neighbour_approach(self):
        file = os.path.join(BASE_PATH, 'grids', 'gaussian_y')
        logging.info(file)
        builder = GridBuilder(file)
        gaussian_grid = builder.build_grid()
        self.array.pp.grid = self.grid
        returned_array = self.array.pp.remapbil(gaussian_grid)
        remapped_array = self.grid.interpolate(self.array, gaussian_grid, 1)
        remapped_array.pp.grid = gaussian_grid
        xr.testing.assert_equal(returned_array, remapped_array)

    def test_lonlatbox_slices_lonlatbox_from_array(self):
        lonlatbox = (9, 55, 12, 52)
        self.array.pp.grid = self.grid.copy()
        returned_array = self.array.pp.sellonlatbox(lonlatbox)
        sliced_array, sliced_grid = self.grid.lonlatbox(self.array, lonlatbox)
        sliced_array.pp.grid = sliced_grid
        xr.testing.assert_equal(returned_array, sliced_array)
        self.assertEqual(sliced_grid, returned_array.pp.grid)

    def test_save_creates_new_nc_file(self):
        self.assertFalse(os.path.isfile('test.nc'))
        self.array.pp.save('test.nc')
        self.assertTrue(os.path.isfile('test.nc'))

    def test_save_saves_same_data(self):
        self.array.pp.save('test.nc')
        opened_array = xr.open_dataarray('test.nc')
        xr.testing.assert_equal(opened_array, self.array)

    def test_save_saves_also_grid(self):
        self.array.pp.grid = self.grid
        self.array.pp.save('test.nc')
        opened_array = xr.open_dataarray('test.nc')
        grid_attrs = {attr[7:]: opened_array.attrs[attr]
                      for attr in opened_array.attrs if attr[:7] == 'ppgrid_'}
        opened_grid = GridBuilder(grid_attrs).build_grid()
        self.assertEqual(self.grid, opened_grid)

    def test_load_load_data_without_grid(self):
        self.array.to_netcdf('test.nc')
        opened_array = xr.DataArray.pp.load('test.nc')
        xr.testing.assert_equal(self.array, opened_array)

    def test_load_load_also_grid(self):
        self.array.pp.grid = self.grid
        self.array.pp.save('test.nc')
        opened_array = xr.DataArray.pp.load('test.nc')
        self.assertEqual(opened_array.pp.grid, self.grid)

    def test_load_removes_grid_attrs(self):
        self.array.pp.grid = self.grid
        self.array.pp.save('test.nc')
        non_gridded_array = xr.open_dataarray('test.nc')
        non_gridded_attrs = [attr for attr in non_gridded_array.attrs
                             if attr[:7] == 'ppgrid_']
        self.assertTrue(non_gridded_attrs)
        gridded_array = xr.DataArray.pp.load('test.nc')
        gridded_attrs = [attr for attr in gridded_array.attrs
                         if attr[:7] == 'ppgrid_']
        self.assertFalse(gridded_attrs)

    def test_get_coord_name_detects_approx_variants(self):
        variant = dict(approx=['ti', ], exact=[])
        returned_coord = self.array.pp._get_coord_name(variant)
        self.assertEqual(returned_coord, 'time')

    def test_get_coord_name_detects_approx_variants_if_exact(self):
        variant = dict(approx=['time', ], exact=[])
        returned_coord = self.array.pp._get_coord_name(variant)
        self.assertEqual(returned_coord, 'time')

    def test_get_coord_name_detects_exact_variants(self):
        variant = dict(exact=['time', ], approx=[])
        returned_coord = self.array.pp._get_coord_name(variant)
        self.assertEqual(returned_coord, 'time')

    def test_get_coord_name_detects_not_exact_variants_if_approx(self):
        variant = dict(exact=['ti', ], approx=[])
        returned_coord = self.array.pp._get_coord_name(variant)
        self.assertIsNone(returned_coord)

    def test_get_coord_name_returns_none_if_no_coord(self):
        variant = dict(exact=['run', ], approx=['runtime', ])
        returned_coord = self.array.pp._get_coord_name(variant)
        self.assertIsNone(returned_coord)

    def test_get_coord_name_resub_non_alpha(self):
        variant = dict(exact=['heightaboveground', ], approx=[])
        returned_coord = self.array.pp._get_coord_name(variant)
        self.assertEqual(returned_coord, self.array.dims[1])

    def test_get_coord_name_uses_list_as_exact(self):
        variant = ['heightaboveground', ]
        returned_coord = self.array.pp._get_coord_name(variant)
        self.assertEqual(returned_coord, self.array.dims[1])

    def test_create_coord_returns_array(self):
        returned_array = self.array.pp._create_coord(self.array, 'test_coord')
        self.assertIsInstance(returned_array, xr.DataArray)

    def test_create_coord_creates_dim_with_name(self):
        self.assertNotIn('test_coord', self.array.dims)
        returned_array = self.array.pp._create_coord(self.array, 'test_coord')
        self.assertIn('test_coord', returned_array.dims)

    def test_create_coord_new_dim_on_first_position(self):
        self.assertNotEqual('test_coord', self.array.dims[0])
        returned_array = self.array.pp._create_coord(self.array, 'test_coord')
        self.assertEqual('test_coord', returned_array.dims[0])

    def test_create_coord_copy_original_array(self):
        returned_array = self.array.pp._create_coord(self.array, 'test_coord')
        self.assertNotEqual(id(returned_array), id(self.array))

    def test_create_coord_expand_dims(self):
        returned_array = self.array.pp._create_coord(self.array, 'test_coord')
        self.assertEqual(len(returned_array.dims), len(self.array.dims)+1)

    def test_create_coord_creates_coordinate(self):
        returned_array = self.array.pp._create_coord(self.array, 'test_coord')
        self.assertIn('test_coord', returned_array.coords)

    def test_create_coord_sets_parameter(self):
        returned_array = self.array.pp._create_coord(self.array, 'test_coord',
                                                     'bla')
        np.testing.assert_equal(returned_array.coords['test_coord'].values,
                                np.array(('bla', )))

    def test_create_coord_raises_valueerror_if_already_exists(self):
        with self.assertRaises(ValueError):
            _ = self.array.pp._create_coord(self.array, 'time')

    def test_rename_coord_returns_dataarray(self):
        renamed_array = self.array.pp._rename_coord(self.array, 'time',
                                                    'validtime')
        self.assertIsInstance(renamed_array, xr.DataArray)

    def test_rename_coord_renames_coord(self):
        self.assertIn('time', self.array.dims)
        renamed_array = self.array.pp._rename_coord(self.array, 'time',
                                                    'validtime')
        self.assertNotIn('time', renamed_array.dims)
        self.assertIn('validtime', renamed_array.dims)

    def test_rename_coord_renamed_dim_has_same_pos(self):
        renamed_array = self.array.pp._rename_coord(self.array, 'time',
                                                    'validtime')
        self.assertEqual(self.array.dims.index('time'),
                         renamed_array.dims.index('validtime'))

    def test_rename_coord_renames_also_coord(self):
        self.assertIn('time', self.array.coords)
        renamed_array = self.array.pp._rename_coord(self.array, 'time',
                                                    'validtime')
        self.assertNotIn('time', renamed_array.coords)
        self.assertIn('validtime', renamed_array.coords)
        np.testing.assert_equal(self.array['time'].values,
                                renamed_array['validtime'].values)

    def test_normalize_order_orders_coordinates(self):
        self.array = self.array.pp._create_coord(self.array, 'ensemble')
        self.array = self.array.pp._create_coord(self.array, 'runtime')
        self.array = self.array.pp._rename_coord(
            self.array, 'time', 'validtime')
        self.array = self.array.pp._rename_coord(
            self.array, 'height_above_ground', 'height')
        dims = list(self.array.dims)
        dims.append(dims[0])
        self.array = self.array.transpose(*dims[1:])
        normalized_array = self.array.pp._get_normalized_order(self.array)
        np.testing.assert_equal(
            np.array(normalized_array.dims),
            np.array(
                ['runtime', 'ensemble', 'validtime', 'height', 'lat', 'lon']
            )
        )

    def test_normalize_order_takes_variable_as_first(self):
        self.array = self.array.pp._create_coord(self.array, 'ensemble')
        self.array = self.array.pp._create_coord(self.array, 'runtime')
        self.array = self.array.pp._rename_coord(
            self.array, 'time', 'validtime')
        self.array = self.array.pp._rename_coord(
            self.array, 'height_above_ground', 'height')
        self.array = self.array.pp._create_coord(self.array, 'variable')
        normalized_array = self.array.pp._get_normalized_order(self.array)
        self.assertEqual('variable', normalized_array.dims[0])

    def test_transform_datetime_returns_dataarray(self):
        transformed_array = self.array.pp._transform_datetime(self.array)
        self.assertIsInstance(transformed_array, xr.DataArray)

    def test_transform_to_datetime_transforms_datetime_to_npdatetime(self):
        self.array = self.array.pp._create_coord(
            self.array, 'runtime', datetime.datetime.now())
        self.assertIsInstance(self.array['runtime'].values[0],
                              datetime.datetime)
        transformed_array = self.array.pp._transform_datetime(self.array)
        self.assertIsInstance(transformed_array['runtime'].values[0],
                              np.datetime64)

    def test_transform_datetime64_to_nanoseconds(self):
        now = np.datetime64(datetime.datetime.now(), 'D')
        self.array = self.array.pp._create_coord(
            self.array, 'runtime', now)
        transformed_array = self.array.pp._transform_datetime(self.array)
        self.assertEqual(transformed_array['runtime'].values.dtype,
                         now.astype('datetime64[ns]').dtype)

    def test_validtime_to_timedelta_returns_dataarray(self):
        self.array = self.array.pp._create_coord(
            self.array, 'runtime', datetime.datetime.utcnow())
        transformed_array = self.array.pp._validtime_to_timedelta(
            self.array, validtime='time')
        self.assertIsInstance(transformed_array, xr.DataArray)

    def test_validtime_to_timedelta_checks_if_both_npdatetime(self):
        now = datetime.datetime.utcnow()
        wrong_array = self.array.pp._create_coord(self.array, 'runtime', now)
        transformed_array = self.array.pp._validtime_to_timedelta(
            wrong_array, validtime='time')
        self.assertFalse(
            np.issubdtype(transformed_array['time'].values.dtype,
                          np.timedelta64))
        right_array = wrong_array.pp._transform_datetime(wrong_array)
        transformed_array = self.array.pp._validtime_to_timedelta(
            right_array, validtime='time')
        self.assertTrue(
            np.issubdtype(transformed_array['time'].values.dtype,
                          np.timedelta64))

    def test_validtime_to_timedelta_uses_given_runtime_and_validtime(self):
        self.array = self.array.pp._create_coord(
            self.array, 'runtime', datetime.datetime.utcnow())
        self.array = self.array.pp._create_coord(
            self.array, 'validtime', datetime.datetime.utcnow())
        self.array = self.array.pp._create_coord(
            self.array, 'anatime', datetime.datetime.utcnow())
        self.array = self.array.pp._transform_datetime(self.array)
        right_coordinate = self.array['time'].values - \
            self.array['anatime'].values
        transformed_array = self.array.pp._validtime_to_timedelta(
            self.array, validtime='time', runtime='anatime'
        )
        np.testing.assert_equal(transformed_array['time'].values,
                                right_coordinate)

    def test_normalize_coords_returns_dataarray(self):
        normalized_array = self.array.pp.normalize_coords()
        self.assertIsInstance(normalized_array, xr.DataArray)

    def test_normalize_coords_renames_coordinates_with_given_names(self):
        self.assertIn('time', self.array.dims)
        normalized_array = self.array.pp.normalize_coords()
        self.assertNotIn('time', normalized_array.dims)
        self.assertIn('validtime', normalized_array.dims)

    def test_normalize_coords_create_coordinate_if_not_exists(self):
        self.assertNotIn('runtime', self.array.dims)
        normalized_array = self.array.pp.normalize_coords()
        self.assertIn('runtime', normalized_array.dims)

    def test_normalize_coords_sets_parameters(self):
        normalized_array = self.array.pp.normalize_coords(ensemble=100)
        np.testing.assert_equal(normalized_array['ensemble'].values,
                                np.array((100, )))

    def test_normalize_coords_orders_coords(self):
        dims = list(self.array.dims)
        dims.append(dims[0])
        self.array = self.array.transpose(*dims[1:])
        normalized_array = self.array.pp.normalize_coords()
        np.testing.assert_equal(
            np.array(normalized_array.dims),
            np.array(
                ['runtime', 'ensemble', 'validtime', 'height', 'lat', 'lon']
            )
        )

    def test_normalize_coords_creates_timedelta(self):
        normalized_array = self.array.pp.normalize_coords(
            runtime=datetime.datetime.utcnow())
        self.assertTrue(
            np.issubdtype(normalized_array['validtime'].values.dtype,
                          np.timedelta64))

if __name__ == '__main__':
    unittest.main()
