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

def login(driver):
    # input login details
    email_input = driver.find_element(by=By.ID, value="input-email")
    email_input.send_keys("mash.potato@gmail.com")
    password_input = driver.find_element(by=By.ID, value="input-password")
    password_input.send_keys("MashedPotato")

    # click login button
    content = driver.find_element(by=By.ID, value="content")
    login_form = content.find_element(by=By.TAG_NAME, value="form")
    login_button = login_form.find_element(by=By.CLASS_NAME, value="btn")
    login_button.click()

def get_price_float(price_string: str):
    price_string = price_string.replace('$', '').replace(',', '').strip()
    return float(price_string)


def test_1_access_order_history():
    driver = setup()
    driver.get("https://opencart.abstracta.us/index.php?route=account/login")

    # click "Order History" button in the right column of the account page
    right_column = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "column-right")))
    order_history_button = right_column.find_element(by=By.LINK_TEXT, value="Order History")
    order_history_button.click()

    # verify that the current page is still the "Account Login" page
    assert driver.title == "Account Login", "driver not on Account Login page"
    
    # input login details
    email_input = driver.find_element(by=By.ID, value="input-email")
    email_input.send_keys("mash.potato@gmail.com")
    password_input = driver.find_element(by=By.ID, value="input-password")
    password_input.send_keys("MashedPotato")

    # click login button
    content = driver.find_element(by=By.ID, value="content")
    login_form = content.find_element(by=By.TAG_NAME, value="form")
    login_button = login_form.find_element(by=By.CLASS_NAME, value="btn")
    login_button.click()

    # click "Order History" button in the right column of the account page
    right_column = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "column-right")))
    order_history_button = right_column.find_element(by=By.LINK_TEXT, value="Order History")
    order_history_button.click()

    # verify that the current page is the "Order History" page
    assert "Order History" in driver.title, "driver not on Order History page"

    end(driver)


def test_2_view_order_details():
    driver = setup()
    driver.get("https://opencart.abstracta.us/index.php?route=account/login")

    login(driver)

    # click "Order History" button in the right column of the account page
    right_column = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "column-right")))
    order_history_button = right_column.find_element(by=By.LINK_TEXT, value="Order History")
    order_history_button.click()

    # locate the first order row
    content = driver.find_element(by=By.ID, value="content")
    table_body = content.find_element(by=By.TAG_NAME, value="tbody")
    order = table_body.find_element(by=By.TAG_NAME, value="tr")
    order_info_row = order.find_elements(by=By.TAG_NAME, value="td")

    # record the order information on the overview
    table_header = driver.find_element(by=By.TAG_NAME, value="thead")
    table_headings = table_header.find_elements(by=By.TAG_NAME, value="td")

    # create a dictionary to store the information for easier access
    order_info_dict = {str: str}
    for i in range(len(table_headings)-1): # stop before recording the button information
        heading = table_headings[i].text
        order_info_dict[heading] = order_info_row[i].text.strip()

    """ the information stored:
                │Order ID   │Customer   │No. of Products    │Status     │Total      │Date Added
        ────────┼───────────┼───────────┼───────────────────┼───────────┼───────────┼───────────
        index 0 │#32958     │Potato Mash│6                  │Pending    │$933.19    │28/10/2026
    """

    # click the "View" button to go to the Order Information page for that order
    view_order_button = order_info_row[-1].find_element(by=By.CLASS_NAME, value="btn")
    view_order_button.click()

    # verify that the current page is the "Order Information" page
    assert driver.title == "Order Information", "driver not on Order Information page"

    # locate the content of the page and the tables on it
    content = driver.find_element(by=By.ID, value="content")
    tables = content.find_elements(by=By.TAG_NAME, value="table")

    # locating the first column of the "Order Details" table for Order ID and Date Added information
    order_details_table = tables[0]
    order_details_body = order_details_table.find_element(by=By.TAG_NAME, value="tbody")
    order_details_c1_text = order_details_body.find_elements(by=By.TAG_NAME, value="td")[0].text
    order_details_c1_rows = order_details_c1_text.split('\n')

    # verify the order id matches the one from before
    order_id_info = order_details_c1_rows[0].split(':')
    order_id_value = order_id_info[-1].strip()
    assert order_info_dict.get("Order ID") == order_id_value, "Order ID does not match"
    assert order_info_dict.get("Order ID") in order_id_value, "Order ID does not match"

    # verify the date added matches the one from before
    date_added_info = order_details_c1_rows[1].split(':')
    date_added_value = date_added_info[-1].strip()
    assert order_info_dict.get("Date Added") == date_added_value, "Date Added does not match"

    # locating the rows of products for no. of products and total information
    products_table = tables[2]
    products_table_body = products_table.find_element(by=By.TAG_NAME, value="tbody")
    product_rows = products_table_body.find_elements(by=By.TAG_NAME, value="tr")

    # loop through each row of the table
    displayed_num_products = 0
    calculated_total = 0
    for product in product_rows:
        product_info = product.find_elements(by=By.TAG_NAME, value="td")

        # find product name
        product_name = product_info[0].text.replace('\n', '').strip()

        # add the product's quantity to the displayed_num_products variable
        product_quantity = int(product_info[2].text)
        displayed_num_products += product_quantity

        # find price
        product_price = get_price_float(product_info[3].text)

        # add total for that product to the calculated_total variable
        product_total = get_price_float(product_info[4].text)
        calculated_total += product_total
        
        # verify that the total for that product is correct
        assert product_quantity * product_price == product_total, f"total for {product_name} not correct"

    # verify that the quantity is correct
    assert order_info_dict.get("No. of Products") == str(displayed_num_products), "number of products: Order Information page != Order History page"

    # verify that the calculated total (with flat shipping fee of $8 added) is correct
    calculated_total += 8
    assert order_info_dict.get("Total") == '$' + str(calculated_total), "total: Order Information calculated total != Order History page"

    # locate the cost components
    total_breakdown = products_table.find_element(by=By.TAG_NAME, value="tfoot")
    cost_component_rows = total_breakdown.find_elements(by=By.TAG_NAME, value="tr")

    cost_component_sum = 0.0
    for i in range(0, len(cost_component_rows)-1): # do not add the last row (total row)
        # locate each cell in the row
        cells = cost_component_rows[i].find_elements(by=By.TAG_NAME, value="td")
        cost_component_cell = cells[2]

        # find the cost component and add it to the cost_component_sum
        cost_component = get_price_float(cost_component_cell.text)
        cost_component_sum += cost_component

    # find displayed total
    total_row = cost_component_rows[-1].find_elements(by=By.TAG_NAME, value="td")
    displayed_total = get_price_float(total_row[2].text)

    # verify that the sum of the cost components equals the displayed total
    assert cost_component_sum == displayed_total, "total: cost components sum != displayed total"

    # verify that the displayed total is the same as the total from the Order History page
    saved_total = get_price_float(order_info_dict.get("Total"))
    assert saved_total == displayed_total, "total: Order Information displayed != Order History page"

    # verify that the name displayed is the same as the account's
    assert order_info_dict.get("Customer").strip() == "Potato Mash", "customer: Order Information displayed != Order History page"

    end(driver)


def test_3_reorder():
    driver = setup()
    driver.get("https://opencart.abstracta.us/index.php?route=account/login")

    login(driver)

    # find the cart button
    cart_button = driver.find_element(by=By.ID, value="cart-total")

    # click cart button to display the cart dropdown menu
    cart_button.click()

    # find the remove button for the first item and click it
    cart_group = driver.find_element(by=By.ID, value="cart")
    cart_items_table = cart_group.find_element(by=By.CLASS_NAME, value="table-striped")
    cart_item_rows = cart_items_table.find_elements(by=By.TAG_NAME, value="tr")
    remove_button = cart_items_table.find_element(by=By.CLASS_NAME, value="btn-danger")
    remove_button.click()

    # wait for changes to be saved
    time.sleep(3)

    # keep removing items until none are left
    for i in range(0, len(cart_item_rows)-1):
        # find the cart button
        cart_button = driver.find_element(by=By.ID, value="cart-total")
        cart_text = cart_button.text

        displayed_num_items = int(cart_text.split()[0].strip())
        if displayed_num_items == 0:
            break

        # click cart button to display the cart dropdown menu
        cart_button.click()

        # find the remove button for the first item in the cart and click it
        remove_button = cart_items_table.find_element(by=By.CLASS_NAME, value="btn-danger")
        remove_button.click()

        # Verify that the cart button now displays the correct number of items. 
        # wait for changes to be saved
        time.sleep(3)


    # click "Order History" button in the right column of the account page
    right_column = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "column-right")))
    order_history_button = right_column.find_element(by=By.LINK_TEXT, value="Order History")
    order_history_button.click()

    # locate the first order row
    content = driver.find_element(by=By.ID, value="content")
    table_body = content.find_element(by=By.TAG_NAME, value="tbody")
    order = table_body.find_element(by=By.TAG_NAME, value="tr")
    order_info_row = order.find_elements(by=By.TAG_NAME, value="td")

    # click the "View" button to go to the Order Information page for that order
    view_order_button = order_info_row[-1].find_element(by=By.CLASS_NAME, value="btn-info")
    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "btn")))
    view_order_button.click()

    # locate the content of the Order Information page and the tables on it
    content = driver.find_element(by=By.ID, value="content")
    tables = content.find_elements(by=By.TAG_NAME, value="table")

    # locating the row for the first product
    products_table = tables[2]
    products_table_body = products_table.find_element(by=By.TAG_NAME, value="tbody")
    product_rows = products_table_body.find_elements(by=By.TAG_NAME, value="tr")
    product = product_rows[0]

    # store table headings for later use
    products_table_header = products_table.find_element(by=By.TAG_NAME, value="thead")
    products_table_headings = products_table_header.find_elements(by=By.TAG_NAME, value="td")

    # store the product information for later reference
    product_info = product.find_elements(by=By.TAG_NAME, value="td")
    product_info_dict = {str: str}
    for i in range(0, len(products_table_headings)):
        heading = products_table_headings[i].text.strip()
        value = product_info[i].text.replace('\n', '').strip()
        product_info_dict[heading] = value

    ''' information stored: 
        Product Name 	|Model 	    |Quantity 	|Price 	    |Total 
        ────────────────┼───────────┼───────────┼───────────┼───────
        Canon EOS 5D    |Product 3 	|1 	        |$98.00 	|$98.00	
    '''


    # find the cart's current number of items and its total
    cart_button = driver.find_element(by=By.ID, value="cart-total")
    cart_text = cart_button.text
    num_cart_items = int(cart_text.split()[0])
    cart_total_string = cart_text.split()[-1]
    cart_total = get_price_float(cart_total_string)

    # locate and click the reorder button
    product_reorder = product.find_element(by=By.CLASS_NAME, value="btn-primary")
    product_reorder.click()

    # update the expected number of items and total of the cart
    num_cart_items += 1
    product_price = get_price_float(product_info_dict.get("Price"))
    cart_total += float(product_price)

    # get cart button text
    cart_button = driver.find_element(by=By.ID, value="cart-total")
    cart_text = cart_button.text

    # Verify that the cart button now displays the correct number of items. 
    displayed_num_items = cart_text.split()[0]
    assert int(displayed_num_items) == num_cart_items, "number of items: button displayed != actual"

    # Verify that the cart button displays the correct total cost. 
    displayed_cart_total_string = cart_text.split()[-1]
    displayed_cart_total = get_price_float(displayed_cart_total_string)
    assert cart_total == displayed_cart_total, "cart total: button displayed != actual"

    # click the cart button to display the cart dropdown menu
    cart_button.click()

    # verify that the cart only contains one type of item (only has 1 row of items)
    cart_group = driver.find_element(by=By.ID, value="cart")
    cart_items_table = cart_group.find_element(by=By.CLASS_NAME, value="table-striped")
    cart_item_rows = cart_items_table.find_elements(by=By.TAG_NAME, value="tr")
    assert len(cart_item_rows) == 1, "cart does not contain exactly one type of item"

    # verify that the cart only contains the product added ("Canon EOS 5D - Select: Blue")
    item = cart_item_rows[0]
    item_sections = item.find_elements(by=By.TAG_NAME, value="td")
    item_name = item_sections[1].text.replace('\n', '').strip()
    assert item_name == product_info_dict.get("Product Name"), "first item in cart does not match product reordered"
    assert "Canon EOS 5D" in item_name and "Blue" in item_name, "first item in cart does not match product reordered"
    
    # verify that the cart dropdown menu displays the correct amount of the product
    amount_string = item_sections[2].text
    amount = int(amount_string.split()[1])
    assert amount == num_cart_items, "amount: menu displayed != actual"
    
    # verify that the product total for the item is correct ($602.00)
    product_total_string = item_sections[3].text.strip()
    product_total = get_price_float(product_total_string)
    assert product_total == get_price_float(product_info_dict.get("Price")) * amount, "product total: displayed != price * amount"

    # verify that the cart dropdown menu displays the correct cart total
    cart_total_breakdown = cart_group.find_element(by=By.CLASS_NAME, value="table-bordered")
    cart_total_breakdown_rows = cart_total_breakdown.find_elements(by=By.TAG_NAME, value="tr")
    cart_total_row = cart_total_breakdown_rows[-1].find_elements(by=By.TAG_NAME, value="td")
    cart_menu_total_string = cart_total_row[-1].text
    cart_menu_total = get_price_float(cart_menu_total_string)
    assert cart_menu_total == cart_total, "cart total: menu displayed != actual"

    # verify that the product total is the same as the cart total since there is only one type of item
    assert product_total == cart_total, "cart total: product total != actual"

    end(driver)


if __name__ == "__main__":
    retcode = pytest.main(["test_case_5_order_history.py", "-v"])