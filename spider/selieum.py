import time
import re
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
import pymysql
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def mysql():
    conn = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='Aa123456',
        database='contract',
        port=3306,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url="https://htsfwb.samr.gov.cn/List?key=%E4%BD%8F%E6%88%BF%E7%A7%9F%E8%B5%81")
    time.sleep(2)
    driver.execute_script("switchType(true); loadFilters(false);")
    time.sleep(5)

    conn = mysql()
    cursor = conn.cursor()
    list_window = driver.current_window_handle

    for page in range(1,3):
        elements = driver.find_elements(By.CSS_SELECTOR,"#list-data-local .item-box a")
        print("第",page,"页合同数量：",len(elements))

        for i in range(len(elements)):
            elements = driver.find_elements(By.CSS_SELECTOR,"#list-data-local .item-box a")
            title = elements[i].text.strip()
            url = elements[i].get_attribute("href")
            print("正在爬取：",title)

            driver.execute_script("window.open(arguments[0]);",url)
            driver.switch_to.window(driver.window_handles[-1])
            WebDriverWait(driver,10).until(lambda d:d.execute_script("return document.readyState")=="complete")
            time.sleep(1)

            raw_text = driver.find_element(By.TAG_NAME,"body").text.strip()
            start = raw_text.find("合同编号：")
            if start == -1:
                start = raw_text.find(title)
            end = raw_text.find("发布机关：")
            if end == -1:
                end = raw_text.find("下载Word文档")
            if end == -1:
                end = raw_text.find("下载PDF文档")

            if start != -1 and end != -1 and end > start:
                cleaned_text = raw_text[start:end].strip()
            elif start != -1:
                cleaned_text = raw_text[start:].strip()
            else:
                cleaned_text = raw_text

            org_match = re.search(r"发布机关：\s*(.*?)\s*发布年份：",raw_text,re.S)
            if org_match:
                source_org = org_match.group(1).strip()
            else:
                source_org = None

            year_match = re.search(r"发布年份：\s*(\d{4})",raw_text)
            if year_match:
                publish_year = int(year_match.group(1))
            else:
                publish_year = None

            content_hash = hashlib.sha256(cleaned_text.encode("utf-8")).hexdigest()
            cursor.execute("SELECT id FROM contract_corpus WHERE source_url=%s",(url,))
            old = cursor.fetchone()

            if old:
                print("已存在：",title)
            else:
                sql = """INSERT INTO contract_corpus
                (title,contract_type,source_url,source_org,source_type,region,publish_year,raw_text,cleaned_text,content_hash,dataset_usage,ragflow_status)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                cursor.execute(sql,(title,'housing_lease',url,source_org,'official_template',None,publish_year,raw_text,cleaned_text,content_hash,'pending','pending'))
                conn.commit()
                print("已保存：",title)

            driver.close()
            driver.switch_to.window(list_window)
            time.sleep(1)

        if page == 1:
            old_elements = driver.find_elements(By.CSS_SELECTOR,"#list-data-local .item-box a")
            old_first = old_elements[0]
            page2 = driver.find_element(By.CSS_SELECTOR,"#pagination-local a[data-page='2']:not(.next)")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});",page2)
            time.sleep(1)
            ActionChains(driver).move_to_element(page2).click().perform()

            WebDriverWait(driver,15).until(EC.staleness_of(old_first))
            WebDriverWait(driver,15).until(
                lambda d:"active" in d.find_element(By.CSS_SELECTOR,"#pagination-local a[data-page='2']:not(.next)").get_attribute("class")
            )
            time.sleep(3)

            print("已真正切换到第二页")

    cursor.close()
    conn.close()
    driver.quit()