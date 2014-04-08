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

def_opt = cfg.BoolOpt('fooey',
                      default=False,
                      help='default boolean flag, ooey gooey fooey')
CONF.register_opt(def_opt)

opt = cfg.StrOpt('foo')

CONF.register_opt(opt, group='bar')

fl_opt = cfg.FloatOpt('weight',
                      default=1.1)
CONF.register_opt(fl_opt, group='bar')

list_opt = cfg.ListOpt('crazy',
                       default=['sample', 'people'],
                       deprecated_name='bob',
                       deprecated_group='sunny')
CONF.register_opt(list_opt)

multi_opt = cfg.MultiStrOpt('numbers',
                            default=['one.two.three.four.five.six'])
CONF.register_opt(multi_opt)

other_multi_opt = cfg.MultiStrOpt('strings',
                                  default=[''])
CONF.register_opt(other_multi_opt)
