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
import yaml

from geomet_mapproxy import cli_options
from geomet_mapproxy.env import (GEOMET_MAPPROXY_CACHE_CONFIG,
                                 GEOMET_MAPPROXY_CONFIG, GEOMET_MAPPROXY_TMP)

LOGGER = logging.getLogger(__name__)

TMP_FILE = os.path.join(GEOMET_MAPPROXY_TMP, 'geomet-mapproxy-config.yml')


def create_initial_mapproxy_config(mapproxy_cache_config):
    """
    Creates initial MapProxy configuration with current temporal information

    :param mapproxy_cache_config: `dict` of cache configuration

    :returns: `dict` of new configuration
    """

    # TODO: add implementation

    return {}


def update_mapproxy_config(mapproxy_config, layers=[]):
    """
    Updates MapProxy configuration with current temporal information

    :param mapproxy_config: `dict` of MapProxy configuration
    :param layers: `list` of layer names

    :returns: `dict` of updated configuration
    """

    # TODO: add implementation

    return {}


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

    with open(GEOMET_MAPPROXY_CACHE_CONFIG) as fh:
        mapproxy_cache_config = yaml.load(fh, Loader=yaml.SafeLoader)

    try:
        dict_ = create_initial_mapproxy_config(mapproxy_cache_config)
        with open(GEOMET_MAPPROXY_CONFIG, 'wb') as fh:
            fh.write(dict_)
    except RuntimeError as err:
        LOGGER.error(err)
        raise click.ClickException('Error creating config: {}'.format(err))

    click.echo('Moving to {}'.format(GEOMET_MAPPROXY_CONFIG))
    shutil.move(TMP_FILE, GEOMET_MAPPROXY_CONFIG)
    click.echo('Done')


@click.command()
@click.pass_context
@cli_options.OPTION_LAYERS
def update(ctx, layers):
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
            mapproxy_config = yaml.load(fh, Loader=yaml.SafeLoader)

        dict_ = update_mapproxy_config(mapproxy_config, layers_)

        with open(TMP_FILE, 'wb') as fh:
            fh.write(dict_)

        click.echo('Moving to {}'.format(GEOMET_MAPPROXY_CONFIG))
        shutil.move(TMP_FILE, GEOMET_MAPPROXY_CONFIG)
    except RuntimeError as err:
        LOGGER.error(err)
        raise click.ClickException('Error updating config: {}'.format(err))

    click.echo('Done')


config.add_command(create)
config.add_command(update)
