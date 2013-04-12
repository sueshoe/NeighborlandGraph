import urllib
import matplotlib.pyplot as plt
from operator import itemgetter
import sys
import os


city_names = {'New Orleans': 'nola', 'San Francisco': 'sf', 'Austin': 'atx', 'Detroit': 'det',
              'St. Louis': 'stl', 'Kansas City': 'kansas-city',  'Boston': 'bos', 'Miami': 'miami',
              'Philadelphia': 'philly', 'Los Angeles': 'la', 'Seattle': 'sea'}

high_poverty = {'New Orleans', 'Detroit', 'St. Louis', 'Miami', 'Philadelphia'}
lower_poverty = {'Seattle', 'San Francisco', 'Austin', 'Kansas City', 'Boston'}

all_topics = {'animals', 'art', 'bikes', 'culture', 'economy', 'education', 'equity', 'food', 'government', 'green',
              'health', 'kids', 'public-space', 'recreation', 'safety', 'shopping', 'streets', 'tech', 'transit',
              'trees-gardens', 'urban-design', 'wayfinding'}

def read_pages(city):
    """ Given a city name, returns a set of all the idea ids from that city. """

    city_all_ids = set()
    for page_num in range(3):
        url = "https://neighborland.com/api/v1/cities/" + city + "/ideas?&page=" + str(page_num) + "&per_page=500"
        city_url = urllib.urlopen(url)
        city_url_str = city_url.read()
        if city_url_str!= '':
            city_ids = get_idea_ids(city_url_str, city)
            city_all_ids = city_all_ids | city_ids
    return city_all_ids

def get_idea_ids(city_url_str, city):
    """
    Given the contents of one page on the Neighborland API and a city,
    returns a set of idea ids. 
    """
    city_ids = set()
    #split city_url_str and add the deliminator back in 
    city_split = set(['"' + element for element in city_url_str.split('"')]) 
    for element in city_split:
        if '"' + city + '-' in element:
            city_ids.add(element.strip('"'))
    return city_ids

def map_topics_to_support_count(city_ids):
    """
    Given a set of id's, returns a dictionary of the topics from those id's mapped to
    the support count for each id. 
    """
    support_for_topics = {}
    for identification in city_ids:
        idea_url = 'https://neighborland.com/api/v1/ideas/' + identification
        idea = urllib.urlopen(idea_url).read()
        city_topics = extract_topics(idea)
        support_count = extract_support_count(idea)
        for topic in city_topics:
            if topic in support_for_topics:
                support_for_topics[topic] = support_for_topics[topic] + support_count
            else:
                support_for_topics[topic] = support_count
    return support_for_topics
        
def extract_topics(idea):
    idea_split = set(idea.split('"'))
    city_topics = idea_split & all_topics
    return city_topics

def extract_support_count(idea):
    idea_split = set(idea.split(','))
    for element in idea_split:
        if '"support_count":' in element:
            count = element.strip('"support_count":')
            num = int(count)
            return num
    return 0

def convert_to_percentages(support_for_topics):
    total = (sum(support_for_topics.values()))
    for key in support_for_topics:
        support_for_topics[key] = (support_for_topics[key]/float(total))*100
    return support_for_topics
              
def plot_topics_and_support_count(support_for_topics, city):
    """
    Given a dictionary, plots a horizontal bar chart with the dictionary values
    as the width, and the keys as the bar labels.
    """
    topics_list = [(key, value) for (key, value) in support_for_topics.items()]
    sorted_by_support = sorted(topics_list, key=itemgetter(1))

    i = 1.5
    counts = []
    for topic in sorted_by_support:
        plt.barh(i, topic[1], height = 1, color = '#68db54', edgecolor = 'w')
        counts.append(i + .5)
        i += 1.5
    ticks = [topic[0].title().replace('-', ' ') for topic in sorted_by_support]
    plt.yticks(counts, ticks)
    plt.title('Support by Topic in ' + city)
    plt.show()
    plt.clf()

def generate_all_cities(cities):
    """
    Given a list of cities, returns a dictionary of topics mapped to the support
    count in all the cities. 
    """
    all_cities = {}
    for city in cities:
        city_id = read_pages(city_names[city])
        city_dict = map_topics_to_support_count(city_id)
        city_dict_percentages = convert_to_percentages(city_dict)
        for topic in city_dict_percentages:
            all_cities[topic] = all_cities.setdefault(topic, 0) + city_dict_percentages[topic]
    return all_cities

def pivot_nested_dict(nested_dict):
    """Pivots a nested dictionary"""
    
    outside = dict()
    setkeys = set()

    # assign keys for new outside dictionary to empty nested dictionaries
    for key in nested_dict.values(): 
        for inner_key in key.keys(): 
            setkeys.add(inner_key)
    for x in setkeys:
        outside[x] = {}

    # Iterate over outer keys and assign values to nested dictionary    
    for input_key in nested_dict: # input_key is a,b
        for output_key in outside: #x,y,z
            if output_key in nested_dict[input_key]:
                outside[output_key][input_key] = nested_dict[input_key][output_key]
            else:
                del output_key
    return outside    

colors = {'High Poverty': '#68db54', 'Low Poverty': '#6666FF'}

def plot_all_cities_stacked_bar(all_cities):
    """
    Given a dictionary with nested dictionaries, plots the keys of the outer dictionary
    as bars and the values of the inner dictionaries as segments of those bars. The plot is
    titled "Support for All Topics in All Cities".
    
    """
    left = 1.5
    bottom = 0
    counts = []
    for topic in all_cities:
        last = 0
        for poverty_level in all_cities[topic]:
            count = all_cities[topic][poverty_level]
            #only create labels for legend once
            if left == 1.5:
                plt.bar(left, count, width = 1, color = colors[poverty_level], bottom = last, edgecolor = 'w', label = poverty_level)
            else:
                plt.bar(left = left, height = count, width = 1, bottom = last, color = colors[poverty_level], edgecolor = 'w')
            last += count
        counts.append(left + .5)
        left += 1.5
    ticks = [topic.title().replace('-',' ') for topic in all_cities.keys()]
    plt.xticks(counts, ticks, rotation = -90)
    plt.title('Support for All Topics in Cities with High Poverty and Low Poverty')
    plt.ylabel('Percentage of Support')
    plt.legend()
    plt.show()
    plt.clf()

#def calculate_variance(topic_dict):
    """
    for topic in topic_dict:
        all_counts = topic_dict[topic].values()
        mean = sum(all_counts)/len(all_counts)
        for count in all_counts:
            diff = (count - mean)**2 
    """
    
def main(city):
    """
    This program takes the name of one of the following cities:
    New Orleans, Detroit, St. Louis, Miami, Philadelphia, Seattle, San Francisco,
    Austin, Kansas City, Boston. The program pulls data from the Neighborland.com API and
    looks at all the ideas proposed, their tags (or 'topics') and the amount
    of support each ideas has gotten. The program outputs a bar chart of topics and the
    percentage of idea supported that are related to that topic.
    It also shows a stacked bar graph of the support for different topics in all cities
    with a high poverty level (above 20 %) and low poverty level.
    """

#read user inputed city
input_city = raw_input("Enter one of the following cities: New Orleans, Detroit, St. Louis, " +
                 "Miami, Philadelphia, Seattle, San Francisco, Austin, Kansas City or, Boston.")
city = city_names[input_city]   
city_all = read_pages(city)

support_topics = map_topics_to_support_count(city_all)
support_for_topics = convert_to_percentages(support_topics)

#plot individual city
plot_topics_and_support_count(support_for_topics, input_city)

print "Cities with a poverty level > 20%: ", high_poverty
print "Cities with a poverty level < 20%: ", lower_poverty

#get data for all cities, organize by poverty level
high_poverty_cities = generate_all_cities(high_poverty)
low_poverty_cities = generate_all_cities(lower_poverty)

all_cities = {}
all_cities['High Poverty'] = high_poverty_cities
all_cities['Low Poverty'] = low_poverty_cities
by_topic = pivot_nested_dict(all_cities)


plot_all_cities_stacked_bar(by_topic)

if __name__ == "__main__":
    main()
        
        
