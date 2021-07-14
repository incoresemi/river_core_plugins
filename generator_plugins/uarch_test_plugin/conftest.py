# conftest.py
def pytest_html_report_title(report):
    report.title = "Generation Report - uarch_test"


def pytest_addoption(parser):
    parser.addoption("--configfile", action="store")

    parser.addoption("--jobs", action="store")

    parser.addoption("--output_dir", action="store")

    parser.addoption("--module_dir", action="store")

    parser.addoption("--test_dir", action="store")
