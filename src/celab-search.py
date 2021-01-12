from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
options.add_argument("--lang=es")
driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)

import re
import wikipediaapi
import requests
from requests.structures import CaseInsensitiveDict
from bs4 import BeautifulSoup
from pprint import pprint

wiki = wikipediaapi.Wikipedia('en')

def googleSearch(query):
  with requests.session() as c:
    url = 'https://www.google.com/search'
    query = {'q': '+'.join(query.split())}
    req = requests.get(url, params=query)
    html = BeautifulSoup(req.text, 'html.parser')
    return html

def extractInfoBox(url):
  req = requests.get(url)
  html = BeautifulSoup(req.text, 'html.parser')

  tt = str.maketrans({
    "\n": " ",
    "\xa0": " ",
    "\u200b": " ",
  })

  info = []
  for tr in html.select("table.infobox > tbody > tr"):
    children = list(tr.children)
    if len(children) != 2: continue
    key = ' '.join(children[0].text.translate(tt).split())
    value = list(map(lambda x: ' '.join(x.text.translate(tt).split()), children[1].select("li") if children[1].select("li") else [children[1]]))
    info.append((key, value))
  
  return CaseInsensitiveDict({k: v for k, v in info})

# with open("./annotations/top-100-celab.txt") as f:
#   for celab in map(lambda l: l.strip(), f.readlines()):
#     page = wiki.page(celab)
#     if not page.exists(): continue
#     info = extractInfoBox(page.fullurl)
#     print(f"=== {celab} ===")
#     pprint(info.get("children", None))


def googleConsent():
  try:
    consent_if_el = driver.find_element_by_css_selector("#cnsw > iframe")
    driver.switch_to.frame(consent_if_el)
    driver.find_element_by_id("introAgreeButton").click()
    driver.switch_to.default_content()
  except:
    pass

def googleSearchChildren(query):
  url = 'https://www.google.com/search'
  query = '+'.join(query.split())
  driver.get(f"{url}?q={query}&hl=en")
  googleConsent()
  extra_els = driver.find_elements_by_css_selector('#extabar [role="list"] > a')
  return list(map(lambda el: re.sub("\(.*?\)", "", el.get_attribute("title")).strip(), extra_els))

def googleSearchUI(query):
  url = 'https://www.google.com/search'
  query = '+'.join(query.split())
  driver.get(f"{url}?q={query}&hl=en")
  googleConsent()
  extra_els = driver.find_elements_by_css_selector('#extabar [role="list"] > a')
  pprint(list(map(lambda el: el.get_attribute("title"), extra_els)))



# html = googleSearch("angelina jouli")

pprint(googleSearchChildren("Angelina Jouli children"))
driver.quit()

# pprint(html)