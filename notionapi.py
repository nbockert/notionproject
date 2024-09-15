import pandas as pd
from mapbox import Directions
import requests
import random


from datetime import datetime, timedelta
#!pip install notion-client
#from notion_client import Client

import pytz


dt = datetime(2024, 1, 24, tzinfo=pytz.UTC)

MAPBOX_API_TOKEN = "MAPBOX_API"
secret_token = 'secret'
NOTION_API_TOKEN  = "NOTION"



fp = "/content/Schedule_datasource.xlsx"
df = pd.read_excel(fp)

class home:
  latitude = 42.343300
  longitude = -71.115640

def get_day():
  #now = datetime.now()
  day = dt.weekday()
  week_day = ["Monday","Tuesday","Wednesday","Thursday","Friday","It's the weekend, relax"]
  if day>4:
    return week_day[5]
  else:
    return week_day[day]
def get_time():
  now = datetime.now()
  time = now.time()
  return time




def map(df):
  directions = Directions(access_token=MAPBOX_API_TOKEN,host=None, cache=None)
  time = get_time()

  current_day = get_day()
  if current_day == "It's the weekend, relax":
    return current_day
  if current_day in ["Monday","Wednesday","Friday"]:
    current_day = 'Monday, Wednesday, Friday'
  elif current_day in ['Tuesday', 'Thursday']:
    current_day = 'Tuesday, Thursday'
  dfa = df[df["Day"]==current_day]
  string = ""

  for index, row in dfa.iterrows():
    features = [
    {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Point",
            "coordinates": [home.longitude,home.latitude]  # Waypoint 1
        }
    },
    {
        "type": "Feature",
        "properties": {},
        "geometry": {
            "type": "Point",
            "coordinates": [row['Longitude'], row['Latitude']]  # Waypoint 2
        }
    },
  ]


    response = directions.directions(features=features,
      coordinates=[],
      profile='mapbox/walking',
      language='en',
      steps=True,
      alternatives=False
    )
    routes = response.json()['routes']
    if routes:
      distance_meters = routes[0]['distance']
      distance_mile = round(distance_meters/1609.34,2)

      travel_time_seconds = routes[0]['duration']
      travel_time_minutes = travel_time_seconds // 60
      original_time = datetime.combine(dt, row["Start"])
      minutes_to_subtract = timedelta(minutes=travel_time_minutes)
      leave = original_time - minutes_to_subtract
      format_leave = leave.strftime("%H:%M")

      classname = row["Class Name"]

      string += f"{classname}:\n"
      string += "Travel Time: " + str(travel_time_minutes) + " minutes from home\n"
      string += "Leave for class at: " + str(format_leave) + "\n"
      string += "Distance: " + str(distance_mile) + " miles\n"
      string += "\n"
    else:
      print("No routes found")
  return string




def to_notion(string):
  database_id = "database"

  headers = {
      'Authorization': 'Bearer '+ NOTION_API_TOKEN,
      'Content-Type': 'application/json',
      "Notion-Version": "2022-06-28"
  }
  colors = ["blue","blue_background","green","green_background","orange","pink","pink_background","purple","purple_background"]
  color = random.choice(colors)


  #set data to schema with same properties as block data structure
  #data contains the text we want to add in json format
  data = {
	    "children": [
		  {
			  "object": "block",
			  "type": "heading_2",
			  "heading_2": {
				"rich_text": [{ "type": "text",
                   "text": {
                       "content": "Class Reminders:"
                       },
                   "annotations": {
                      "bold": False,
                      "italic": True,
                      "strikethrough": False,
                      "underline": False,
                      "code": False,
                      "color": color
                      },
                    }]
			}
		},
		{
			"object": "block",
			"type": "paragraph",
			"paragraph": {
				"rich_text": [
					{
						"type": "text",
						"text": {
							"content": string
						}
					}
				],
			}
		}
	],
}




  #url set to interact with notion api/version/datastructure we want to add/place where we want to put it/children because we want to append it to a child block
  url = f"https://api.notion.com/v1/blocks/{database_id}/children"
  #communicate to api - patch lets you insert into notion - params are url, the data we want to add in JSON format and headers with all of api access info
  response = requests.patch(url,json=data,headers=headers)
  print(response.status_code)
  if response.status_code == 200:
      print("Text block added successfully")
      #response_content = response.json()
      #print("Response Content:", response_content)
  else:
      print("Error:", response.text)


note = map(df)
to_notion(note)
