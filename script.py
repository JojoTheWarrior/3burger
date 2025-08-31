from re import match
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import random

# is this incognito or normal mode?
driver = webdriver.Chrome()

driver.get("https://order.harveys.ca/login")

wait = WebDriverWait(driver, 20)

wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

# signing up
sign_up_button = driver.find_element(By.ID, "btnSignup")
sign_up_button.click()

# filling out the form
email_number = 0
with open("email_number.txt", "r") as file:
    email_number = int(file.read().strip())
print(email_number)
with open("email_number.txt", "w") as file:
    file.write(str(email_number + 1))

time.sleep(1)

email_box = driver.find_element(By.ID, "inEmail")
pw_box = driver.find_element(By.ID, "inPassword") 
pw_2_box = driver.find_element(By.ID, "inVerifyPassword")
first_name_box = driver.find_element(By.ID, "inFirstName")
last_name_box = driver.find_element(By.ID, "inLastName")
phone_box = driver.find_element(By.ID, "inPhone")

email_box.send_keys(f"joshua.wang{email_number}@gmail.com")
pw_box.send_keys("jojothewarrior1")
pw_2_box.send_keys("jojothewarrior1")
first_name_box.send_keys("Joshua")

suffix = ""
match email_number % 10:
    case 1:
        "st"
    case 2:
        "nd"
    case 3:
        "rd"
    case _:
        "th"

last_name_box.send_keys(f"The Harvey's Lover")
phone_box.send_keys("1234567890")

time.sleep(0.5)

sign_up_button = (driver.find_elements("xpath", "//button[contains(normalize-space(.), 'Sign Up')]"))[1]

time.sleep(0.5)
sign_up_button.click()

time.sleep(0.5)
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

# navigating to coupons
coupon_button = driver.find_element(By.LINK_TEXT, "Coupons")
coupon_button.click()

time.sleep(0.5)
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

# wait for "ok" button to pop up

time.sleep(1)

ok_button = (driver.find_elements(By.XPATH, '//button[text()="Ok"]'))[4]
ok_button.click()

time.sleep(1)

location_bar = driver.find_element(By.CSS_SELECTOR, 'input.autocomplete')
location_bar.send_keys("170 University Ave W")

time.sleep(1)

# decide if we're going to 3343 bayview avenue or 2555 victoria park avenue
restaurant_button = driver.find_element(
    By.XPATH,
    '//div[strong[text()="170 University Ave W"]]'
)
restaurant_button.click()

time.sleep(0.5)
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

takeout_option = driver.find_element(By.XPATH, '//select[@class="secret"]/option[normalize-space()="Takeout"]')
takeout_option.click()

time.sleep(1)

save_order_setup = driver.find_element("xpath", "//button[contains(normalize-space(.), 'Save Order Setup')]")
save_order_setup.click()

# go to add coupon code page
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))
time.sleep(0.5)

add_coupon_code = driver.find_element("xpath", "//a[contains(normalize-space(.), '+ Add Coupon Code')]")
add_coupon_code.click()

time.sleep(0.5)

coupon_code = driver.find_element(By.ID, "inCouponCode")
coupon_code.send_keys("3BURGER")

time.sleep(0.5)

add_coupon = driver.find_element(By.XPATH, "//button[contains(normalize-space(.), 'Add Coupon')]")
add_coupon.click()

time.sleep(0.5)
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

use_coupon = driver.find_element(By.XPATH, "//button[contains(normalize-space(.), 'Use Coupon')]")
use_coupon.click()

time.sleep(0.5)
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

original_burger = driver.find_element(
    "xpath",
    "//div[contains(@class, 'option-element') and .//label[@title='Original Burger']]"
)
original_burger.click()
time.sleep(0.5)

toppings_div = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//div[@id='toppingSelect']//div[contains(@class,'heading') and .//h4[text()='Toppings']]")
    )
)
toppings_div.click()

time.sleep(1)

toppings = ["Shredded Lettuce", "Tomatoes", "Onions", "Pickles", "Hot Peppers", "Jalapeños", "Black Olives", "Salt & Pepper"]

for topping in toppings:
    topping_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            f"//div[contains(@class,'topping-option')][.//span[contains(normalize-space(text()), '{topping}')]]"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", topping_button)
    topping_button.click()
    time.sleep(0.5) # experimental feature - spending 1/2 second on each topping

time.sleep(0.5)

sauces_div = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//div[@id='toppingSelect']//div[contains(@class,'heading') and .//h4[text()='Sauces']]")
    )
)
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sauces_div)
sauces_div.click()

time.sleep(1)

sauces = ["Chipotle"]

# playing russian roulette with ghost pepper sauce - 1/6 chance to add death sauce
if random.random() < (1.0 / 6.0):
    sauces.append("Ghost Pepper Mayo")

for sauce in sauces:
    sauce_button = wait.until(
        EC.element_to_be_clickable((
            By.XPATH,
            f"//div[@id='config2']//div[contains(@class, 'topping-option')][.//span[normalize-space(text())='{sauce}']]"
        ))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sauce_button)
    sauce_button.click()
    time.sleep(0.5) # experimental feature - spending 1/2 second on each sauce

time.sleep(0.5)

# clicks "continue"
continue_button = driver.find_element(
    By.XPATH,
    '//button[@alt="Continue"]'
)
continue_button.click()

time.sleep(0.5)

# clicks "Add to Cart"
add_to_cart_button = driver.find_element(
    By.XPATH,
    '//button[@alt="Add to Cart"]'
)
add_to_cart_button.click()

# clicks "view cart"
time.sleep(0.5)

view_cart_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, '//button[normalize-space()="View cart"]')
    )
)
view_cart_button.click()

time.sleep(0.5)
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

# clicks "checkout"

checkout_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, '//button[normalize-space()="Checkout"]')
    )
)

checkout_button.click()

time.sleep(0.5)
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

# clicks "confirm"
time.sleep(0.5)
confirm_button = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, '//button[normalize-space()="Confirm"]')
    )
)
confirm_button.click()

time.sleep(0.5)
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))
time.sleep(1)

# clicks paying option
new_cc_radio = wait.until(
    EC.element_to_be_clickable(
        (By.ID, "inNewCC")
    )
)
new_cc_radio.click()

time.sleep(0.5)
wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

# fills out card info
cc_number_box = driver.find_element(By.ID, "inCCnumber")
cc_name_box = driver.find_element(By.ID, "inCCname")
cc_cvv_box = driver.find_element(By.ID, "inCVVCode")
cc_postal_code_box = driver.find_element(By.ID, "inPostalCode")
expiry_month_select = Select(driver.find_element(By.ID, "inExpiryMonth"))
expiry_year_select = Select(driver.find_element(By.ID, "inExpiryYear"))

card_number = "1234123412341234"
card_name = "Hugh Mongus"
card_cvv = "123"
card_postal_code = "A1B2C3"
card_month = "08"
card_year = "2025"

cc_number_box.send_keys(card_number)
cc_name_box.send_keys(card_name)
cc_cvv_box.send_keys(card_cvv)
cc_postal_code_box.send_keys(card_postal_code)
expiry_month_select.select_by_value(card_month)
expiry_year_select.select_by_value(card_year)

# sends in the order
complete_order_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//button[normalize-space(text())='Complete Order']"))
)

# complete_order_button.click()

time.sleep(5)

