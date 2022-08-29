import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def get_lotto_table_raw()->pd.DataFrame:
    """gets the raw table of the lotto winnings from yotta.

    Yotta is a a fintech company that aims to promote savings by giving its users a slightly higher than average savings rate and
    a weekly chance at a lottery. The tickets to their lotto scales with the amount you have in your bank account.
    It was inspired by the Premium Bond program in the UK. https://en.wikipedia.org/wiki/Premium_Bond

    there isn't a table of the winnings so we can't use pd.read_html
    instead we gotta scrape it

    first the function will get the html of winnings page and target a subset of the page that shold contain the table

    Returns:
        pandas.DataFrame: raw table of the lotto winnings from yotta, should have winnings, odds and conditions of winning
    """
    URL = "https://www.withyotta.com/official-rules"
    r = requests.get(URL)
    soup = BeautifulSoup(r.text, 'html.parser')


    #get table headings
    headers = [thing.string for thing in soup.find_all("div", attrs={"class": "table-block table-header"})]

    data = {title:[] for title in headers}
    data_hash = {index:title for index,title in enumerate(headers)}

    num_headers = len(data)
    
    #get table contents and place them in right key value pair
    for index,tag in enumerate(soup.find_all("div", attrs={"class": "table-block"})):
    
        if tag.string in data.keys():
            pass
        else:
            data[data_hash[index%num_headers]].append(tag.string)
        
    return pd.DataFrame(data)

def clean_prize(some_str:str)->float:
    """cleans each entry of prize to get raw value

    Args:
        some_str (str): entry comes in a str

    Returns:
        float: number repersentation of some_str
    """


    some_str = some_str.replace("..",".")
    some_str = some_str.replace(",","")

    pattern = r"[0-9]+\.?[0-9]*"
    
    return float(re.search(pattern,some_str)[0])
    
def clean_odds(some_str):
    """cleans each entry of odds to get raw value

    Args:
        some_str (str): entry comes in a str

    Returns:
        float: number repersentation of some_str
    """

    some_str = some_str.replace(",","")

    pattern = r"(?<=:)[0-9]+"
    odds = float(re.search(pattern,some_str)[0])
    
    return 1/(1+odds)

def get_column(df:pd.DataFrame,some_str:str)->str:
    """returns first column that matches some_str

    Args:
        df (pd.DataFrame): df
        some_str (str): pattern that you care about

    Returns:
        str: name of column that matched some_str
    """
    for column in df.columns:
        if re.search(some_str,column,re.IGNORECASE):
            return column

    return None

def get_lotto_table()->pd.DataFrame:
    """gets a cleaned table of the lotto winnings from yotta


    Returns:
        pd.DataFrame: table of the lotto winnings from yotta, should have winnings, odds and conditions of winning
    """
    
    df = get_lotto_table_raw()

    prize_column = get_column(df,"prize")
    odds_column = get_column(df,"odds")

    
    df["winnings"] = df[prize_column].apply(lambda prize_str: clean_prize(prize_str))
    df["probability"] = df[odds_column].apply(lambda odds_str: clean_odds(odds_str))


    df["expected_winnings"] = df["winnings"] * df["probability"]
    
    return df