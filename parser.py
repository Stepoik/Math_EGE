from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import re
import sqlite3
import requests
import random
from selenium.webdriver.common.action_chains import ActionChains


db = sqlite3.connect("db.sqlite3")
cur = db.cursor()

num_re = re.compile(r"(№ \w+)")
def polyk():
    with webdriver.Firefox(executable_path="geckodriver.exe") as driver:
        driver.get("https://kpolyakov.spb.ru/school/ege/generate.htm")
        cats = driver.find_element(By.ID, "egeId")
        for cat in range(len(cats.find_elements(By.TAG_NAME, "option"))):
            nowcats = driver.find_element(By.ID, "egeId")
            nowcat = nowcats.find_elements(By.TAG_NAME, "option")[cat]
            nowcat.click()
            sleep(0.5)
            button = driver.find_element(By.XPATH, "//input[@value='Найти все задачи']")
            button.click()
            sleep(1)
            for quest in driver.find_elements(By.CLASS_NAME, "hidedata"):
                cur.execute(f"""
                        insert into tasks(site_id,answer) values({quest.get_attribute("id")},'{quest.get_attribute("innerHTML").split(">")[-1]}')
                """)
                db.commit()
            ege_num = driver.find_element(By.CLASS_NAME, "title").text.split()[-1]

            for quest in driver.find_elements(By.CLASS_NAME, "topicview"):
                cur.execute(f'''
                    update tasks
                    set text = '{quest.text.replace("'","")}', ege_num = '{ege_num}'
                    where site_id = {num_re.findall(quest.text)[0].split()[1]}
               ''')
                db.commit()
            driver.back()
def reshuege_rus():
    profile = FirefoxProfile()
    profile.set_preference("network.http.connection-timeout", 10)
    with webdriver.Firefox(executable_path="geckodriver.exe", firefox_profile=profile) as driver:
        last = 3
        finish = 19
        while last != finish:
            try:
                driver.get("https://math-ege.sdamgia.ru/")
                input_prob = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME,"prob"+str(last))))
                input_prob.send_keys(250)
                button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@class='Button Button_view_default Button_size_l ConstructorForm-SubmitButton']")))
                button.click()

                WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.CLASS_NAME, "nobreak")))
                for k in driver.find_elements(By.XPATH, "//a[contains(text(), 'Показать')]"):
                    k.click()
                texts_elements = driver.find_elements(By.CLASS_NAME, "nobreak")
                texts = []
                for j in texts_elements:
                    if j.text != "":
                        texts.append(j.text)
                button_save = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, "//input[@value='Сохранить']")))
                button_save.click()
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.CLASS_NAME, "res_row")))
                for k,i in enumerate(driver.find_elements(By.CLASS_NAME, "res_row")):
                    info = []
                    for j in i.find_elements(By.TAG_NAME, "td"):
                        info.append(j.text)
                    cur.execute(f"select * from task_math where id={info[1]}")
                    if cur.fetchone() is None:
                        cur.execute(f'''insert into task_math(id,ege_id,ans) values({info[1]},'{info[2]}','{info[4]}')''')
                        db.commit()
                last+=1
            except Exception as e:
                print(e)
                continue
def math():
    with webdriver.Chrome(executable_path="chromedriver.exe") as driver:
        actions = ActionChains(driver)
        driver.get("https://math-ege.sdamgia.ru/")
        themes = driver.find_elements(By.CLASS_NAME, "ConstructorForm-TopicDesc")
        last = len(themes)
        now = 121
        print(1)
        while now != last:
            try:
                wait = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, "ConstructorForm-TopicDesc")))
                nowthemes = driver.find_elements(By.CLASS_NAME, "ConstructorForm-TopicDesc")
                theme = nowthemes[now]
                print(now,theme.get_attribute("innerHTML"))
                if len(theme.find_elements(By.TAG_NAME, "a")) == 0:
                    now+=1
                    continue
                theme_text = theme.get_attribute("innerHTML").split("&")[0]
                theme_link = theme.find_element(By.TAG_NAME, "a").get_attribute("href")
                driver.get(theme_link+'&ttest=true')
                WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.CLASS_NAME, "prob_maindiv")))
                for k in driver.find_elements(By.XPATH, "//a[contains(text(), 'Показать')]"):
                    k.click()
                texts_elements = driver.find_elements(By.CLASS_NAME, "prob_maindiv")
                inputs = driver.find_elements(By.CLASS_NAME,"prob_view")
                texts = []
                for k,j in zip(inputs,texts_elements):
                    actions.move_to_element(k).perform()
                    prob_num = j.find_element(By.CLASS_NAME,"prob_nums").text.split()[-1]
                    prob_num_ege = j.find_element(By.CLASS_NAME,"prob_nums").text.split()[1]
                    url = "images/"+str(prob_num)+".png"
                    j.screenshot(url)
                    cur.execute(f"select * from task_math where id={prob_num}")
                    if cur.fetchone() is None:
                        cur.execute(
                            f'''insert into task_math(id, cat,ege_id,image) values({prob_num}, '{theme_text}','{prob_num_ege}', '{url}')''')
                        db.commit()
                try:
                    button_save = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                        (By.XPATH, "//input[@value='Сохранить']")))
                    button_save.click()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                        (By.CLASS_NAME, "res_row")))
                    print(len(driver.find_elements(By.CLASS_NAME, "res_row")))
                    for k,i in enumerate(driver.find_elements(By.CLASS_NAME, "res_row")):
                        info = []
                        for j in i.find_elements(By.TAG_NAME, "td"):
                            info.append(j.text)
                        print(info)
                        cur.execute(f'''update task_math set ans = '{info[4]}', ege_id = '{info[2]}' where id = {info[1]} ''')
                        db.commit()
                except Exception as e:
                    print(e)
                    pass
                now+=1
                driver.get("https://math-ege.sdamgia.ru/")
            except Exception as e:
                driver.get("https://math-ege.sdamgia.ru/")
                print(e)
                continue
def get_solution():
    cur.execute("select * from task_math")
    all_solutions = cur.fetchall()
    start = 866
    with webdriver.Chrome(executable_path="chromedriver.exe") as driver:
        actions = ActionChains(driver)
        while start != len(all_solutions):
            try:
                driver.get("https://math-ege.sdamgia.ru/problem?id="+str(all_solutions[start][0]))
                actions.move_to_element(driver.find_element(By.CLASS_NAME,"minor")).perform()

                solution = driver.find_element(By.CLASS_NAME,"solution")
                print(solution.text)
                solution.screenshot(f"answers/{all_solutions[start][0]}.png")
                start+=1
            except:
                continue
get_solution()
