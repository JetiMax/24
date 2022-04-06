import warnings
import unicodedata
import pytest
import uuid
from selenium import webdriver
driver = webdriver.Chrome()
pytestmark = pytest.mark.filterwarnings("error")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    # This function helps to detect that some test failed
    # and pass this information to teardown:

    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep


@pytest.fixture
def web_browser(request, selenium):

    browser = selenium
    browser.set_window_size(1400, 1000)

    # Return browser instance to test case:
    yield browser

    # Do teardown (this code will be executed after each test):

    if request.node.rep_call.failed:
        # Make the screen-shot if test failed:
        try:
            browser.execute_script("document.body.bgColor = 'white';")

            # Make screen-shot for local debug:
            browser.save_screenshot('screenshots/' + str(uuid.uuid4()) + '.png')

            # For happy debugging:
            print('URL: ', browser.current_url)
            print('Browser logs:')
            for log in browser.get_log('browser'):
                print(log, "utf8")
        except:
            pass  # just ignore any errors here


def get_test_case_docstring(item):
    """ This function gets doc string from test case and format it
        to show this docstring instead of the test case name in reports.
    """

    full_name = ''

    if item._obj.__doc__:
        # Remove extra whitespaces from the doc string:
        name = str(item._obj.__doc__.split('.')[0]).strip()
        full_name = ' '.join(name.split())

        # Generate the list of parameters for parametrized test cases:
        if hasattr(item, 'callspec'):
            params = item.callspec.params

            res_keys = sorted([k for k in params])
            # Create List based on Dict:
            res = ['{0}_"{1}"'.format(k, params[k]) for k in res_keys]
            # Add dict with all parameters to the name of test case:
            full_name += ' Parameters ' + str(', '.join(res))
            full_name = full_name.replace(':', '')

    return full_name


def pytest_itemcollected(item):
    """ This function modifies names of test cases "on the fly"
        during the execution of test cases.
    """

    if item._obj.__doc__:
        item._nodeid = get_test_case_docstring(item)


def pytest_collection_finish(session):
    """ This function modified names of test cases "on the fly"
        when we are using --collect-only parameter for pytest
        (to get the full list of all existing test cases).
    """

    if session.config.option.collectonly is True:
        for item in session.items:
            # If test case has a doc string we need to modify it's name to
            # it's doc string to show human-readable reports and to
            # automatically import test cases to test management system.
            if item._obj.__doc__:
                full_name = get_test_case_docstring(item)
                print(full_name)

        pytest.exit('Done!')


@pytest.fixture(autouse=True)
def testind():
    pytest.driver = webdriver.Chrome('chrome/chromedriver.exe')
    pytest.driver.get('http://petfriends1.herokuapp.com/login')
    yield
    pytest.driver.quit()


def test_my_pets():
    pytest.driver.find_element_by_id('email').send_keys('jetimax@yandex.ru')
    pytest.driver.find_element_by_id('pass').send_keys('1725maksim')
    pytest.driver.find_element_by_css_selector('button[type="submit"]').click()
    assert pytest.driver.find_element_by_tag_name('h1').text == "PetFriends"

    images = pytest.driver.find_element_by_css_selector('.card-deck.card-img-top')
    names = pytest.driver.find_element_by_css_selector('.card-deck.card-title>baks</h5>')
    description = pytest.driver.find_element_by_css_selector('.card-deck.card-text')

    for i in range(len(names)):
        assert images[i].get_atribute('src') != ''
        assert names[i].text != ''
        assert description[i].text != ''
        assert ', ' in description[i]
        parts = description[i].text.split(", ")
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0


def api_v1():
    warnings.warn(DeprecationWarning("DeprecationWarning"))
    return 1


@pytest.mark.filterwarnings("DeprecationWarning")
def test_one():
    assert api_v1() == 1
