###############################################################################
#
# Copyright (C) 2021 Tom Kralidis
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import logging
import os
import shutil

import click
from owslib.wms import WebMapService
import yaml

from geomet_mapproxy import cli_options
from geomet_mapproxy.env import (GEOMET_MAPPROXY_CACHE_CONFIG,
                                 GEOMET_MAPPROXY_CACHE_MAPFILE,
                                 GEOMET_MAPPROXY_CACHE_XML,
                                 GEOMET_MAPPROXY_CACHE_WMS,
                                 GEOMET_MAPPROXY_CONFIG, GEOMET_MAPPROXY_TMP)
from geomet_mapproxy.util import yaml_load

LOGGER = logging.getLogger(__name__)

TMP_FILE = os.path.join(GEOMET_MAPPROXY_TMP, 'geomet-mapproxy-config.yml')


def create_initial_mapproxy_config(mapproxy_cache_config, mode='wms'):
    """
    Creates initial MapProxy configuration with current temporal information

    :param mapproxy_cache_config: `dict` of cache configuration
    :param mode: mode of deriving temporal properties

    :returns: `dict` of new configuration
    """

    sources = {}
    caches = {}
    layers = []

    c = mapproxy_cache_config

    LOGGER.debug('Building up configuration')
    for layer in mapproxy_cache_config['wms-server']['layers']:
        LOGGER.debug('Configuring layer: {}'.format(layer))
        LOGGER.debug('Configuring layer caches')
        caches['{}_cache'.format(layer)] = {
            'grids': ['GLOBAL_GEODETIC'],
            'sources': ['{}_source'.format(layer)]
        }

        LOGGER.debug('Configuring layer sources')
        sources['{}_source'.format(layer)] = {
            'forward_req_params': ['time', 'dim_reference_time'],
            'req': {
                'layers': layer,
                'transparent': True,
                'url': c['wms-server']['url']
            },
            'type': 'wms'
        }

        if 'RADAR' in layer:
            layers.append({
                'name': layer,
                'title': layer,
                'sources': ['{}_cache'.format(layer)],
                'dimensions': {
                    'time': {
                        'default': None,
                        'values': []
                    }
                }
            })
        else:
            layers.append({
                'name': layer,
                'title': layer,
                'sources': ['{}_cache'.format(layer)],
                'dimensions': {
                    'time': {
                        'default': None,
                        'values': []
                    },
                    'reference_time': {
                        'default': None,
                        'values': []
                    }
                }
            })

    dict_ = {
        'sources': sources,
        'caches': caches,
        'layers': layers,
        'globals': None,
        'services': {
            'demo': None,
            'wms': {
                'md': {
                    'title': c['wms-server']['name']
                },
                'versions': ['1.1.1', '1.3.0']
            }
        }
    }
    final_dict = update_mapproxy_config(
        dict_, c['wms-server']['layers'], 'wms')

    return final_dict


def update_mapproxy_config(mapproxy_config, layers=[], mode='wms'):
    """
    Updates MapProxy configuration with current temporal information

    :param mapproxy_config: `dict` of MapProxy configuration
    :param layers: `list` of layer names
    :param mode: mode of deriving temporal properties

    :returns: `dict` of updated configuration
    """

    def from_wms(layers=[]):
        """
        Derives temporal information from a WMS

        :param layers:
        :param layers: `list` of layer names

        :returns: `dict` of layer temporal configuration
        """

        if GEOMET_MAPPROXY_CACHE_WMS is None:
            raise RuntimeError('WMS not set')

        ltu = {}
        for layer in layers:
            url = '{}?layer={}'.format(GEOMET_MAPPROXY_CACHE_WMS, layer)
            wms = WebMapService(url, version='1.3.0')

            dimensions_list = ['time', 'reference_time']
            for dimension in dimensions_list:
                if dimension in wms[layer].dimensions.keys():
                    if layer not in ltu.keys():
                        ltu[layer] = {}
                    ltu[layer][dimension] = {
                        'default': wms[layer].dimensions[dimension]['default'],
                        'values': wms[layer].dimensions[dimension]['values']
                    }

        return ltu

    def from_mapfile(mapfile, layers):
        """
        Derives temporal information from a MapServer mapfile

        :param mapfile: filepath to mapfile on disk
        :param layers: `list` of layer names

        :returns: `dict` of layer temporal configuration
        """

        if GEOMET_MAPPROXY_CACHE_MAPFILE is None:
            raise RuntimeError('mapfile not set')

        return {}

    def from_xml(xml, layers):
        """
        Derives temporal information from a Capabilities XML file on disk

        :param mapfile: filepath to Capabilities XML on disk
        :param layers: `list` of layer names

        :returns: `dict` of layer temporal configuration
        """

        if GEOMET_MAPPROXY_CACHE_XML is None:
            raise RuntimeError('xml not set')

        return {}

    if mode == 'wms':
        layers_to_update = from_wms(layers)
    elif mode == 'xml':
        layers_to_update = from_xml(layers)
    elif mode == 'mapfile':
        layers_to_update = from_mapfile(layers)

    for layer in mapproxy_config['layers']:
        layer_name = layer['name']
        if layer_name in layers_to_update:
            for dim in layers_to_update[layer_name].keys():
                layer['dimensions'][dim]['default'] = (
                    layers_to_update[layer_name][dim]['default'])
                layer['dimensions'][dim]['values'] = (
                    layers_to_update[layer_name][dim]['values'])

    return mapproxy_config


@click.group()
def config():
    """Manage MapProxy configuration"""
    pass


@click.command()
@click.pass_context
@cli_options.OPTION_MODE
def create(ctx, mode='wms'):
    """Create initial MapProxy configuration"""

    click.echo('Creating {}'.format(TMP_FILE))

    click.echo('Reading from initial layer list ({})'.format(
       GEOMET_MAPPROXY_CACHE_CONFIG))

    with open(GEOMET_MAPPROXY_CACHE_CONFIG) as fh:
        mapproxy_cache_config = yaml_load(fh)

    try:
        dict_ = create_initial_mapproxy_config(mapproxy_cache_config, mode)
        with open(TMP_FILE, 'w') as fh:
            yaml.dump(dict_, fh)
    except RuntimeError as err:
        LOGGER.error(err)
        raise click.ClickException('Error creating config: {}'.format(err))

    click.echo('Moving to {}'.format(GEOMET_MAPPROXY_CONFIG))
    shutil.move(TMP_FILE, GEOMET_MAPPROXY_CONFIG)
    click.echo('Done')


@click.command()
@click.pass_context
@cli_options.OPTION_LAYERS
@cli_options.OPTION_MODE
def update(ctx, layers, mode='wms'):
    """Update MapProxy configuration"""

    if layers is None:
        click.echo('Updating all layers')
        ctx.invoke(create)
        return

    click.echo('Reading {}'.format(GEOMET_MAPPROXY_CONFIG))
    layers_ = [x.strip() for x in layers.split(',')]

    click.echo('Updating layers {}'.format(layers_))
    try:
        with open(GEOMET_MAPPROXY_CONFIG, 'rb') as fh:
            mapproxy_config = yaml_load(fh, Loader=yaml.SafeLoader)

        dict_ = update_mapproxy_config(mapproxy_config, layers_, mode)

        with open(TMP_FILE, 'w') as fh:
            yaml.dump(dict_, fh)

        click.echo('Moving to {}'.format(GEOMET_MAPPROXY_CONFIG))
        shutil.move(TMP_FILE, GEOMET_MAPPROXY_CONFIG)
    except RuntimeError as err:
        LOGGER.error(err)
        raise click.ClickException('Error updating config: {}'.format(err))

    click.echo('Done')


config.add_command(create)
config.add_command(update)
