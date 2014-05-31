# Copyright 2012 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from oslo.config import cfg

CONF = cfg.CONF

opt = cfg.StrOpt('baa')

CONF.register_opt(opt, group='baar')

num_opt = cfg.IntOpt('baaad',
                     default=7,
                     required=True,
                     help='number of bad items')
CONF.register_opt(num_opt)

str_opt = cfg.StrOpt('zooey',
                     default='dewey')
CONF.register_opt(str_opt)

empty_str_opt = cfg.StrOpt('doe',
                           default=' ')
CONF.register_opt(empty_str_opt)

start_path = cfg.StrOpt('start_path',
                        default='~/seedbox')
CONF.register_opt(start_path)

list_opt = cfg.ListOpt('tests',
                       default=['test1', 'test2', 'test3'])
CONF.register_opt(list_opt)

bool_opt = cfg.BoolOpt('enabled',
                       default=True)
CONF.register_cli_opt(bool_opt)


SYNC_OPTS = [
    cfg.BoolOpt('dryrun',
                default=False,
                help='rsync dryrun option'),
    cfg.BoolOpt('verbose',
                default=False,
                help='rsync verbose option'),
    cfg.BoolOpt('progress',
                default=False,
                help='rsync progress option'),
    cfg.BoolOpt('perms',
                default=True,
                help='rsync perms option'),
    cfg.BoolOpt('delayupdates',
                default=True,
                help='rsync delayupdates option'),
    cfg.BoolOpt('recursive',
                default=True,
                help='rsync recursive option'),
    cfg.StrOpt('chmod',
               default='ugo+rwx',
               help='rsync chmod option'),
    cfg.StrOpt('identity',
               help='rsync-ssh identity option (ssh key)'),
    cfg.StrOpt('port',
               default='22',
               help='rsync-ssh port'),
    cfg.StrOpt('remote_user',
               help='User name on remote system (ssh)'),
    cfg.StrOpt('remote_host',
               help='Host name/IP Address of remote system'),
    cfg.StrOpt('remote_path',
               help='rsync destination path'),
]

CONF.register_opts(SYNC_OPTS, group='allsync')
