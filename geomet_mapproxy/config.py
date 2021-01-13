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

import click

from geomet_mapproxy import cli_options
from geomet_mapproxy.env import (GEOMET_MAPPROXY_CACHE_CONFIG,
                                 GEOMET_MAPPROXY_CONFIG, GEOMET_MAPPROXY_TMP)

LOGGER = logging.getLogger(__name__)

TMP_FILE = os.path.join(GEOMET_MAPPROXY_TMP, 'geomet-mapproxy-config.yml')


@click.group()
def config():
    """Manage MapProxy configuration"""
    pass


@click.command()
@click.pass_context
def create(ctx):
    """Create initial MapProxy configuration"""

    click.echo('Creating {}'.format(TMP_FILE))
    click.echo('Reading from initial layer list ({})'.format(
       GEOMET_MAPPROXY_CACHE_CONFIG))
    click.echo('Moving to {}'.format(GEOMET_MAPPROXY_CONFIG))

    pass


@click.command()
@click.pass_context
@cli_options.OPTION_LAYERS
def update(ctx, layers):
    """Update MapProxy configuration"""

    click.echo('Reading {}'.format(GEOMET_MAPPROXY_CONFIG))
    click.echo('Writing to {}'.format(TMP_FILE))
    click.echo('Moving to {}'.format(GEOMET_MAPPROXY_CONFIG))

    pass


config.add_command(create)
config.add_command(update)
