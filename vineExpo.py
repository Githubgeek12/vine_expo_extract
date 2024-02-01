import functools
import time
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
n = 1
visited_urls = set()
last_visited_url = 0

def retry(max_retries, delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    print(f"Retrying after error: {e}")
                    time.sleep(delay)
            raise Exception(f"Max retries reached for {func.__name__}")

        return wrapper

    return decorator


@retry(max_retries=3)
def scrape_data():
    global last_visited_url
    driver = webdriver.Safari()
    driver.set_window_size(1200, 600)
    try:
        driver.get("https://wineparis-vinexpo.com/newfront/marketplace/exhibitors?limit=60")
        last_visited_url = driver.current_url
    except Exception:
        raise Exception('Error launching browser')
    scrape_pg(driver)


@retry(max_retries=3)
def scrape_pg(driver):
    global n, last_visited_url
    while True:

        try:
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#__next > div.MuiBox-root.css-g9qx4c > div.MuiBox-root.css-1roqr68 > main > div > div > div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-md-8.MuiGrid-grid-lg-9.css-vhv0fi > div > div.MuiBox-root.css-0 > div.MuiGrid-root.MuiGrid-container.MuiGrid-spacing-xs-2.css-1fxdrvb ")))
            print(driver.current_url)
            # Set the scroll increment (adjust as needed)
            scroll_increment = 800

            # Initial scroll position
            scroll_position = 0

            # Get the total height of the page
            total_height = driver.execute_script(
                "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

            while scroll_position < total_height:
                # Scroll down by the increment
                driver.execute_script(f"window.scrollBy(0, {scroll_increment});")

                total_height = driver.execute_script(
                    "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")

                # Wait for a short duration to allow content to load (adjust as needed)
                time.sleep(.5)

                # Update the scroll position
                scroll_position += scroll_increment

            ele1 = driver.find_elements(By.CSS_SELECTOR, '#__next > div.MuiBox-root.css-g9qx4c > div.MuiBox-root.css-1roqr68 > main > div > div > div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-md-8.MuiGrid-grid-lg-9.css-vhv0fi > div > div.MuiBox-root.css-0 > div.MuiGrid-root.MuiGrid-container.MuiGrid-spacing-xs-2.css-1fxdrvb > div')
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#__next > div.MuiBox-root.css-g9qx4c > div.MuiBox-root.css-1roqr68 > main > div > div > div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-md-8.MuiGrid-grid-lg-9.css-vhv0fi > div > div.MuiBox-root.css-0 > div.MuiGrid-root.MuiGrid-container.MuiGrid-spacing-xs-2.css-1fxdrvb > div:nth-child("+str(len(ele1))+") > div > div.MuiBox-root.css-cduqi1 > div.MuiBox-root.css-ob69bz > a > div > div")))
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#__next > div.MuiBox-root.css-g9qx4c > div.MuiBox-root.css-1roqr68 > main > div > div > div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-md-8.MuiGrid-grid-lg-9.css-vhv0fi > div > div.MuiBox-root.css-0 > div.MuiBox-root.css-1ek3hjv > nav > ul > li:nth-child(9) > button ')))
            button = driver.find_element(By.CSS_SELECTOR, '#__next > div.MuiBox-root.css-g9qx4c > div.MuiBox-root.css-1roqr68 > main > div > div > div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-md-8.MuiGrid-grid-lg-9.css-vhv0fi > div > div.MuiBox-root.css-0 > div.MuiBox-root.css-1ek3hjv > nav > ul > li:nth-child(9) > button ')
            if driver.current_url in visited_urls:
                print(f'page {driver.current_url} is already visited')
                print(last_visited_url)
                while last_visited_url != driver.current_url:
                    driver.execute_script("arguments[0].click();", button)
                    WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
                else:
                    driver.execute_script("arguments[0].click();", button)
                continue
            html = driver.page_source
        except Exception as e:
            print(e)
            driver.refresh()
            raise Exception("error loading page content")

        soup = bs(html, "html.parser")

        # titles = soup.select('#__next > div.MuiBox-root.css-g9qx4c > div.MuiBox-root.css-1roqr68 > main > div > div > div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-12.MuiGrid-grid-md-8.MuiGrid-grid-lg-9.css-vhv0fi > div > div.MuiBox-root.css-0 > .MuiGrid-root.MuiGrid-container.MuiGrid-spacing-xs-2.css-1fxdrvb div')
        titles = soup.find_all('div', class_='MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-sm-6 MuiGrid-grid-md-4 MuiGrid-grid-lg-3 css-1m6ye84')

        for indx, title in enumerate(titles):
            sele = 'div:nth-child(' + str(
                indx + 1) + ') > div > div.MuiBox-root.css-cduqi1 > div.MuiBox-root.css-ob69bz > a > div > div'
            name = title.select_one(sele).get_text()
            link = title.select_one('div:nth-child(' + str(indx + 1) + ') > div > div.MuiBox-root.css-79elbk > a')
            print(f"{n}){name}--------{link['href']}")
            n += 1
        visited_urls.add(driver.current_url)
        last_visited_url = driver.current_url
        if button.is_enabled():
            driver.execute_script("arguments[0].click();", button)
        else:
            break

    # Close the Browser
    driver.close()


scrape_data()
