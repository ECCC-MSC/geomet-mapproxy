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
import mappyfile
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


def from_wms(layers=[]):
    """
    Derives temporal information from a WMS

    :param layers:
    :param layers: `list` of layer names

    :returns: `dict` of layer temporal configuration
    """

    if GEOMET_MAPPROXY_CACHE_WMS is None:
        raise RuntimeError('GEOMET_MAPPROXY_CACHE_WMS not set')

    ltu = {}
    for layer in layers:
        LOGGER.debug('Requesting WMS Capabilities for layer: {}'.format(layer['name']))
        url = '{}?layer={}'.format(GEOMET_MAPPROXY_CACHE_WMS, layer['name'])
        wms = WebMapService(url, version='1.3.0')

        dimensions_list = ['time', 'reference_time']
        for dimension in dimensions_list:
            if dimension in wms[layer['name']].dimensions.keys():
                if layer['name'] not in ltu.keys():
                    ltu[layer['name']] = {}
                ltu[layer['name']][dimension] = {
                    'default': wms[layer['name']].dimensions[dimension]['default'],
                    'values': wms[layer['name']].dimensions[dimension]['values']
                }
    return ltu


def from_mapfile(layers):
    """
    Derives temporal information from a MapServer mapfile

    :param mapfile: filepath to mapfile on disk
    :param layers: `list` of layer names

    :returns: `dict` of layer temporal configuration
    """

    if GEOMET_MAPPROXY_CACHE_MAPFILE is None:
        raise RuntimeError('GEOMET_MAPPROXY_CACHE_MAPFILE not set')

    ltu = {}
    all_layers = False

    if len(layers) == 0 or layers == 'all':
        LOGGER.debug('Processing all layers')
        all_layers = True
        LOGGER.debug('Reading global mapfile from disk')
        f = mappyfile.open(GEOMET_MAPPROXY_CACHE_MAPFILE)

    for layer in layers:
        if not all_layers:
            filepath = '{}/geomet-{}-en.map'.format(
                os.path.dirname(GEOMET_MAPPROXY_CACHE_MAPFILE), layer['name'])
            LOGGER.debug('Reading layer mapfile from disk')
            f = mappyfile.open(filepath)

        if layer['name'] not in ltu.keys():
            ltu[layer['name']] = {}

        if ('wms_timeextent' in f['layers'][0]['metadata'].keys()):
            ltu[layer['name']]['time'] = {
                'default': f['layers'][0]['metadata']['wms_timedefault'],
                'values': [f['layers'][0]['metadata']['wms_timeextent']]
            }
        if ('wms_reference_time_default' in f['layers'][0]['metadata'].keys()):
            ltu[layer['name']]['reference_time'] = {
                'default':
                    f['layers'][0]['metadata']['wms_reference_time_default'],
                'values':
                    [f['layers'][0]['metadata']['wms_reference_time_extent']]
            }
    return ltu


def from_xml(layers):
    """
    Derives temporal information from a Capabilities XML file on disk

    :param mapfile: filepath to Capabilities XML on disk
    :param layers: `list` of layer names

    :returns: `dict` of layer temporal configuration
    """

    if GEOMET_MAPPROXY_CACHE_XML is None:
        raise RuntimeError('GEOMET_MAPPROXY_CACHE_XML not set')

    ltu = {}

    LOGGER.debug('Reading global WMS Capabilities XML from disk')
    with open(GEOMET_MAPPROXY_CACHE_XML, 'rb') as fh:
        xml = fh.read()

        wms = WebMapService('url', version='1.3.0', xml=xml)

        for layer in layers:
            dimensions_list = ['time', 'reference_time']
            for dimension in dimensions_list:
                if dimension in wms[layer['name']].dimensions.keys():
                    if layer['name'] not in ltu.keys():
                        ltu[layer['name']] = {}
                    ltu[layer['name']][dimension] = {
                        'default': wms[layer['name']].dimensions[dimension]['default'],
                        'values': wms[layer['name']].dimensions[dimension]['values']
                    }
    return ltu


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
        layer['styles'].append("default")
        for style in layer['styles']:
            LOGGER.debug('Configuring layer: {}_{}'.format(layer['name'], style))
            LOGGER.debug('Configuring layer caches')
            caches['{}_cache_{}'.format(layer['name'], style)] = {
                'grids': ['GLOBAL_GEODETIC'],
                'sources': ['{}_source_{}'.format(layer['name'], style)]
            }

        LOGGER.debug('Configuring layer sources')
        for style in layer['styles']:
            sources['{}_source_{}'.format(layer['name'], style)] = {
                'forward_req_params': ['time', 'dim_reference_time'],
                'req': {
                    'layers': layer['name'],
                    'transparent': True,
                    'url': c['wms-server']['url'],
                    'styles': style
                },
                'type': 'wms'
            }

        for style in layer['styles']:
            if 'RADAR' in layer['name']:
                layers.append({
                    'name': "{}_{}".format(layer['name'], style),
                    'title': "{}_{}".format(layer['name'], style),
                    'sources': ['{}_cache_{}'.format(layer['name'], style)],
                    'dimensions': {
                        'time': {
                            'default': None,
                            'values': []
                        }
                    }
                })
            else:
                layers.append({
                    'name': "{}_{}".format(layer['name'], style),
                    'title': "{}_{}".format(layer['name'], style),
                    'sources': ['{}_cache_{}'.format(layer['name'], style)],
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
        dict_, c['wms-server']['layers'], mode)

    return final_dict

def update_mapproxy_config(mapproxy_config, layers=[], mode='wms'):
    """
    Updates MapProxy configuration with current temporal information

    :param mapproxy_config: `dict` of MapProxy configuration
    :param layers: `list` of layer names
    :param mode: mode of deriving temporal properties

    :returns: `dict` of updated configuration
    """

    if mode == 'wms':
        layers_to_update = from_wms(layers)
    elif mode == 'xml':
        layers_to_update = from_xml(layers)
    elif mode == 'mapfile':
        layers_to_update = from_mapfile(layers)

    for layer in mapproxy_config['layers']:
        for key in layers_to_update.keys():
            if key in layer['name']:
                for dim in layers_to_update[key].keys():
                    layer['dimensions'][dim]['default'] = (
                        layers_to_update[key][dim]['default'])
                    layer['dimensions'][dim]['values'] = (
                        layers_to_update[key][dim]['values'])

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
        ctx.invoke(create, mode=mode)
        return

    click.echo('Reading {}'.format(GEOMET_MAPPROXY_CONFIG))
    layers_ = [x.strip() for x in layers.split(',')]

    click.echo('Updating layers {}'.format(layers_))
    try:
        with open(GEOMET_MAPPROXY_CONFIG, 'rb') as fh:
            mapproxy_config = yaml_load(fh)

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
