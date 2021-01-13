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

from geomet_mapproxy.cli_env import GEOMET_MAPPROXY_CACHE_DATA
from geomet_mapproxy import cli_options

LOGGER = logging.getLogger(__name__)


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
              help='Force deletion')
def clean(ctx, layer, force):
    """Clean cache directories"""

    to_delete = False

    if force:
        to_delete = True

    if click.confirm('Continue?'):
        to_delete = True

    if layer is not None:
        if layer == 'all':
            layer_to_delete = GEOMET_MAPPROXY_CACHE_DATA
        else:
            layer_to_delete = os.path.join(GEOMET_MAPPROXY_CACHE_DATA, layer)

    if to_delete:
        click.echo('Removing {}'.format(layer_to_delete))
        shutil.rmtree(layer_to_delete)

        if layer_to_delete == GEOMET_MAPPROXY_CACHE_DATA:
            click.echo('Recreating {}'.format(GEOMET_MAPPROXY_CACHE_DATA))
            create(ctx)


cache.add_command(clean)
cache.add_command(create)
