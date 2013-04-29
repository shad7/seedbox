#!/usr/bin/python

import logging, logging.config
logging.config.fileConfig("logging.cfg", disable_existing_loggers=False)

from simple_actions import SimpleAction
 
 
#import inspect
 
#for member in inspect.getmembers(SimpleAction, predicate=inspect.ismethod):
#    print 'Member: [%s]' % member
#
#for item in dir(SimpleAction):
#    print 'item: [%s]' % item

#action = SimpleAction()

#for item in dir(action):
#    print 'item: [%s]' % item

#print '_workflows: [%s]' % action._workflows
#
#state_field = action._workflows.get('state')
#print 'state_field: %s' % state_field
#print 'state field wf: %s' % state_field.workflow
#
#print '_xworkflows_implems: [%s]' % action._xworkflows_implems
#
#imp_list = action._xworkflows_implems.get('state')
#print 'imp_list: %s' % imp_list
#
#print 'imp_list state_field: %s' % imp_list.state_field
#print 'imp_list workflow: %s' % imp_list.workflow
#print 'imp_list impls: %s' % imp_list.implementations
#
#for impkey in imp_list.implementations.keys():
#    print 'doc: %s' % imp_list.implementations[impkey].__doc__
#
#print 'imp_list tran at: %s' % imp_list.transitions_at
#print 'imp_list cust impls: %s' % imp_list.custom_implems


#print 'Action Workflow: [%s]' % action.state.workflow
#print 'Workflow Impl Class: [%s]' % action.state.workflow.implementation_class
#
#print '_xworkflows_implems: [%s]' % action._xworkflows_implems

#exit(0)

import random

def get_next_step_func(action, tran_name):
    """
    get the function we need to execute to perform transition
    """
    imp_dict = action._xworkflows_implems.get('state')

    #imp_dict.implementations[tran_name].implementation

    return imp_dict.transitions_at.get(tran_name)
 
any_num = random.randint(1, 999999)

action = SimpleAction()
 

while not action.state.is_done and not action.state.is_cancelled:

    print 'Action State: [%s]' % action.state
    # we only need first one since it is a 1:1 mapping of state
    # to transition; therefore no need to go beyond first entry
    transition = list(action.state.transitions())[0]
    print 'Transition [%s]' % transition

    method_name = get_next_step_func(action, transition.name)
    tran_method = getattr(action, method_name)
    print 'transition method [%s]' % tran_method

    if not callable(tran_method):
        print 'method=[%s] is not callable; stopping workflow' % transition.name
        break

    print 'executiong tran method [%s]' % tran_method
    # load and pass torrents to method but for now, we'll just be happy
    # if this really works
    tran_method('%s-%d' % (action.state.name, any_num))

    print 'method execution complete'
    # then update the torrents after it completes

    print '(updated) Action State: [%s]' % action.state

# end of loop



#print 'Action State: [%s]' % action.state
#print 'Action Transition(s): [%s]' % list(action.state.transitions())[0].name
#
#action.step1()
#print 'Action State: [%s]' % action.state
#print 'Action Transition(s): [%s]' % action.state.transitions
#
#action.step2()
#print 'Action State: [%s]' % action.state
#print 'Action Transition(s): [%s]' % action.state.transitions
#
#action.step3()
#print 'Action State: [%s]' % action.state
#print 'Action Transition(s): [%s]' % action.state.transitions
#
#if action.state.is_ready or action.state.is_active:
#    action.step4()
#    print 'Action State: [%s]' % action.state
#    print 'Action Transition(s): [%s]' % action.state.transitions
#else:
#    print 'Unable to execute...'

