import flask, requests
from flask import Flask, request
from bs4 import BeautifulSoup
app = flask.Flask(__name__)
app.config["DEBUG"] = True

#fucntion that displays detailed weather reports for each day
def weather_detail(c):
    #creation of table in html
    data = "Results: " + "<br> <table border='0'> "
    url = c
    #execute http request to get website url
    response = requests.get(url)
    #using BeautifulSoup to scrape the website
    soup = BeautifulSoup(response.content, "html.parser")
    #using BeautifulSoup to find the correct class which contains the data
    results = soup.find(class_="wr-day-carousel__list wr-js-day-carousel-list clearfix")
    weather_text = results.find_all("div", class_="wr-day__body")
    weather_text_elements = [
        a_element.parent for a_element in weather_text
    ]
    #looping through results to get day details
    for text in weather_text_elements:
        if weather_text_elements.index(text) == 0:
            a = text.find(class_="wr-date")
        else:
            a = text.find("span", class_="wr-date__longish")
        b = text.find("div",
                      class_="wr-day__weather-type-description wr-js-day-content-weather-type-description wr-day__content__weather-type-description--opaque")
        data = data + "<tr><td>" + a.text + "</td>"
        data = data + "<td>" + b.text + "</td></tr>"
    data = data + "</table>"
    #return formatted data
    return data

#route page to display search form
@app.route('/', methods=['GET'])
def home():
    return "<form action='./search/' method='get'><div><input type='text' name='s' maxLength='75' placeholder='Enter a town, city or UK postcode' autoComplete='off' spellcheck='false'/></div><input type='submit' value='Search' title='Search for a location'/></form>"

#function used to search and scrape the bbc weather page
@app.route('/search/', methods=['GET', 'POST'])
def search():
    #extract request variable from url
    result = request.args.get("s")
    #build bbc weather url and execute request
    url = "https://www.bbc.co.uk/weather/search?s="
    url = url + result
    response = requests.get(url)
    #using BeautifulSoup to scrape the website
    soup = BeautifulSoup(response.content, "html.parser")
    #using BeautifulSoup to find the correct class which contains the data
    results = soup.find("div", class_="location-search-results")
    location_elements = results.find_all("li", class_="location-search-results__result")
    my_counter = 0

    for location_element in location_elements:
        my_counter += 1
    #if one result returned call detailed weather for location
    if my_counter == 1:
        for location_element in location_elements:
            links = location_element.find_all("a")
            for link in links:
                link_url = link["href"]
                param = "https://www.bbc.co.uk/weather/" + str(link_url)
                data = weather_detail(param)
    #if more than one result returned a table of locations is returned fot the user to select
    else:
        data = "More than one entry exists please select one of the following <br><table border='0'>"
        for location_element in location_elements:
            links = location_element.find_all("a")
            for link in links:
                link_url = link["href"]
                link_name = link.text
                data = data + "<tr><td><a href='../searchdet/?s=" + str(link_url) + "'>" + str(link_name) + "</a></td></tr>"
        data = data + "</table>"
    return data

#function that is called after the user has chosen a location if there is multiple choices
@app.route('/searchdet/', methods=['GET', 'POST'])
def search_detail():
    result = request.args.get("s")
    url = "https://www.bbc.co.uk/weather/"
    param = url + result
    data = weather_detail(param)
    return data


app.run(host='0.0.0.0')
