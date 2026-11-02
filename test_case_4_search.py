import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

def setup():
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    return driver

def end(driver):
    time.sleep(3)
    driver.quit()


def test_1_key_word_search():
    driver = setup()
    driver.get("https://opencart.abstracta.us/")

    # locate the search bar
    top_search = driver.find_element(by=By.ID, value="search")

    # locate and input search value into search bar
    search_value = "mac"
    top_search_input = top_search.find_element(by=By.CLASS_NAME, value="input-lg")
    top_search_input.send_keys(search_value)
    search_value = search_value.lower()

    # locate and click search button
    top_search_button = top_search.find_element(by=By.CLASS_NAME, value="input-group-btn")
    top_search_button.click()

    # locate all products on the page
    products = driver.find_elements(by=By.CLASS_NAME, value="product-layout")

    # check all products contain search keyword in their name, ignoring capitalisation
    for p in products:
        name = p.find_element(by=By.TAG_NAME, value="h4").text
        assert search_value in name.lower(), f"{name} does not contain keyword {search_value}"

    end(driver)

def test_2_key_word_description_search():
    driver = setup()
    driver.get("https://opencart.abstracta.us/")

    # locate the search bar
    top_search = driver.find_element(by=By.ID, value="search")

    # locate and input search value into search bar
    search_value = "mac"
    top_search_input = top_search.find_element(by=By.CLASS_NAME, value="input-lg")
    top_search_input.send_keys(search_value)
    search_value = search_value.lower()

    # locate and click search button
    top_search_button = top_search.find_element(by=By.CLASS_NAME, value="input-group-btn")
    top_search_button.click()

    # find and select the "Search in product descriptions" option
    description_search = driver.find_element(by=By.ID, value="description")
    description_search.click()

    # find and click the blue search button
    search_button = driver.find_element(by=By.ID, value="button-search")
    search_button.click()

    # locate all products on the page
    products = driver.find_elements(by=By.CLASS_NAME, value="product-layout")

    # check all products contain search keyword in their name or product 
    # description, ignoring capitalisation
    for i in range(0, len(products)):
        name = products[i].find_element(by=By.TAG_NAME, value="a")
        name_text = name.text.lower()
        try:
            assert search_value in name_text
        except AssertionError:
            name.click()
            product_description = driver.find_element(by=By.ID, value="tab-description").text.lower()
            assert search_value in product_description, f"{name} does not contain keyword {search_value} in its name nor its product description"
            driver.back()
            products = driver.find_elements(by=By.CLASS_NAME, value="product-layout")

    end(driver)

def test_3_category_search():
    driver = setup()
    driver.get("https://opencart.abstracta.us/")

    search_value = " "

    # locate the search bar
    top_search = driver.find_element(by=By.ID, value="search")

    # locate and input search value into search bar input
    top_search_input = top_search.find_element(by=By.CLASS_NAME, value="input-lg")
    top_search_input.send_keys(search_value)

    # locate and click search button
    top_search_button = top_search.find_element(by=By.CLASS_NAME, value="input-group-btn")
    top_search_button.click()

    # locate the "Categories" dropdown and select "Desktops"
    category = "Desktops"
    categories = Select(driver.find_element(by=By.NAME, value="category_id"))
    categories.select_by_visible_text(category)

    # locate and click blue search button
    search_button = driver.find_element(by=By.ID, value="button-search")
    search_button.click()

    # store the resulting products
    result_products = []
    for p in driver.find_elements(by=By.CLASS_NAME, value="product-layout"):
        result_products.append(p.text)

    # navigate to the "Desktops" page
    driver.get("http://opencart.abstracta.us/index.php?route=product/category&path=20")

    # list the products in the category
    category_products = []
    for p in driver.find_elements(by=By.CLASS_NAME, value="product-layout"):
        category_products.append(p.text)

    # verify that all the result products are in the "Desktops" category
    for p in result_products:
        name = p.split('\n')[0].strip()
        assert p in category_products, f"{name} does not appear in the Desktops category"

    end(driver)


if __name__ == "__main__":
    retcode = pytest.main(["test_case_4_search.py", "-v"])
