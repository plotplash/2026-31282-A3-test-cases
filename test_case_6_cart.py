import time
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

def setup():
    driver = webdriver.Firefox()
    driver.implicitly_wait(10)
    return driver

def end(driver):
    time.sleep(3)
    driver.quit()

def get_price_float(price_string: str):
    price_string = price_string.replace('$', '').replace(',', '').strip()
    return float(price_string)

def test_1_empty_cart():
    driver = setup()
    driver.get("https://opencart.abstracta.us/")

    # get cart button text
    cart_button = driver.find_element(by=By.ID, value="cart-total")
    cart_text = cart_button.text

    # Verify that the cart button displays that there are 0 items in the cart. 
    displayed_num_items = cart_text.split()[0].strip()
    assert displayed_num_items == '0', "number of items: button displayed != actual"

    # Verify that the cart button displays that the cart total is 0. 
    displayed_cart_total = cart_text.split()[-1].strip()
    assert displayed_cart_total == '$0.00', "cart total: button displayed != actual"

    # click the cart button to display the cart dropdown menu
    cart_button.click()

    # verify that the cart dropdown menu displays the "Your shopping cart is empty!" message
    cart_group = driver.find_element(by=By.ID, value="cart")
    wait = WebDriverWait(driver, 10)
    cart_empty = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "text-center")))
    assert cart_empty.text == "Your shopping cart is empty!", "cart empty text does not appear" 

    end(driver)

def test_2_add_to_cart():
    driver = setup()
    driver.get("https://opencart.abstracta.us/")

    num_cart_items = 0
    cart_total = 0

    # find the first product on the page
    product = driver.find_element(by=By.CLASS_NAME, value="product-layout")

    # record the product's name
    product_name = product.find_element(by=By.TAG_NAME, value="h4").text

    # record the product's price without currency symbols
    price_detailed = product.find_element(by=By.CLASS_NAME, value="price").text
    price = get_price_float(price_detailed.split()[0])

    # find the first product's "ADD TO CART" button and click it
    add_button = product.find_element(by=By.CLASS_NAME, value="fa-shopping-cart")
    add_button.click()
    num_cart_items += 1
    cart_total += price

    # wait for changes to be updated
    time.sleep(3)

    # get cart button text
    cart_button = driver.find_element(by=By.ID, value="cart-total")
    cart_text = cart_button.text

    # Verify that the cart button now displays the correct number of items. 
    displayed_num_items = cart_text.split()[0]
    assert int(displayed_num_items) == num_cart_items, "number of items: button displayed != actual"

    # Verify that the cart button displays the correct total cost. 
    displayed_cart_total = get_price_float(cart_text.split()[-1])
    assert cart_total == displayed_cart_total, "cart total: button displayed != actual"

    # click the cart button to display the cart dropdown menu
    cart_button.click()

    # verify that the cart only contains one type of item (only has 1 row of items)
    cart_group = driver.find_element(by=By.ID, value="cart")
    cart_items_table = cart_group.find_element(by=By.CLASS_NAME, value="table-striped")
    cart_item_rows = cart_items_table.find_elements(by=By.TAG_NAME, value="tr")
    assert len(cart_item_rows) == 1, "cart does not contain exactly one type of item"

    # verify that the cart only contains the product added (MacBook)
    item = cart_item_rows[0]
    item_sections = item.find_elements(by=By.TAG_NAME, value="td")
    item_name = item_sections[1].text
    assert item_name == product_name, "first item in cart does not match product added"
    
    # verify that the cart dropdown menu displays the correct amount of the product (1)
    amount_string = item_sections[2].text
    amount = int(amount_string.split()[1])
    assert amount == num_cart_items, "amount: menu displayed != actual"

    # verify that the product total for the item is correct ($602.00)
    product_total_string = item_sections[3].text.strip()
    product_total = get_price_float(product_total_string)
    assert product_total == price * amount, "product total: displayed != actual"

    # verify that the cart dropdown menu displays the correct cart total
    cart_total_breakdown = cart_group.find_element(by=By.CLASS_NAME, value="table-bordered")
    cart_total_breakdown_rows = cart_total_breakdown.find_elements(by=By.TAG_NAME, value="tr")
    cart_total_row = cart_total_breakdown_rows[-1].find_elements(by=By.TAG_NAME, value="td")
    cart_menu_total = get_price_float(cart_total_row[-1].text)
    assert cart_menu_total == cart_total, "cart total: menu displayed != actual"
    
    # verify that the product total is the same as the cart total since there is only one type of item
    assert product_total == cart_total, "cart total: product total != actual"

    end(driver)

def test_3_remove_from_cart():
    driver = setup()
    driver.get("https://opencart.abstracta.us/")

    # find the first product on the page
    product = driver.find_element(by=By.CLASS_NAME, value="product-layout")

    # record the product's name
    product_name = product.find_element(by=By.TAG_NAME, value="h4").text

    # record the product's price without currency symbols and commas
    price_detailed = product.find_element(by=By.CLASS_NAME, value="price").text
    price = get_price_float(price_detailed.split()[0])

    # find the first product's "ADD TO CART" button and click it
    add_button = product.find_element(by=By.CLASS_NAME, value="fa-shopping-cart")
    add_button.click()

    # wait for changes to be saved
    time.sleep(3)

    # find the cart button
    cart_button = driver.find_element(by=By.ID, value="cart-total")

    # click cart button to display the cart dropdown menu
    cart_button.click()

    # find the remove button for the item and click it
    cart_group = driver.find_element(by=By.ID, value="cart")
    remove_button = cart_group.find_element(by=By.CLASS_NAME, value="btn-danger")
    remove_button.click()

    # wait for changes to be saved
    time.sleep(3)

    # Verify that the cart button displays that there are 0 items in the cart. 
    cart_button = driver.find_element(by=By.ID, value="cart-total")
    cart_text = cart_button.text
    displayed_num_items = cart_text.split()[0]
    assert int(displayed_num_items) == 0, "number of items: button displayed != actual"

    # Verify that the cart button displays that the cart total is 0. 
    displayed_cart_total = float(cart_text.split()[-1][1:])
    assert displayed_cart_total == 0, "cart total: button displayed != actual"

    # click the cart button to display the cart dropdown menu
    cart_button.click()

    # verify that the cart dropdown menu displays the "Your shopping cart is empty!" message
    cart_group = driver.find_element(by=By.ID, value="cart")
    cart_empty = cart_group.find_element(by=By.CLASS_NAME, value="text-center")
    assert cart_empty.text == "Your shopping cart is empty!", "cart empty message does not appear"

    end(driver)

if __name__ == "__main__":
    retcode = pytest.main(["test_case_6_cart.py","-v"])
