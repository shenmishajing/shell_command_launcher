import pytest

from shell_command_launcher.shell_command_launcher import iter_arg_dict


@pytest.mark.parametrize(
    "arg_dict, expected_result",
    [
        ({}, [{}]),
        ({"arg1": [1]}, [{"arg1": 1}]),
        ({"arg1": [1, 2]}, [{"arg1": 1}, {"arg1": 2}]),
        (
            {"arg1": [1, 2], "arg2": [3, 4]},
            [
                {"arg1": 1, "arg2": 3},
                {"arg1": 1, "arg2": 4},
                {"arg1": 2, "arg2": 3},
                {"arg1": 2, "arg2": 4},
            ],
        ),
        (
            {"arg1": [1, 2], "arg2": [3, 4], "arg3": [5, 6]},
            [
                {"arg1": 1, "arg2": 3, "arg3": 5},
                {"arg1": 1, "arg2": 3, "arg3": 6},
                {"arg1": 1, "arg2": 4, "arg3": 5},
                {"arg1": 1, "arg2": 4, "arg3": 6},
                {"arg1": 2, "arg2": 3, "arg3": 5},
                {"arg1": 2, "arg2": 3, "arg3": 6},
                {"arg1": 2, "arg2": 4, "arg3": 5},
                {"arg1": 2, "arg2": 4, "arg3": 6},
            ],
        ),
    ],
)
def test_iter_arg_dict(arg_dict, expected_result):
    for result, expected_result in zip(iter_arg_dict(arg_dict), expected_result):
        assert result == expected_result
