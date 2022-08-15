from dash.testing.application_runners import import_app
import dash
from dash import html

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from dashUI.index import title_header
from dashUI import params


def test_home(dash_duo):
    app = import_app("dashUI.app")
    dash_duo.start_server(app)
    wait = WebDriverWait(dash_duo.driver, 10)

    navbar_elem = dash_duo.find_element("#navbar")

    # check title
    assert navbar_elem.text == title_header

    # check help link
    helplink = navbar_elem.find_element(By.CSS_SELECTOR,'#helplink_image')

    #check if image is loaded properly
    help_imlink = helplink.get_attribute('src')
    response = requests.get(help_imlink, stream=True)

    assert response.status_code == 200

    #check if help redirect works

    # Store the ID of the original window
    original_window = dash_duo.driver.current_window_handle

    # Check we don't have other windows open already
    assert len(dash_duo.driver.window_handles) == 1

    # click the link to open the help page
    helplink.click()

    # Wait for the new window or tab
    wait.until(EC.number_of_windows_to_be(2))

    for window_handle in dash_duo.driver.window_handles:
        if window_handle != original_window:
            dash_duo.driver.switch_to.window(window_handle)

            assert dash_duo.driver.current_url == params.doc_url
            response = requests.get(dash_duo.driver.current_url)

            assert response.status_code == 200

            dash_duo.driver.close()
            dash_duo.driver.switch_to.window(original_window)
