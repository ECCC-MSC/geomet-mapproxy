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

from geomet_mapproxy import cli_options
from geomet_mapproxy.env import (GEOMET_MAPPROXY_CACHE_DATA,
                                 GEOMET_MAPPROXY_CONFIG)
from geomet_mapproxy.util import yaml_load

LOGGER = logging.getLogger(__name__)

GRIDS_TO_EPSG_DIRNAMES = {
    'GLOBAL_GEODETIC': 'EPSG4326'
}


@click.group()
def cache():
    """Manage MapProxy cache"""
    pass


@click.command()
@click.pass_context
def create(ctx):
    """Create default base cache directory"""

    click.echo('Creating {}'.format(GEOMET_MAPPROXY_CACHE_DATA))
    try:
        os.makedirs(GEOMET_MAPPROXY_CACHE_DATA)
        click.echo('Done')
    except FileExistsError:
        click.echo('Directory already exists')


@click.command()
@click.pass_context
@cli_options.OPTION_LAYERS
@click.option('--force', '-f', 'force', is_flag=True, default=False,
              required=True, help='Force deletion')
def clean(ctx, layers, force):
    """Clean cache directories"""

    to_delete = False
    dirs_to_delete = []

    if layers is None:
        raise click.ClickException('--layers must be "all" or a list')

    if force:
        to_delete = True

    if not force and click.confirm('Continue?'):
        to_delete = True

    if not to_delete:
        click.echo('Exiting')
        return

    if layers is not None:
        if layers == 'all':
            dirs_to_delete = [GEOMET_MAPPROXY_CACHE_DATA]
        else:
            layer_dirs = [x.strip() for x in layers.split(',')]
            with open(GEOMET_MAPPROXY_CONFIG) as fh:
                yaml_config = yaml_load(fh)

            for ld in layer_dirs:
                cache_layer = list(filter(lambda x: x['name'] == ld,
                                   yaml_config['layers']))
                if cache_layer:
                    LOGGER.debug('Found layer')
                    LOGGER.debug('Finding layer caches')
                    caches = cache_layer[0]['sources']
                    for cache in caches:
                        grids = yaml_config['caches'][cache]['grids']
                        LOGGER.debug('Finding layer cache grids')
                        for grid in grids:
                            dirname = '{}_{}'.format(
                                cache, GRIDS_TO_EPSG_DIRNAMES[grid])
                            ltd = os.path.join(GEOMET_MAPPROXY_CACHE_DATA,
                                               dirname)
                            LOGGER.debug('Adding {} to delete'.format(ltd))
                            dirs_to_delete.append(ltd)

    if to_delete:
        click.echo('Removing cache directories')
        for dtd in dirs_to_delete:
            if os.path.isdir(dtd):
                click.echo('Deleting {}'.format(dtd))
                shutil.rmtree(dtd)

        if not os.path.isdir(GEOMET_MAPPROXY_CACHE_DATA):
            click.echo('Recreating {}'.format(GEOMET_MAPPROXY_CACHE_DATA))
            ctx.invoke(create)


cache.add_command(clean)
cache.add_command(create)
