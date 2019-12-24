# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
"""Methods for CLI push functionality."""

import click
import os
import tarfile
import shutil

from distutils.dir_util import copy_tree

from aea.cli.common import logger
from aea.cli.registry.utils import request_api, load_yaml, clean_tarfiles


def _remove_pycache(source_dir: str):
    pycache_path = os.path.join(source_dir, '__pycache__')
    if os.path.exists(pycache_path):
        shutil.rmtree(pycache_path)


def _compress_dir(output_filename: str, source_dir: str):
    _remove_pycache(source_dir)
    with tarfile.open(output_filename, "w:gz") as f:
        f.add(source_dir, arcname=os.path.basename(source_dir))


@clean_tarfiles
def push_item(item_type: str, item_name: str) -> None:
    """
    Push item to the Registry.

    :param item_type: str type of item (connection/protocol/skill).
    :param item_name: str item name.

    :return: None
    """
    item_type_plural = item_type + 's'
    cwd = os.getcwd()

    items_folder = os.path.join(cwd, item_type_plural)
    item_path = os.path.join(items_folder, item_name)
    logger.debug(
        'Searching for {} {} in {} ...'
        .format(item_name, item_type, items_folder)
    )
    if not os.path.exists(item_path):
        raise click.ClickException(
            '{} "{}" not found  in {}. Make sure you run push command '
            'from a correct folder.'.format(
                item_type.title(), item_name, items_folder
            )
        )

    output_filename = '{}.tar.gz'.format(item_name)
    logger.debug(
        'Compressing {} {} to {} ...'
        .format(item_name, item_type, output_filename)
    )
    _compress_dir(output_filename, item_path)
    output_filepath = os.path.join(cwd, output_filename)

    item_config_filepath = os.path.join(item_path, '{}.yaml'.format(item_type))
    logger.debug('Reading {} {} config ...'.format(item_name, item_type))
    item_config = load_yaml(item_config_filepath)

    data = {
        'name': item_name,
        'description': item_config['description'],
        'version': item_config['version']
    }
    path = '/{}/create'.format(item_type_plural)
    logger.debug('Pushing {} {} to Registry ...'.format(item_name, item_type))
    resp = request_api(
        'POST', path, data=data, auth=True, filepath=output_filepath
    )
    click.echo(
        'Successfully pushed {} {} to the Registry. Public ID: {}'.format(
            item_type, item_name, resp['public_id']
        )
    )


def get_packages_path() -> str:
    """
    Get path to packages folder.

    Should not be called from outside the project dir.

    :return: str path to packages dir.
    """
    project_parent_dir = os.path.abspath('__file__').split(
        '{0}agents-aea{0}'.format(os.path.sep)
    )[0]
    return os.path.join(project_parent_dir, 'agents-aea', 'packages')


def _get_item_source_path(
    cwd: str, item_type_plural: str, item_name: str
) -> str:
    source_path = os.path.join(cwd, item_type_plural, item_name)
    if not os.path.exists(source_path):
        raise click.ClickException(
            'Item "{}" not found in {}.'.format(item_name, cwd)
        )
    return source_path


def _get_item_target_path(item_type_plural: str, item_name: str) -> str:
    packages_path = get_packages_path()
    target_path = os.path.join(packages_path, item_type_plural, item_name)
    if os.path.exists(target_path):
        raise click.ClickException(
            'Item "{}" already exists in packages folder.'.format(item_name)
        )
    return target_path


def save_item_locally(item_type: str, item_name: str) -> None:
    """
    Save item to local packages.

    :param item_type: str type of item (connection/protocol/skill).
    :param item_name: str item name.

    :return: None
    """
    item_type_plural = item_type + 's'
    cwd = os.getcwd()

    source_path = _get_item_source_path(cwd, item_type_plural, item_name)
    target_path = _get_item_target_path(item_type_plural, item_name)
    copy_tree(source_path, target_path)
    click.echo(
        '{} "{}" successfully saved in packages folder.'
        .format(item_type.title(), item_name)
    )
