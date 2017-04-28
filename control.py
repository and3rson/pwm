import subprocess
import os
import sys
import traceback
import log


class Control(object):
    def __init__(self, wm):
        self._wm = wm

    def debug(self, wm, cbkey):
        log.debug('Pages: %s', self._wm.get_pages())
        log.debug('Windows: %s', self._wm.windows)

    def next_window(self, wm, cbkey):
        windows = self._wm.get_current_page().get_windows()
        current_index = windows.index(self._wm.get_current_page().get_current_window())
        if current_index == -1:
            log.debug('No windows on this page')
            return
        next_index = (current_index + 1) % len(windows)
        if next_index == current_index:
            log.debug('Only one window on this page')
            return
        log.debug('Switching window %s -> %s', windows[current_index], windows[next_index])
        self._wm.get_current_page().focus_window(windows[next_index])

    def prev_window(self, wm, cbkey):
        windows = self._wm.get_current_page().get_windows()
        current_index = windows.index(self._wm.get_current_page().get_current_window())
        if current_index == -1:
            log.debug('No windows on this page')
            return
        next_index = (current_index - 1)
        if next_index < 0:
            next_index = len(windows) - 1
        if next_index == current_index:
            log.debug('Only one window on this page')
            return
        log.debug('Switching window %s -> %s', windows[current_index], windows[next_index])
        self._wm.get_current_page().focus_window(windows[next_index])

    def next_page(self, wm, cbkey):
        current_index = self._wm.get_pages().index(self._wm.get_current_page())
        next_index = (current_index + 1) % len(self._wm.get_pages())
        self._wm.switch_page(self._wm.get_pages()[next_index])

    def prev_page(self, wm, cbkey):
        current_index = self._wm.get_pages().index(self._wm.get_current_page())
        prev_index = (current_index - 1)
        if prev_index < 0:
            prev_index = len(self._wm.get_pages()) - 1
        self._wm.switch_page(self._wm.get_pages()[prev_index])

    def select_page(self, num):
        def cb(wm, cbkey):
            if num - 1 < len(self._wm.get_pages()):
                self._wm.switch_page(self._wm.get_pages()[num - 1])
        return cb

    def select_window(self, num):
        def cb(wm, cbkey):
            if num - 1 < len(self._wm.get_current_page().get_windows()):
                self._wm.get_current_page().focus_window(self._wm.get_current_page().get_windows()[num - 1])
        return cb

    def spawn(self, *args):
        def cb(wm, cbkey):
            self.system(args)
            # print('Spawning', args)
            # ps = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # o, e = ps.communicate()
            # print(ps.returncode, o, e)
        return cb

    def system(self, command):
        '''
        Forks a command and disowns it.
        '''
        if os.fork() != 0:
            return

        try:
            # Child.
            os.setsid()     # Become session leader.
            if os.fork() != 0:
                os._exit(0)

            # os.chdir(os.path.expanduser('~'))
            os.umask(0)

            # Close all file descriptors.
            # import resource
            # maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
            # if maxfd == resource.RLIM_INFINITY:
            #     maxfd = 1024
            # for fd in range(maxfd):
            #     try:
            #         os.close(fd)
            #     except OSError:
            #         pass
            # print('FOO')

            # Open /dev/null for stdin, stdout, stderr.
            os.open('/dev/null', os.O_RDWR)
            os.dup2(0, 1)
            os.dup2(0, 2)

            os.execve(command[0], command, os.environ)
        except Exception:
            try:
                # Error in child process.
                log.exception('Error in child process')
            except Exception:
                log.error('Error in error handler :/')
            sys.exit(1)
