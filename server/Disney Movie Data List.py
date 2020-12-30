#!/usr/bin/env python
# coding: utf-8

# In[19]:


# Import neccessary libraries

from bs4 import BeautifulSoup as bs
import requests


# In[20]:


r = requests.get("https://en.wikipedia.org/wiki/Toy_Story_3")

# Convert to a BeautifulSoup object
soup = bs(r.content)

# Print out HTML
contents = soup.prettify()
print(contents)


# In[21]:


info_box = soup.find(class_="infobox vevent")
info_rows = info_box.find_all("tr")
for row in info_rows:
    print(info_box.prettify())


# In[22]:


def get_content_value(row_data):
    if row_data.find("li"):
        return [li.get_text(" ", strip=True).replace("\xa0", " ") for li in row_data.find_all("li")]
    else:
        return row_data.get_text(" ", strip=True).replace("\xa0", " ")
    
movie_info = {}
for index, row in enumerate(info_rows):
    if index == 0:
        movie_info['title'] = row.find("th").get_text(" ", strip=True)
    elif index == 1:
        continue
    else:
        content_key = row.find("th").get_text(" ", strip=True)
        content_value = get_content_value(row.find("td"))
        movie_info[content_key] = content_value
    
movie_info


# # TASK 2: GRAB THE MOVIE LIST

# In[23]:


r = requests.get("https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films")

# Convert to a BeautifulSoup object
soup = bs(r.content)

# Print out HTML
contents = soup.prettify()
print(contents)


# In[24]:


movies = soup.select(".wikitable.sortable i")
print(movies[0:10]) # selecting 10 items


# In[25]:


def get_content_value(row_data):
    if row_data.find("li"):
        return [li.get_text(" ", strip=True).replace("\xa0", " ") for li in row_data.find_all("li")]
    elif row_data.find("br"):
        return [text for text in row_data.stripped_strings]
    else:
        return row_data.get_text(" ", strip=True).replace("\xa0", " ")
    
    
def clean_tags(soup):
    for tag in soup.find_all(["sup", "span"]):
        tag.decompose()


def get_info_box(url):
    
    r = requests.get(url)

    soup = bs(r.content)
    contents = soup.prettify()
    info_box = soup.find(class_="infobox vevent")
    info_rows = info_box.find_all("tr")
    
    clean_tags(soup)

    movie_info = {}
    for index, row in enumerate(info_rows):
        if index == 0:
            movie_info['title'] = row.find("th").get_text(" ", strip=True)
        else:
            header = row.find('th')
            if header:
                content_key = row.find("th").get_text(" ", strip=True)
                content_value = get_content_value(row.find("td"))
                movie_info[content_key] = content_value

    return movie_info


# In[26]:


get_info_box("https://en.wikipedia.org/wiki/The_Nightmare_Before_Christmas")


# In[ ]:





# In[27]:


r = requests.get("https://en.wikipedia.org/wiki/List_of_Walt_Disney_Pictures_films")
soup = bs(r.content)
movies = soup.select(".wikitable.sortable i a")

base_path = "https://en.wikipedia.org/"

movie_info_list = []
for index, movie, in enumerate(movies):
    if index % 10 == 0:
        print(index)
  
    try:
        relative_path = movie['href']
        full_path = base_path + relative_path
        title = movie['title']
    
        movie_info_list.append(get_info_box(full_path))
        
    except Exception as e:
        print(movie.get_text())
        print(e)
       


# In[28]:


len(movie_info_list)


# #### Save/Reload Movie Data (json file is here "disney_data.json" saved to Jonshish on my computer)

# In[134]:


import json

def save_data(title, data):
    with open(title, 'w', encoding='utf-8') as f:
        return json.dump(data, f, ensure_ascii=False, indent=2)


# In[127]:


import json

def load_data(title):
    with open(title, encoding="utf-8") as f:
        return json.load(f)


# In[125]:


save_data("disney_data_cleaned.json", movie_info_list)


# # Clean Our Data!

# In[32]:


movie_info_list = load_data("disney_data_cleaned.json")


# # Subtasks
#     - clean up references
#     - convert running time into an integer
#     - convert dates into datetime object
#     - split up long strings
#     - convert budeget and box office to numbers

# In[33]:


# Clean up references (remove [1])
# DONE


# In[34]:


# Split up long strings
#DONE


# In[35]:


# Convert running time into integer
#DONE


# In[36]:


# Convert budget and box office to numbers
# DONE


# In[37]:


# convert dates into datetime object


# In[ ]:





# In[38]:


movie_info_list[-25]


# In[39]:


print([movie.get('Running time', 'N/A') for movie in movie_info_list])


# In[40]:


# Convert running time into integer

def minutes_to_integer(running_time):
    if running_time == "N/A":
        return None
    if isinstance(running_time, list):
        entry = running_time[0]
        return int(running_time[0].split(" ")[0])
    else:
        return int(running_time.split(" ")[0])
    
for movie in movie_info_list:
    movie['Running time (int)'] = minutes_to_integer(movie.get('Running time', "N/A"))


# In[41]:


# Convert running time into integer
print([movie.get('Running time (int)', 'N/A') for movie in movie_info_list])


# In[42]:


# Convert budget and box office to numbers
print([movie.get('Budget', 'N/A') for movie in movie_info_list])


# In[43]:


# Convert running time into integer
import re

amounts = r"thousand|million|billion"
number = r"\d+(,\d{3})*\.*\d*"

word_re = rf"\${number}(-|\sto\s|–)?({number})?\s({amounts})"
value_re = rf"\${number}"


def word_to_value(word):
    value_dict = {"thousand": 1000, "million": 1000000, "billion": 1000000000}
    return value_dict[word]

def parse_word_syntax(string):
    value_string = re.search(number, string).group()
    value = float(value_string.replace(",", ""))
    word = re.search(amounts, string, flags=re.I).group().lower()
    word_value = word_to_value(word)
    return value*word_value

def parse_value_syntax(string):
    value_string = re.search(number, string).group()
    value = float(value_string.replace(",", ""))
    return value


def money_conversion(money):
    if money == "N/A":
        return None

    if isinstance(money, list):
        money = money[0]

    word_syntax = re.search(word_re, money, flags=re.I)
    value_syntax = re.search(value_re, money)

    if word_syntax:
        return parse_word_syntax(word_syntax.group())

    elif value_syntax:
        return parse_value_syntax(value_syntax.group())
    
    else:
        return None
        

print(money_conversion("$790 million"))


# In[44]:


# Convert running time into integer
for movie in movie_info_list:
    movie['Budget (float)'] = money_conversion(movie.get('Budget', "N/A"))
    movie['Box office (float)'] = money_conversion(movie.get('Box office', "N/A"))


# In[45]:


movie_info_list[-150]


# In[46]:


# Convert dates into times
print([movie.get('Release date', 'N/A') for movie in movie_info_list])


# In[47]:


# June 28, 1960


# In[48]:


# Convert dates into times
# to "June 28, 1960"

from datetime import datetime

dates = [movie.get('Release date', 'N/A') for movie in movie_info_list]

def clean_date(date):
    return date.split("(")[0].strip()

def date_conversion(date):
    if isinstance(date, list):
        date = date[0]
    
    if date == "N/A":
        return None
        
    date_str = clean_date(date)
    
    fmts = ["%B %d, %Y", "%d %B %Y"]
    for fmt in fmts:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            pass
    return None


# In[49]:


for movie in movie_info_list:
    movie['Release date (datetime)'] = date_conversion(movie.get('Release date', 'N/A'))


# In[50]:


movie_info_list[-25]


# In[55]:


import pickle

def save_data_pickle(name, data):
    with open(name, 'wb') as f:
        pickle.dump(data, f)


# In[56]:


import pickle

def load_data_pickle(name):
    with open(name, 'rb') as f:
        return pickle.load(f)


# In[57]:


save_data_pickle("disney_movie_data_cleaned_more.pickle", movie_info_list)


# In[60]:


load_data_pickle("disney_movie_data_cleaned_more.pickle")


# # Task 4: Attach IMDB/Rotten Tomatoes scores and Metascores

# In[61]:


movie_info_list = load_data_pickle("disney_movie_data_cleaned_more.pickle")


# In[62]:


movie_info_list[-60]


# In[ ]:


# http://www.omdbapi.com/?apikey=[690cbde]&


# In[67]:


import requests
import urllib
import os

def get_omdb_info(title):
    base_url = "http://www.omdbapi.com/?"
    parameters = {"apikey": '690cbde', 't': title}
    params_encoded = urllib.parse.urlencode(parameters)
    full_url = base_url + params_encoded
    return requests.get(full_url).json()

def get_rotten_tomatoes_score(omdb_info):
    ratings = omdb_info.get('Ratings', [])
    for rating in ratings:
        if rating['Source'] == 'Rotten Tomatoes':
            return rating['Value']
    return None


# In[75]:


for movie in movie_info_list:
    title = movie['title']
    omdb_info = get_omdb_info(title)
    movie['imdb'] = omdb_info.get('imdbRating', None)
    movie['metascore'] = omdb_info.get('Metascore', None)
    movie['rotten_tomatoes'] = get_rotten_tomatoes_score(omdb_info)


# In[77]:


movie_info_list[-55]


# In[78]:


save_data_pickle('disney_movie_data_final.pickle', movie_info_list)


# # Task 5: Save data as a JSON and CSV

# In[79]:


movie_info_list[-55]


# In[96]:


movie_info_copy = [movie.copy() for movie in movie_info_list]


# In[129]:


movie_info_copy[-55]


# In[114]:


for movie in movie_info_copy:
    current_date = movie['Release date (datetime)']
    if current_date:
        movie['Release date (datetime)'] = current_date.strftime("%B %d, %Y")
    else:
        movie['Release date (datetime)'] = None
    
        


# In[132]:


movie_info_copy[-55]


# In[136]:


save_data("disney_data_final.json", movie_info_copy)


# In[137]:


import pandas as pd

df = pd.DataFrame(movie_info_list)


# In[138]:


df.head()


# In[139]:


df.to_csv("disney_movie_data_final.csv")


# In[143]:


running_times = df.sort_values(['Running time (int)'], ascending=False)
running_times.head()


# In[1]:


pwd


# In[2]:


cd C:\Users\Jonshish\Desktop\Python Projects\Disney Movie Data List


# In[3]:


pwd


# In[ ]:




