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
