"""
Manages the overflow of execution
"""
from __future__ import absolute_import
import logging
import xworkflows

from oslo.config import cfg

from seedbox import processmap, datamanager
from seedbox.workflow import Taskflow

log = logging.getLogger(__name__)

DEFAULT_MAX_RETRY = 5


class ProcessError(Exception):
    """
    Identify when the Process errors
    """
    def __init__(self, value):
        super(ProcessError, self).__init__()
        self.value = value

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return self.value


class Process(xworkflows.WorkflowEnabled):
    """
    The workflow process that manages the transistions on step by step basis,
    associated with the processing a group of torrents for a given state.
    """

    state = Taskflow()

    def __init__(self):
        super(Process, self).__init__()

    @xworkflows.transition()
    def prepare(self, torrents):
        """
        Executes all the torrents ready for processing at prepare phase

        :param list torrents:   group of Torrent to process via Tasks
        :returns:               Torrents successfully processed during
                                prepare phase
        :rtype:                 list
        """
        return self._run(torrents)

    @xworkflows.transition()
    def activate(self, torrents):
        """
        Executes all the torrents ready for processing at activate phase

        :param list torrents:   group of Torrent to process via Tasks
        :returns:               Torrents successfully processed during
                                activate phase
        :rtype:                 list
        """
        return self._run(torrents)

    @xworkflows.transition()
    def complete(self, torrents):
        """
        Executes all the torrents ready for processing at complete phase

        :param list torrents:   group of Torrent to process via Tasks
        :returns:               Torrents successfully processed during
                                complete phase
        :rtype:                 list
        """
        return self._run(torrents)

    def abort(self, torrents):
        """
        handle steps necessary to make cancel transistion;
        typically called from retry logic

        :param list torrents:   group of Torrent to update as cancelled
        """
        log.trace('current state [%s]', self.state.name)
        self.cancel()
        log.trace('updated state [%s]', self.state.name)
        datamanager.update_state(torrents, self.state.name)

    def get_transistion_method(self):
        """
        figure out which method needs to be executed next based on current
        state to trigger a transistion in the workflow.

        :returns:   workflow transistion method (prepare, activate,
                    complete, abort)
        :rtype:     method reference
        """

        # we only need first one since it is a 1:1 mapping of state
        # to transition; therefore no need to go beyond first entry
        phase = processmap.get_phase(self.state)
        log.trace('processing phase [%s] for current state %s',
                  phase, self.state.name)

        method_name = self._get_next_step_func(phase)
        log.trace('phase method name %s', method_name)
        tran_method = getattr(self, method_name)
        log.trace('phase method %s', tran_method)

        # make sure it is really callable
        if not callable(tran_method):
            log.error('method=[%s] is not callable; stopping workflow',
                      method_name)
            raise ProcessError('no steps to execute %s of process' % phase)

        return tran_method

    def _get_next_step_func(self, tran_name):
        """
        get the function we need to execute to perform transition
        if you do not name your transition methods after the name of the
        transitions then you need to find out which function maps to
        which transition. All of this information is stored within the
        workflow library xworkflows based on what we defined previously.
        I'd rather not depend on the internals especially names of things
        but it is what it is and I like automation!
        """
        imp_dict = self._xworkflows_implems.get('state')

        return imp_dict.transitions_at.get(tran_name)

    def _run(self, torrents):
        """
        run the actual task for phase based on state
        """
        processed_torrents = []
        # we will only reach this point if called for purposes of advancing to
        # next state so simply return empty.
        if not torrents:
            log.info('Advancing state [%s]', self.state.name)
            # torrents is already empty but since we expect a list back
            # we will return a true empty list since torrents could have
            # been None or something else
            return processed_torrents

        phase_tasks = processmap.get_tasks(self.state.name)
        log.debug('state:phase [%s]:[%s]', self.state.name, phase_tasks.name)

        # we are going to assume that all torrents get processed successfully
        processed_torrents = torrents
        for taskinfo in phase_tasks.tasks:

            log.trace('executing action [%s] for task [%s]',
                      taskinfo.action, taskinfo.task)
            # by passing in the processed_torrents for to a task
            # (initially all of them) we will overwrite the list with a new
            # list of those that did get processed and pass that list to the
            # next task (if any). This means if a torrent fails one task we
            # should stop processing it therefore it will be removed from
            # the list and only those that need further processing
            # will continue.
            processed_torrents = taskinfo.action(processed_torrents)

        # we are only going to return the ones that were succesfully
        # processed such we don't move the state on those that are not
        # ready to move on.
        return processed_torrents
# end Process


def start():
    """
    entry point for module to handle managing the end2end processing
    and tasking
    """
    if cfg.CONF.retry:
        log.info('running in retry mode....no new work will be done')
        # only process those that are in an error state, and have not
        # already gone past our threshold
        _execute(cfg.CONF.disabled_phases, True, cfg.CONF.max_retry)
    else:
        log.debug('running normal mode')
        # time to start processing; first process all new stuff
        _execute(cfg.CONF.disabled_phases)
        log.debug('normal mode completed, now executing retry mode')
        # then process all failed stuff by performing retry
        _execute(cfg.CONF.disabled_phases, True, cfg.CONF.max_retry)


def _execute(disabled_phases, retry=False, max_retry=None):
    """
    the entry point into the taskmanager
    """

    log.trace('disabled phases: %s', disabled_phases)

    for phase in processmap.get_run_phases():

        log.trace('starting execute for phase %s', phase)

        # if there was a request to disable a phase, we simply log some info
        # and continue to the next phase
        if phase in disabled_phases:
            log.info('disabled phase based on configuration (%s)', phase)
            continue

        # convert phase to state, and load corresponding torrents
        # for the specified state. the retry flag will be either True/False
        # if True, load only failed torrents
        # if False, load all non-failed torrents
        state = processmap.get_state(phase)
        log.trace('Loading torrents for state [%s]', state)
        torrents = datamanager.get_torrents_by_state(state, retry)

        if retry:
            log.trace('checking if any torrents need to be cancelled')
            # handle any and all cancellations; we will get back
            # only those torrents that still need processing
            # if nothing, it will be an empty list
            torrents = _handle_torrent_cancellation(torrents, max_retry)

        # if there are no torrents in this particular state then simply
        # proceed to the next phase
        if not torrents:
            log.debug('No torrents found for state [%s]', state)
            continue

        try:
            # now execute the flow for this given state
            processed_torrents = _handle_phase_execution(state, torrents)

            if retry:
                log.trace('torrent retry successful; resetting counters')
                # the processed torrents were the succesful ones so
                # we need to reset the retry counter
                for torrent in processed_torrents:
                    torrent.retry_counter = 0

        except ProcessError as procerr:
            log.error('Process failed! [%s]', procerr)
            break


def _handle_phase_execution(state, torrents):
    """
    Handle the actual execution flow for a given state
    """

    processed_torrents = []
    # establish a process
    process = Process()

    # as long as state != current state of process; we need to perform
    # advancement
    while state != process.state.name:

        log.trace('process step needs to be advanced from %s to %s',
                  process.state.name, state)

        if process.state.is_done or process.state.is_cancelled:
            log.debug('process step (done/cancelled) all execution complete')
            break

        tran_method = process.get_transistion_method()

        # execute the transistion method with no torrents
        # to force the transistion
        tran_method([])

    else:
        tran_method = process.get_transistion_method()

        log.trace('Processing torrents [%d] for state [%s]',
                  len(torrents), state)
        processed_torrents = tran_method(torrents)
        log.trace('Successfully processed torrents [%d] for state [%s]',
                  len(processed_torrents), state)
        datamanager.update_state(processed_torrents, process.state.name)

    # now return the successfully processed torrents so additional
    # processing can take place if needed.
    return processed_torrents


def _handle_torrent_cancellation(torrents, max_retry):
    """
    check for torrents that have reached their max execution threshold and
    perform the abort process on them so we can retire them from future
    execution
    """
    # we will allow users to configure this as per their preferences
    # but the value must be an integer greater than 0; if nothing is
    # provided by user then we default it, or if they provided some stupid
    # value then we override back to default.
    use_max_retry = DEFAULT_MAX_RETRY
    if max_retry is not None and isinstance(max_retry, int) and max_retry > 0:
        log.debug('using configured max retry [%d]', max_retry)
        use_max_retry = max_retry

    log.trace('sorting torrents to abort or continue execution')
    execute_torrents = []
    abort_torrents = []
    for torrent in torrents:
        # has the the torrent reached its max retry limit?
        if torrent.retry_count >= use_max_retry:
            abort_torrents.append(torrent)
            continue

        # not reached limit then we will reset the failed flags
        # so that if it errors again we will have a new error message
        datamanager.reset_failed(torrent)

        # now increment retry counter as we are about to execute!
        torrent.retry_count += 1

        # now add it to the list of those we still need to perform
        # normal processing on.
        execute_torrents.append(torrent)

    # if there were any that we needed to abort this is when we do it
    if abort_torrents:
        log.debug('aborting torrents [%d] that reached their execution limit',
                  len(abort_torrents))
        process = Process()
        try:
            process.abort(abort_torrents)
        except ProcessError as procerr:
            log.error('Abort process failed! [%s]', procerr)

    # now send back those that still need processing
    # (could be just an empty list)
    return execute_torrents
