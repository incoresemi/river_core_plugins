# conftest.py
import pytest
from py.xml import html


def pytest_html_report_title(report):
    report.title = "RISC-V Verification"


def pytest_addoption(parser):
    # parser.addoption(
    #     "--regress_list",
    #     action="store"
    # )
    parser.addoption(
        "--asm_dir",
        action="store"
    )
    # parser.addoption(
    #     "--output_dir",
    #     action="store"
    # )
    parser.addoption(
        "--yaml_config",
        action="store"
    )


# @pytest.mark.optionalhook
# def pytest_html_results_table_header(cells):
#     cells.insert(1, html.th('Fail Reason'))


# @pytest.mark.optionalhook
# def pytest_html_results_table_row(report, cells):
#     cells.insert(1, html.td(report.ticket))


# @pytest.mark.hookwrapper
# def pytest_runtest_makereport(item, call):
#     outcome = yield
#     report = outcome.get_result()
#     report.ticket = 'todo'
