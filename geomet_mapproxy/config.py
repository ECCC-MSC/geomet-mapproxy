# =================================================================
#
# Author: Tom Kralidis <tom.kralidis@ec.gc.ca>
#
# Copyright (c) 2023 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import logging
import os
import shutil

import click
import mappyfile
from owslib.wms import WebMapService
import yaml

from geomet_mapproxy import cli_options
from geomet_mapproxy.env import (
    GEOMET_MAPPROXY_CACHE_CONFIG,
    GEOMET_MAPPROXY_CACHE_DATA,
    GEOMET_MAPPROXY_CACHE_MAPFILE,
    GEOMET_MAPPROXY_CACHE_XML,
    GEOMET_MAPPROXY_CACHE_WMS,
    GEOMET_MAPPROXY_CONFIG,
    GEOMET_MAPPROXY_TMP
)
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
        LOGGER.debug('Requesting WMS Capabilities for layer: {}'.format(layer))
        url = '{}?layer={}'.format(GEOMET_MAPPROXY_CACHE_WMS, layer)
        wms = WebMapService(url, version='1.3.0')

        for dimension in wms[layer].dimensions.keys():
            if layer not in ltu.keys():
                ltu[layer] = {}
            ltu[layer][dimension] = {
                'default': wms[layer].dimensions[dimension]['default'],
                'values': wms[layer].dimensions[dimension]['values']
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
                os.path.dirname(GEOMET_MAPPROXY_CACHE_MAPFILE), layer
            )
            LOGGER.debug('Reading layer mapfile from disk')
            f = mappyfile.open(filepath)

        if layer not in ltu.keys():
            ltu[layer] = {}

        if 'wms_timeextent' in f['layers'][0]['metadata'].keys():
            ltu[layer]['time'] = {
                'default': f['layers'][0]['metadata']['wms_timedefault'],
                'values': [f['layers'][0]['metadata']['wms_timeextent']]
            }
        if 'wms_reference_time_default' in f['layers'][0]['metadata'].keys():
            ltu[layer]['reference_time'] = {
                'default': f['layers'][0]['metadata'][
                    'wms_reference_time_default'
                ],
                'values': [
                    f['layers'][0]['metadata']['wms_reference_time_extent']
                ]
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
            for dimension in wms[layer].dimensions.keys():
                if layer not in ltu.keys():
                    ltu[layer] = {}
                ltu[layer][dimension] = {
                    'default': wms[layer].dimensions[dimension]['default'],
                    'values': wms[layer].dimensions[dimension]['values']
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
        LOGGER.debug('Configuring layer: {}'.format(layer))
        LOGGER.debug('Configuring layer caches')
        caches['{}_cache'.format(layer)] = {
            'grids': [
                'GLOBAL_GEODETIC',
                'GLOBAL_WEBMERCATOR',
                'CANADA_ATLAS_LAMBERT'
            ],
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
            'type': 'wms',
            'wms_opts': {
                'featureinfo_format': 'application/vnd.ogc.gml',
                'legendgraphic': True,
                'version': '1.3.0'
            }
        }

        layers.append(
            {
                'name': layer,
                'title': layer,
                'sources': ['{}_cache'.format(layer)],
            }
        )

    dict_ = {
        'sources': sources,
        'caches': caches,
        'layers': layers,
        'globals': {
            'cache': {
                'base_dir': GEOMET_MAPPROXY_CACHE_DATA,
            },
            'http': {
                'headers': {
                    'User-agent': (
                        'geomet-mapproxy '
                        '(https://github.com/ECCC-MSC/geomet-mapproxy)'
                    )
                }
            },
        },
        'grids': {
            'CANADA_ATLAS_LAMBERT': {
                'srs': 'EPSG:3978',
                'bbox': [-7192737.96, -3004297.73, 5183275.29, 4484204.83]
            }
        },
        'services': {
            'demo': None,
            'wms': {
                'md': {'title': c['wms-server']['name']},
                'versions': ['1.3.0', '1.1.1'],
                'srs': ['EPSG:4326', 'EPSG:3857', 'EPSG:3978']
            }
        }
    }
    final_dict = update_mapproxy_config(dict_, c['wms-server']['layers'], mode)

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
        layer_name = layer['name']
        if layer_name in layers_to_update:
            for dim in layers_to_update[layer_name].keys():
                if 'dimensions' not in layer.keys():
                    layer['dimensions'] = {}
                layer['dimensions'][dim] = {
                    'default': layers_to_update[layer_name][dim]['default'],
                    'values': layers_to_update[layer_name][dim]['values']
                }

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

    click.echo(
        'Reading from initial layer list ({})'.format(
            GEOMET_MAPPROXY_CACHE_CONFIG
        )
    )

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
