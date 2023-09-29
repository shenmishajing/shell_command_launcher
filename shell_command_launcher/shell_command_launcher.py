import os
import subprocess
import time
from collections import deque
from string import Template
from typing import Union

from jsonargparse import CLI


def iter_arg_dict(arg_dict, keys=None, cur_arg_dict=None):
    if keys is None:
        keys = list(arg_dict.keys())

    if cur_arg_dict is None:
        cur_arg_dict = {}

    if len(keys) == 0:
        yield cur_arg_dict
    else:
        key = keys[0]
        for arg_value in arg_dict[key]:
            cur_arg_dict[key] = arg_value
            yield from iter_arg_dict(arg_dict, keys[1:], cur_arg_dict)
            cur_arg_dict.pop(key)


def single_command_launcher(
    command: str, log_dir: str = None, num: int = 1, sleep_time: float = 0, tasks=None
):
    if log_dir is not None:
        if num == 1:
            name = os.path.basename(log_dir)
            log_dir = os.path.dirname(log_dir)
        os.makedirs(log_dir, exist_ok=True)

    for num_ind in range(num):
        print(f"running command: {command}, num: {num_ind+1}/{num}")

        if num > 1:
            name = num_ind

        if log_dir is not None:
            stdout = open(os.path.join(log_dir, f"{name}.log"), "w")
        elif tasks.maxlen > 1:
            stdout = subprocess.DEVNULL
        else:
            stdout = None

        tasks.append(
            subprocess.Popen(
                command, stdout=stdout, stderr=subprocess.STDOUT, shell=True
            )
        )

        if len(tasks) == tasks.maxlen:
            tasks.popleft().wait()

        if sleep_time:
            time.sleep(sleep_time)


def shell_command_launcher(
    command: str,
    arg_dict: dict[str, Union[list, str]] = None,
    log_dir: str = None,
    num: int = 1,
    parallel_num: int = 1,
    sleep_time: float = 0,
):
    parallel_num = max(1, parallel_num)
    tasks = deque(maxlen=parallel_num)

    try:
        if arg_dict is not None:
            for arg in arg_dict:
                if isinstance(arg_dict[arg], str):
                    arg_dict[arg] = arg_dict[arg].split(",")

            for args in iter_arg_dict(arg_dict):
                cur_command = Template(command).substitute(args)
                if log_dir is not None:
                    keys = sorted(args.keys())
                    name = "__".join([f"{key}_{args[key]}" for key in keys])
                    cur_log_dir = os.path.join(log_dir, name)
                else:
                    cur_log_dir = None
                single_command_launcher(
                    cur_command, cur_log_dir, num, sleep_time, tasks=tasks
                )
        else:
            single_command_launcher(command, log_dir, num, sleep_time, tasks=tasks)
    except KeyboardInterrupt:
        try:
            print(
                "detect Ctrl-C pressed, try to terminate all tasks gracefully, press Ctrl-C again to force kill all tasks"
            )
            for t in tasks:
                t.terminate()
        except KeyboardInterrupt:
            print("force kill all tasks")
            for t in tasks:
                t.kill()
    else:
        for t in tasks:
            t.wait()


def main():
    CLI(shell_command_launcher)


if __name__ == "__main__":
    main()
