# conftest.py
import pytest
import inspect
from py.xml import html


def pytest_html_report_title(report):
    report.title = "Compilation Report"


def pytest_addoption(parser):
    # parser.addoption(
    #     "--regress_list",
    #     action="store"
    # )
    parser.addoption("--make_file", action="store")
    parser.addoption("--asm_dir", action="store")
    # parser.addoption(
    #     "--output_dir",
    #     action="store"
    # )
    # parser.addoption(
    #     "--gen_suite",
    #     action="store"
    # )


# Possible chance of adding stages here
# i.e. a new column for getting the stage,
# Need to figure out a way to get the 2nd argument passed to item.function


@pytest.mark.optionalhook
def pytest_html_results_table_header(cells):
    cells.insert(1, html.th('Stage'))

@pytest.mark.optionalhook
def pytest_html_results_table_row(report, cells):
    cells.insert(1, html.td(report.ticket))

@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.ticket = str(item.funcargs['test_input'][-1])
