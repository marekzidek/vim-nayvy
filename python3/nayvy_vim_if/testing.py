import sys
from typing import List

import vim  # noqa

from nayvy.testing.autogen import AutoGenerator
from nayvy.projects.modules.loader import SyntacticModuleLoader


def nayvy_auto_touch_test(filepath: str) -> None:
    """ Vim interface for touch unittest script.
    """
    auto_generator = AutoGenerator(SyntacticModuleLoader())
    test_path = auto_generator.touch_test_file(filepath)
    if test_path is None:
        print(
            'Please check if your python project is created correcty',
            file=sys.stderr,
        )
        return
    vim.command(f'vs {test_path}')
    return


def nayvy_jump_to_test_or_generate(
    filepath: str,
    func_name: str,
) -> None:
    """ Vim interface for jump of generate unittest.
    """
    auto_generator = AutoGenerator(SyntacticModuleLoader())
    test_path = auto_generator.touch_test_file(filepath)
    if test_path is None:
        print(
            'Please check if your python project is created correcty',
            file=sys.stderr,
        )
        return

    with open(filepath) as f:
        impl_module_lines = [
            line.strip('\n') for line in f.readlines()
        ]

    with open(test_path) as f:
        test_module_lines = [
            line.strip('\n') for line in f.readlines()
        ]

    lines = auto_generator.get_added_test_lines(
        func_name,
        impl_module_lines,
        test_module_lines,
    )

    # open test in split buffer
    vim.command(f'vs {test_path}')

    if lines is None:
        return None

    # change lines
    vim.current.buffer[:] = lines

    # search lines
    row: int
    column: int
    for i, line in enumerate(lines):
        needle = f'def test_{func_name}'
        if needle in line:
            vim.current.window.cursor = (
                i + 1,
                line.index(needle),
            )
    return


def nayvy_list_untested_functions() -> List[str]:
    """ Vim interface for implementing not-tested functions
    """
    filepath = vim.eval('expand("%")')
    lines = vim.current.buffer[:]
    loader = SyntacticModuleLoader()
    auto_generator = AutoGenerator(loader)
    test_path = auto_generator.touch_test_file(filepath)
    if test_path is None:
        print(
            'Please check if your python project is created correcty',
            file=sys.stderr,
        )
        return []

    impl_mod = loader.load_module_from_lines(lines)
    test_mod = loader.load_module_from_path(test_path)
    if impl_mod is None or test_mod is None:
        print(
            'Loading python scripts failed.',
            file=sys.stderr,
        )
        return []
    subtraction = impl_mod.to_test().sub(test_mod)
    return subtraction.to_func_list_lines()