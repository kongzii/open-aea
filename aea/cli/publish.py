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

"""Implementation of the 'aea publish' subcommand."""
import click

from aea.cli.common import pass_ctx, Context, DEFAULT_AEA_CONFIG_FILE, Path
from aea.cli.registry.publish import publish_agent, save_agent_locally
from aea.cli.registry.utils import get_default_registry_path


@click.command(name='publish')
@click.option(
    '--registry', is_flag=True, help="For publishing agent to Registry."
)
@pass_ctx
def publish(ctx: Context, registry):
    """Publish Agent to Registry."""
    if not registry:
        packages_path = get_default_registry_path(ctx)
        save_agent_locally(packages_path)
    else:
        publish_agent()
