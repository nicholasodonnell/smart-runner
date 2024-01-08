import threading
from subprocess import Popen, PIPE


class Command:
    def __init__(self, cmd, stdout=lambda x: None, stderr=lambda x: None):
        self.cmd = cmd
        self.stdout = stdout
        self.stderr = stderr

    def __streamOutput__(self, stream, callback):
        while True:
            line = stream.readline()
            if line:
                callback(line.strip())
            else:
                break

    def exec(self):
        try:
            # Start the subprocess
            process = Popen(
                self.cmd, stdout=PIPE, stderr=PIPE, shell=True, text=True, bufsize=1
            )

            # Create and start threads to read stdout and stderr
            stdout_thread = threading.Thread(
                target=self.__streamOutput__, args=(process.stdout, self.stdout)
            )
            stderr_thread = threading.Thread(
                target=self.__streamOutput__, args=(process.stderr, self.stderr)
            )

            stdout_thread.start()
            stderr_thread.start()

            # Wait for the threads to finish
            stdout_thread.join()
            stderr_thread.join()

            # Wait for the subprocess to finish
            process.wait()

            # Return the exit code
            return process.returncode
        except Exception as e:
            raise Exception('Failed to run command "{}": {}'.format(self.cmd, e))
