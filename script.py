from flask import Flask, request, jsonify

from re import match
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
import time
import random

app = Flask(__name__)

def decrypt(encrypted_str):
    return encrypted_str # placeholder for rsa decryption

# endpoint to trigger task
@app.route('/get_burger', methods=['POST'])
def get_burger():
    data = request.json

    if not data:
        return jsonify({"error": "invalid or missing JSON"}), 400
    
    # extracting parameters - with proper type checks
    customizations = data.get("customizations", {})

    if not isinstance(customizations, dict):
        return jsonify({"error": "customizations must be a dictionary"}), 400
    toppings = customizations.get("toppings", [])
    sauces = customizations.get("sauces", [])

    if not isinstance(toppings, list) or not isinstance(sauces, list):
        return jsonify({"error": "toppings and sauces must be lists"}), 400
    
    # location and order time
    location = data.get("location")
    order_time = data.get("order_time")

    if not location or not isinstance(location, str):
        return jsonify({"error": "location must be a non-empty string"}), 400
    
    # card info
    card = data.get("card", {})
    if not isinstance(card, dict):
        return jsonify({"error": "card must be a dictionary"}), 400

    run_selenium_task(toppings, sauces, location, order_time, card)
    

# for more user-like movements
def get_human_like_options():
    options = Options()

    # Launch in normal (non-headless) mode
    # options.add_argument("--headless")  # Keep commented if you want visible
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-extensions")
    
    # Fake a random but valid user-agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")

    # No automation flag in JS
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    return options

def run_selenium_task(toppings, sauces, location, order_time, card):
    try:
        driver = webdriver.Chrome(options=get_human_like_options())

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

        time.sleep(3) # just to be safe

        print("we're good now")

        email_box = driver.find_element(By.ID, "inEmail")
        pw_box = driver.find_element(By.ID, "inPassword") 
        pw_2_box = driver.find_element(By.ID, "inVerifyPassword")
        first_name_box = driver.find_element(By.ID, "inFirstName")
        last_name_box = driver.find_element(By.ID, "inLastName")
        phone_box = driver.find_element(By.ID, "inPhone")

        email_box.send_keys(f"theharveyslover{email_number}@gmail.com")
        pw_box.send_keys("sexyharveys1")
        pw_2_box.send_keys("sexyharveys1")

        # extracting full name from card
        first_name_box.send_keys(card.get("name"))

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

        time.sleep(1.5)

        location_bar = driver.find_element(By.CSS_SELECTOR, 'input.autocomplete')
        location_bar.send_keys(location)

        time.sleep(1.5)

        # decide if we're going to 3343 bayview avenue or 2555 victoria park avenue or 170 University Avenue West
        restaurant_button = driver.find_element(
            By.XPATH,
            '//div[strong[text()="${location}"]]'
        )
        restaurant_button.click()

        time.sleep(0.5)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

        # you need this for bayview, though
        try:
            takeout_option = driver.find_element(By.XPATH, '//select[@class="secret"]/option[normalize-space()="Takeout"]')
            takeout_option.click()
        except Exception as e:
            print("i guess no takeout option")

        time.sleep(1)

        # selects order later
        if order_time != "now":
            try:
                later_label = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//label[normalize-space(text())='Later']"))
                )
                later_label.click()

                time_later = Select(driver.find_element(By.ID, "inTime"))
                time_later.select_by_value(order_time) # such as 20:30
            except Exception as e:
                print("defaulting to ordering now")

        # saves order setup
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

        # all toppings are ["Shredded Lettuce", "Onions", "Tomatoes", "Pickles", "Relish", "Hot Peppers", "Jalapeños", "Black Olives", "Cucumbers", "Salt & Pepper"]
        josh_toppings = ["Shredded Lettuce", "Onions", "Pickles", "Hot Peppers", "Jalapeños", "Black Olives", "Salt & Pepper"]
        richard_toppings = ["Shredded Lettuce", "Onions", "Pickles", "Cucumbers"]
        jeremy_toppings = ["Shredded Lettuce", "Pickles", "Onions", "Black Olives", "Salt & Pepper", "Relish"]
        alex_toppings = ["Shredded Lettuce", "Pickles", "Onions", "Tomatoes"]
        yoav_toppings = []
        jamieson_toppings = ["Shredded Lettuce", "Onions", "Pickles"]
        raymond_toppings = ["Shredded Lettuce", "Tomatoes", "Pickles", "Black Olives", "Cucumbers"]
        will_toppings = ["Shredded Lettuce", "Onions"]

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

        # all sauces are ["Ketchup", "Mustard", "Mayo", "BBQ Sauce", "Ghost Pepper Mayo", "Chipotle", "Harv Sauce", "Hot Sauce", "Garlic Mayo", "Ranch"]
        josh_sauces = ["Chipotle"]
        alex_sauces = ["Harv Sauce", "BBQ Sauce"]
        richard_sauces = []
        jeremy_sauces = ["BBQ Sauce", "Mayo", "Chipotle"]
        yoav_sauces = ["Ketchup"]
        ryan_sauces = ["Ketchup"]
        raymond_sauces = ["Ketchup"]
        will_sauces = ["Ghost Pepper Mayo", "Harv Sauce", "Ketchup"]

        # playing russian roulette with ghost pepper sauce - 1/6 chance to add death sauce
        # if random.random() < (1.0 / 6.0):
        #    sauces.append("Ghost Pepper Mayo")

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
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))

        try:
            confirm_button = driver.find_element(By.XPATH, '//button[normalize-space()="Confirm"]')
            confirm_button.click()
        except Exception as e:
            print("i guess no confirm button")

        time.sleep(1)

        time.sleep(0.5)

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

        card_number = decrypt(card.get("number"))
        card_name = card.get("name")
        card_cvv = decrypt(card.get("cvv"))
        card_postal_code = card.get("postal_code")
        card_month, card_year = card.get("expiry").split("/")

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

        complete_order_button.click()

        time.sleep(0.5)
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "spinner-overlay")))
        time.sleep(0.5)
        wait.until(
            EC.visibility_of_element_located((By.XPATH, "//*[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'feedback')]"))
        )

        print("burger ordered")
        return ("burger ordered", 200)
    
    except Exception as e:
        print(f"smth went wrong {e}")
        return ("smth went wrong", 500)

    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)