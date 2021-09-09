# conftest.py
def pytest_html_report_title(report):
    report.title = "Generation Report - UATG"


def pytest_addoption(parser):
    parser.addoption("--dut_config", action="store")

    parser.addoption("--modules_dir", action="store")

    parser.addoption("--jobs", action="store")

    parser.addoption("--output_dir", action="store")

    parser.addoption("--module_dir", action="store")

    parser.addoption("--work_dir", action="store")

    parser.addoption("--linker_dir", action="store")

    parser.addoption("--module", action="store")

    parser.addoption("--gen_cvg", action="store")

    parser.addoption("--alias_file", action="store")
