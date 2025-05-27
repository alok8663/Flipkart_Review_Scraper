import streamlit as st
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

st.set_page_config(layout="centered")
st.title("🛒 Flipkart Product Review Scraper")
st.write("Paste a Flipkart product URL below (e.g.- https://www.flipkart.com/gujarat-police-constable-gpc-exam-books-gujarati-set-3/p/itm42921c458a392 {not the whole url}) and click **Start Scraping**.")

product_url = st.text_input("Enter Flipkart Product URL:")
start_button = st.button("Start Scraping")

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless=new')  # use new headless mode
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

if start_button and product_url:
    with st.status("🔍 Launching browser and scraping reviews...", expanded=True) as status:
        reviews_data = []

        try:
            driver = setup_driver()
            wait = WebDriverWait(driver, 10)
            driver.get(product_url)
            time.sleep(3)

            def extract_reviews():
                try:
                    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'EKFha-')]")))
                    reviews = driver.find_elements(By.XPATH, "//div[contains(@class, 'EKFha-')]")
                    for review in reviews:
                        try:
                            rating = review.find_element(By.XPATH, ".//div[contains(@class, 'XQDdHH')]").text.strip()
                        except:
                            rating = "N/A"
                        try:
                            title = review.find_element(By.XPATH, ".//p[contains(@class, 'z9E0IG')]").text.strip()
                        except:
                            title = "N/A"
                        try:
                            body = review.find_element(By.XPATH, ".//div[contains(@class, 'ZmyHeo')]").text.strip()
                        except:
                            body = "N/A"
                        reviews_data.append([rating, title, body])
                except:
                    st.warning("❌ Failed to extract reviews from review page.")

            def extract_from_product_page():
                try:
                    wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='RcXBOT']")))
                    reviews = driver.find_elements(By.XPATH, "//div[@class='RcXBOT']")
                    for review in reviews:
                        try:
                            rating = review.find_element(By.XPATH, ".//div[@class='XQDdHH Js30Fc Ga3i8K']").text.strip()
                        except:
                            rating = "N/A"
                        try:
                            title = review.find_element(By.XPATH, ".//p[@class='z9E0IG']").text.strip()
                        except:
                            title = "N/A"
                        try:
                            body = review.find_element(By.XPATH, ".//div[@class='ZmyHeo']").text.strip()
                        except:
                            body = "N/A"
                        reviews_data.append([rating, title, body])
                except:
                    st.warning("❌ Failed to extract reviews from product page.")

            try:
                all_reviews_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'All') and contains(text(), 'review')]")))
                all_reviews_button.click()
                time.sleep(2)
                while True:
                    extract_reviews()
                    try:
                        next_button = driver.find_element(By.XPATH, "//nav//a[.//span[text()='Next']]")
                        if next_button.is_enabled():
                            next_button.click()
                            time.sleep(2)
                        else:
                            break
                    except:
                        break
            except:
                extract_from_product_page()

            driver.quit()

            if reviews_data:
                filename = "flipkart_reviews.csv"
                with open(filename, mode="w", newline='', encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(["User_Rating_Out_Of_5", "Review_Title", "Review_Body"])
                    writer.writerows(reviews_data)

                status.update(label="✅ Scraping completed!", state="complete", expanded=False)
                st.download_button("📥 Download CSV", data=open(filename, "rb").read(), file_name=filename)
            else:
                status.update(label="⚠️ No reviews were found.", state="error", expanded=True)

        except Exception as e:
            st.error(f"❌ An error occurred:\n```\n{str(e)}\n```")
