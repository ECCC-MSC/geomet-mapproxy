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

    if click.confirm('Continue?'):
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
