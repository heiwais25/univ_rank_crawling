import json
from six import string_types
from bs4 import BeautifulSoup
from selenium import webdriver

def check_PhantomJS_driver(driver):
    '''
        Check whether the driver is PhantomJS webdriver
        Args:
            driver(webdriver.PhantomJS) : initiated PhantomJS driver
    '''
    if not isinstance(driver, webdriver.PhantomJS):
        raise TypeError("driver should be PhantomJS webdriver")
    

def init_web_driver(drive_dir):
    '''
        Assuming we use PhantomJS for the webdriver
        
        Args:
            driver_dir(str) : directory that driver located in
        Returns:
            driver(webdriver.PhantomJS) : initiated PhantomJS driver
    '''
    if not isinstance(drive_dir, string_types):
        raise TypeError("argument should be string")
    driver = webdriver.PhantomJS(str(drive_dir))
    return driver


def connect_to_url(driver, url):
    '''
        Connect to specific url using webdriver
        
        Args: 
            driver(webdriver.PhantomJS) : PhantomJS driver
            url(str) : string that contain information of url
        Returns:
            driver(webdriver.PhantomJS) : PhantomJS driver
    '''
    check_PhantomJS_driver(driver)
    if not isinstance(url, string_types):
        raise TypeError("url should be string")

    driver.get(url)
    return driver


def get_univ_rank(driver, univ_info, univ_rank_map):
    '''
        It will read rank information of university under the selected subject option
        The list of university and country will be stored in the univ_info to prevent that we need to 
        store string information every time
        
        Args:
            driver(webdriver.PhantomJS) : PhantomJS driver
            univ_info(dict)     : including university name list and its corresponding country
            univ_rank_map(dict) : connect university name to its index in the univ_info

        Returns:
            univ_info(dict)     : including university name list and its corresponding country
            univ_rank_map(dict) : connect university name to its index in the univ_info
            ranks(list)         : include index of university in the order obtained under the subject condition
    '''
    check_PhantomJS_driver(driver)
    if not isinstance(univ_info, dict) or not isinstance(univ_rank_map, dict):
        raise TypeError("univ_info and univ_rank_map should be dict format")

    # This is restricted to the "qsranking website" 
    driver.find_element_by_xpath("//div[@class='dataTables_length']/label/span/span[@class='jcf-select-opener']").click()
    driver.find_element_by_xpath("//div[@class='jcf-select-drop jcf-select-jcf-hidden jcf-unselectable']/div/span/span/ul/li/span[text()='All']").click()

    soup = BeautifulSoup(driver.page_source, 'lxml')
    rankTable = soup.find("table",{"id":"qs-rankings"})

    univ_names = [tag.get_text() for tag in rankTable.select("a[class*='title']")]
    country_names = [tag.get_text() for tag in rankTable.find_all("td", {"class":" country"})] 
    ranks = []

    # In the case of calling this function first time (used for reading rank under the any subject condition)
    if len(univ_rank_map) == 0:
        univ_info["name"] = univ_names
        univ_info["country"] = country_names
        univ_rank_map = {name : idx for idx, name in enumerate(univ_names)}

        # Set rank of default
        ranks = list(range(len(univ_rank_map)))

    else:
        for univ_name, country_name in zip(univ_names, country_names):
            if univ_name not in univ_rank_map:
                univ_info["name"].append(univ_name)
                univ_info["country"].append(country_name)
                univ_rank_map[univ_name] = len(univ_rank_map)
            ranks.append(univ_rank_map[univ_name])

    return univ_info, univ_rank_map, ranks


def get_subject_href(driver, url):
    '''
        It will get href corresponding to the list obtained under the each condition

        Args:
            driver(webdriver.PhantomJS) : PhantomJS driver
            url(str) : string that contain information of url

        Returns:
            subject_href(dict) : dict including href info corresponding to each subject
    '''
    check_PhantomJS_driver(driver)
    if not isinstance(url, string_types):
        raise TypeError("url should be string")
    driver = connect_to_url(driver, url)
    subject_container = driver.find_elements_by_class_name("sub-list")
    subject_href = {}

    for div in subject_container:
        a_container = div.find_elements_by_tag_name("a")
        for a in a_container:
            subject_href[a.text] = a.get_attribute("href")
            
    return subject_href


default_drive_dir = "C:\\Users\\heiwa\\Desktop\\package\\driver\\phantomjs"
default_rank_url = "https://www.topuniversities.com/university-rankings/world-university-rankings/2018"
subject_rank_url = "https://www.topuniversities.com/subject-rankings/2018"
default_json_file_name = "univ_rank.json"


def crawling(drive_dir = default_drive_dir,
                    rank_url = default_rank_url,
                    subject_url = subject_rank_url,
                    json_file_name = default_json_file_name):
    '''
        Update university rank by reading the website 

        Args:
            driver_dir(str) : directory that driver located in
            rank_url(str) : url showing ranks under any subject condition
            subject_url(str) : url showing categories
            json_file_name(str) : file name or path where we want to save json file
    '''
    if not isinstance(drive_dir, string_types) or not isinstance(rank_url, string_types) \
        or not isinstance(subject_rank_url, string_types) or not isinstance(json_file_name, string_types):
        raise TypeError("Arguments should be string")

    driver = init_web_driver(drive_dir)

    univ_rank_info = {} # It will include all rank informatio
    rank_info = {} # Include rank under each condition
    univ_rank_map = {} # Map connecting the university name and index in order of default rank
    rank_by_subject = {} # Save rank in the condition of subject

    # Get basic university ranking
    driver = connect_to_url(driver, rank_url) 

    univ_info = {
        "name" : [],
        "country" : []
    }

    univ_info, univ_rank_map, ranks = get_univ_rank(driver, univ_info, univ_rank_map)
    print("Get basic ranking")

    univ_rank_info["univ_info"] = univ_info
    rank_info["default"] = ranks
    
    # Get other subject ranking
    subject_href = get_subject_href(driver, subject_url)

    for subject, href in subject_href.items():
        driver = connect_to_url(driver, href)
        univ_info, univ_rank_map, rank_by_subject[subject] = get_univ_rank(driver, univ_info, univ_rank_map)
        print("Get %s" % subject)

    rank_info["subject"] = rank_by_subject

    # Collect overall data for rank
    univ_rank_info["rank"] = rank_info

    # Save rank information in the format of json
    with open(json_file_name, 'w', encoding="utf-8") as fp:
        json.dump(univ_rank_info, fp, ensure_ascii=False, indent="\t")
