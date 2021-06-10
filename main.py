import bs4
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
from urllib3.packages.six import _import_module

cpu_url = "https://www.bestbuy.com/site/amd-ryzen-5-5600x-4th-gen-6-core-12-threads-unlocked-desktop-processor-with-wraith-stealth-cooler/6438943.p?skuId=6438943"
gpu_url = "https://www.bestbuy.com/site/nvidia-geforce-rtx-3070-ti-8gb-gddr6x-pci-express-4-0-graphics-card-dark-platinum-and-black/6465789.p?skuId=6465789"
test_url = "https://www.bestbuy.com/site/tripp-lite-6-usb-type-a-to-usb-type-b-cable-black/9598875.p?skuId=9598875"

def login(driver, usr, pwd):
    driver.get("https://www.bestbuy.com/identity/signin?token=tid%3A1e1c8ef8-c98a-11eb-93b5-12d11c10de83")
    driver.find_element_by_id("fld-e").send_keys(usr)
    driver.find_element_by_id("fld-p1").send_keys(pwd)
    driver.find_element_by_class_name("cia-form__controls__submit").click()
    time.sleep(3)


def patrol_item(driver, item_url):
    driver.get(item_url)
    try:
        add_to_cart = driver.find_element_by_class_name("add-to-cart-button")
        active_btn = True if add_to_cart.get_attribute("disabled") == None else False
    except:
        active_btn = False

    # Wait for change add to cart btn to change w/ product release.
    #print(add_to_cart.get_attribute("disabled"))
    while not active_btn:
        driver.refresh()
        time.sleep(3)
        try:
            add_to_cart = driver.find_element_by_class_name("add-to-cart-button")
            active_btn = True if add_to_cart.get_attribute("disabled") == None else False
            print("loop 1. disbled value:", add_to_cart.get_attribute("disabled"))
        except:
            print("error in loop 1")
            continue

    time.sleep(3)
    add_to_cart.click()
    time.sleep(3)

    # Check if adding somehow goes off w/o a hitch.
    print(driver.current_url)
    if driver.current_url == "https://www.bestbuy.com/cart":
        return 1

    try:
        add_to_cart = driver.find_element_by_class_name("add-to-cart-button")

        # Handle "Please Wait" case.
        while add_to_cart.get_attribute("disabled") == None:
            add_to_cart = driver.find_element_by_class_name("add-to-cart-button")
            print("spinning...")
    except:
        pass

    # Wait for product queue to end.
    print("loop 2. disbled value:", add_to_cart.get_attribute("disabled"))
    active_btn = False
    while not active_btn:
        time.sleep(3)
        driver.refresh()
        try:
            add_to_cart = driver.find_element_by_class_name("add-to-cart-button")
            active_btn = True if add_to_cart.get_attribute("disabled") == None else False
            print("loop 2. disbled value:", add_to_cart.get_attribute("disabled"))
        except:
            print("error in loop 2")
            continue


    # Item should be added to cart w/ this click.
    add_to_cart.click()
    time.sleep(3)
    print("exiting patrol")

    return 1


def checkout(driver, cvv):
    print("starting checkout...")

    if driver.current_url != "https://www.bestbuy.com/cart":
        driver.get("https://www.bestbuy.com/cart")
        time.sleep(3)

    # No populated-cart element means item was lost. Retry.
    try:
        driver.find_element_by_class_name("populated-cart")
    except NoSuchElementException:
        print("cart unpopulated")
        return -1

    try:
        driver.find_element_by_class_name("checkout-buttons__checkout").click()
    except:
        checkout(driver, cvv)

    try:
        driver.find_element_by_id("credit-card-cvv").send_keys(cvv)
    except:
        pass

    return 0


def main():
    print("User Info Input (I promise I don't do anything with these)")
    usr = input("Best Buy Username: ")
    pwd = input("Best Buy Password: ")
    cvv = input("Credit Card CVV: ")

    driver = webdriver.Firefox()
    login(driver, usr, pwd)

    patrol_result = patrol_item(driver, test_url)

    while patrol_result == 1:

        while checkout(driver, cvv) == -1:
            patrol_result = patrol_item(driver, test_url)


if __name__ == "__main__":
    main()