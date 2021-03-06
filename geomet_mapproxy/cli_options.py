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

import click

OPTION_LAYERS = click.option(
    '--layers', default=None,
    help='CSV list of layer names (layer1,layer2,...) or "all" for all layers')
OPTION_MODE = click.option(
    '--mode', default='wms', type=click.Choice(['mapfile', 'wms', 'xml']),
    help='mode of deriving temporal properties')
