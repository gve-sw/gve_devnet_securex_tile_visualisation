""" Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

# Import Section
from flask import Flask, render_template, request, url_for, redirect, session, jsonify
from collections import defaultdict
from datetime import datetime
import requests
import json
from dotenv import load_dotenv
import os
import pandas as pd
from urllib.parse import quote
from storage import save_data, load_data
#import merakiAPI

# load all environment variables
load_dotenv()


# Global variables
app = Flask(__name__)
dropdown_content = []

def load_client_credentials():
    with open('config.json', 'r') as f:
        data = json.load(f)
    return data['clients']

#Read data from json file
def getJson(filepath):
	with open(filepath, 'r') as f:
		json_content = json.loads(f.read())
		f.close()

	return json_content

#Write data to json file
def writeJson(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f)
    f.close()

def open_config():
    '''
    this function opens config.json
    '''
    if os.path.isfile("config.json"):
        global config_file
        with open("config.json", 'r') as config_file:
            config_file = json.loads(config_file.read())
            print("\nThe config.json file was loaded.\n")
    else:
        print("No config.json file, please make sure config.json file is in same directory.\n")

def load_last_selection():
    try:
        last_selection_data = getJson('last_selection.json')
        last_selection = last_selection_data.get('last_selection', None)
    except FileNotFoundError:
        last_selection = None
    return last_selection

def get_CTR_access_token(client_id, client_secret):
    ''' 
    This function requests access token for OAuth2 for other CTR API requests
    '''
    #error checking for API client details
    if not client_id or not client_secret:
        print("client id or secret is missing in config.json file...\n")
        
    # create headers for access token request
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
    }

    data = {
    'grant_type': 'client_credentials'
    }

    # create headers for access token request
    response = requests.post('https://visibility.amp.cisco.com/iroh/oauth2/token', headers=headers, data=data, auth=(client_id, client_secret))

    #check if request was succesful
    if response.status_code == 200:
        
        # grab the text from the request
        rsp_dict = json.loads(response.text)
        # retrieve variables from text, global variable so that it can be used by all functions for CTR
        access_token = (rsp_dict['access_token'])
        scope = (rsp_dict['scope'])
        expiration_time = (rsp_dict['expires_in'])     
        # user feedback
        # return token
        return access_token
    else:
        # user feedback
        print(f"Access token request failed, status code: {response.status_code}\n")   

def get_all_client_tiles():
    clients = load_client_credentials()
    all_client_tiles = {}

    for client in clients:
        access_token = get_CTR_access_token(client['client_id'], client['client_secret'])
        client_tiles = return_all_available_tiles(access_token)
        
        # Filter out modules with no associated tiles
        client_tiles = [module for module in client_tiles if module['tiles']]

        all_client_tiles[client['client_name']] = client_tiles

    return all_client_tiles


#ORIGINAL CODE 
# def return_all_available_tiles():
#     '''
#     this function returns all available tiles and modules for a SecureX org
#     '''
#     # create headers for API request
#     bearer_token = 'Bearer ' + _access_token()

#     headers = {
#         'Authorization': bearer_token,
#         'Content-Type':'application/json',
#         'Accept':'application/json'
#         }
    
#     response = requests.get('https://visibility.amp.cisco.com/iroh/iroh-dashboard/tiles', headers=headers)
#     return json.loads(response.text)

def return_all_available_tiles(access_token):
    # ... (keep the headers and API request part unchanged)
    bearer_token = 'Bearer ' + access_token

    headers = {
        'Authorization': bearer_token,
        'Content-Type':'application/json',
        'Accept':'application/json'
        }
    
    response = requests.get('https://visibility.amp.cisco.com/iroh/iroh-dashboard/tiles', headers=headers)

    if response.status_code == 200:
        returned_tiles = json.loads(response.text)
        seen = set()
        module_names = []

        for tile in returned_tiles['data']:
            if tile['module'] not in module_names:
                module_names.append(tile['module'])

        modules_and_tiles = []
        for module in module_names:
            module_tile_collection = []
            for tile in returned_tiles['data']:
                if tile['module'] == module and tile['title'] not in seen:
                    tile_name = {"tile": tile['title']}
                    tile_url = {"url": tile['data_url']}
                    tile_name.update(tile_url)
                    module_tile_collection.append(tile_name)
                    seen.add(tile['title'])
            modules_and_tiles.append({"module_name": module, "tiles": module_tile_collection})

        return modules_and_tiles
    else:
        # Handle errors or return an empty list if no tiles are available for the access token
        return []

# def build_page_data(access_token):
#     returned_tiles = return_all_available_tiles(access_token)
#     global dropdown_content 
#     module_names = []
#     seen = set()
#     temp_dict = {}
#     tile_collection = []
#     module_names = []
#          # loop through all modules to get an overview
#     for tile in returned_tiles['data']:
#         if tile['module'] not in module_names:
#             module_names.append(tile['module'])

#     print(f"All available modules:\n\n{module_names}\n")

#     for module in module_names:
#         #dropdown_content = {'module':module}
#         for tile in returned_tiles['data']:
#             if tile['module'] == module and tile['title'] not in seen:
#                 tile_name = {"tile":tile['title']}
#                 tile_url = {"url":tile['data_url']}
#                 tile_name.update(tile_url)
#                 tile_collection.append(tile_name)
#                 seen.add(tile['title'])
#         temp_dict = {
#             "modulename":module,
#             "tiles":tile_collection
#         }
        
#         if not module in dropdown_content:
#             dropdown_content.append(temp_dict.copy())
        
#         temp_dict.clear()
#         tile_collection = []
#     return dropdown_content

def return_data_from_tile(tile_info, data_period):
    '''
    this function returns all data from a tile for a specific perdiod
    '''
    client_name = tile_info['client']
    clients = load_client_credentials()

    for client in clients:
        if client['client_name'] == client_name:
            access_token = get_CTR_access_token(client['client_id'], client['client_secret'])
            # create headers for API request
            bearer_token = 'Bearer ' + access_token

            headers = {
                'Authorization': bearer_token,
                'Content-Type':'application/json',
                'Accept':'application/json'
                }

            concat_url = 'https://visibility.amp.cisco.com' + tile_info['url']
            params = {"period": data_period}
            
            # retrieve dispositions for observables
            response = requests.get(concat_url, headers=headers, params=params)
            return json.loads(response.text)

# def extract_data_entries(tile_response):
#     tile_data = {'multi_line':False, 'columns':False}
#     list_data = []
#     if 'multi_line' in tile_response['data']:
#         tile_data.update({
#                 "label1" : tile_response['data']['labels'][0],
#                 "label2" : tile_response['data']['labels'][1],
#                 "value1" : [],
#                 "value2" : [],
#                 "multi_line" : True
#             })

#         for entry in tile_response["data"]["data"]:
#             tile_data['value1'].append(entry["value"])
#             tile_data['value2'].append(entry["value2"])

#     elif not tile_response['data']['data']: 
#         print('hi')
#         for count, entry in enumerate(tile_response["data"]["data"]):
#             tile_data.update(
#                 {
#                     f"label{count+1}" : entry['label'],
#                     f"value{count+1}" : entry['value'],
#                     "value-unit" : entry['value-unit']
#                 }
#             )
#     else: 
#         #TODO: get data or info on rows as we have no data to see format
#         if 'columns' in tile_response['data']['data']:
#             tile_data.update({"columns" : True})

#             for count, column in enumerate(tile_response['data']['data']['columns']):
#                 tile_data.update(
#                     {
#                         f"label{count+1}" : column['label'],
#                         f"content_type{count+1}" : column['content_type'],
#                     }
#                 )
#             for count, row in enumerate(tile_response['data']['data']['rows']):
#                 tile_data.update(
#                     {
#                         f"value{count+1}" : row['value']
#                     }
#                 )
#         elif 'label' in tile_response['data']['data'][0]:
#             for count, entry in enumerate(tile_response["data"]["data"]):
#                 tile_data.update(
#                     {
#                         f"label{count+1}" : entry['label'],
#                         f"value{count+1}" : entry['value'],
#                         "value-unit" : entry['value-unit']
#                     }
#                 )
#         elif tile_response['data'].get('key_type') == 'timestamp':
#             #Corresponds to category tiles which are multi-line but data is not structured the same to other multi-line tiles as no label present
#             #TODO restructure the values into a list
#             tile_data.update(
#                 {
#                     "value1" : [],
#                     "timestamps": [],
#                     "single_line":True
#                 }
#             )
#             for count, entry in enumerate(tile_response["data"]["data"]):
#                 tile_data['value1'].append(entry["value"])
#                 tile_data['timestamps'].append(entry['key'])
#     return tile_data

def extract_data_entries(tile_response):
    tile_data = {'multi_line': False, 'columns': False}
    list_data = []

    if tile_response['data'] is None or tile_response['data']['data'] is None:
        return tile_data

    data_section = tile_response['data']

    if 'multi_line' in data_section:
        tile_data.update({
            "label1": data_section['labels'][0],
            "label2": data_section['labels'][1],
            "value1": [],
            "value2": [],
            "multi_line": True
        })

        for entry in data_section["data"]:
            tile_data['value1'].append(entry["value"])
            tile_data['value2'].append(entry["value2"])

    else:
        if 'columns' in data_section:
            tile_data.update({"columns": True})

            for count, column in enumerate(data_section['columns']):
                tile_data.update(
                    {
                        f"label{count + 1}": column['label'],
                        f"content_type{count + 1}": column['content_type'],
                    }
                )
            for count, row in enumerate(data_section['rows']):
                tile_data.update(
                    {
                        f"value{count + 1}": row['value']
                    }
                )
        elif len(data_section) > 0 and 'label' in list(data_section.values())[0]:
            for count, entry in enumerate(data_section):
                tile_data.update(
                    {
                        f"label{count + 1}": entry['label'],
                        f"value{count + 1}": entry['value'],
                        "value-unit": entry['value-unit']
                    }
                )
        elif data_section.get('key_type') == 'timestamp':
            tile_data.update(
                {
                    "value1": [],
                    "timestamps": [],
                    "single_line": True
                }
            )
            for count, entry in enumerate(data_section['data']):
                tile_data['value1'].append(entry["value"])
                tile_data['timestamps'].append(entry['key'])
    return tile_data




def extract_timestamps(tile_response):
    if tile_response["data"] is None:
        return {}
    
    start_time = tile_response["data"]["observed_time"]["start_time"]
    end_time = tile_response["data"]["observed_time"]["end_time"]
    period = tile_response["data"]["period"]
    
    n_days = period
    date_input_format = '%Y-%m-%dT%H:%M:%S.%fZ'
    data_output_format = '%Y-%m-%d'

    start_date_obj = datetime.strptime(start_time, date_input_format)
    start_time = start_date_obj.strftime(data_output_format)

    end_date_obj = datetime.strptime(end_time, date_input_format)
    end_time = end_date_obj.strftime(data_output_format)
    timestamp_freq = '1H'
    timestamps = []

    if period != 'last_24_hours':
        timestamp_freq = 'D'

    timestamp_range = pd.date_range(start=start_time,
                                end=end_time, freq=timestamp_freq)

    for i in timestamp_range:
        entry_timestamp = i.strftime(data_output_format)
        timestamps.append(entry_timestamp)

    return timestamps

##Routes
#Instructions
def reformat_timestamps(timestamps):
    formatted_dates = []
    for timestamp in timestamps:
        date = datetime.fromtimestamp(timestamp / 1000)
        formatted_date = date.strftime('%Y-%m-%d')
        formatted_dates.append(formatted_date)
    return formatted_dates

def create_tile_lookup(all_client_tiles):
    tile_lookup = {}
    for client, module_list in all_client_tiles.items():
        for module_dict in module_list:
            module_name = module_dict['module_name']
            for tile in module_dict['tiles']:
                key = (client, tile['tile'])
                tile_lookup[key] = {
                    'url': tile['url'],
                    'client': client,
                    'module': module_name
                }
    return tile_lookup

def load_and_display_charts(selected_items):
    all_client_tiles = get_all_client_tiles()
    tile_lookup = create_tile_lookup(all_client_tiles)
    selected_tiles_data = []

    for selected_item in selected_items:
        tile_lookup_key = (selected_item['client'], selected_item['tile'])
        if tile_lookup_key in tile_lookup:
            tile_info = tile_lookup[tile_lookup_key]
            selected_period = selected_item['period']
            tile_response = json.dumps(return_data_from_tile(tile_info, selected_period), indent=2)
            tile_data = extract_data_entries(json.loads(tile_response))
            if 'timestamps' not in tile_data:
                timestamps = extract_timestamps(json.loads(tile_response))
            else:
                timestamps = reformat_timestamps(tile_data['timestamps'])
            temp_dict = {
                'tile_data': tile_data,
                'timestamps': timestamps,
                'client': tile_info['client'],
            }
            temp_dict.update(selected_item)
            selected_tiles_data.append(temp_dict)

    return render_template('chartdisplay.html', selected_tiles_data=selected_tiles_data)


#Index
@app.route('/')
def index():
    try:
        return redirect(url_for('chartdisplay'))
    except Exception as e: 
        print(e)  
        #OR the following to show error message 
        return render_template('instructions.html', error=False, errormessage="CUSTOMIZE: Add custom message here.", errorcode=e)


# https://www.chartjs.org/docs/latest/charts/line.html
@app.route('/chartdisplay', methods=['GET', 'POST'])
def chartdisplay():
    if request.method == 'GET':
        last_selection = load_last_selection()
        if last_selection is not None:
            # Load the charts using the last selection
            return load_and_display_charts(last_selection)
        else:
            # Redirect to the config_selection page if there is no last selection
            return redirect(url_for('config_selection'))
    if request.method == 'POST':
        return render_template('tileSelection.html', hiddenLinks=False, dropdown_content = dropdown_content)

@app.route('/tileSelection', methods=['GET'])
def tileSelection():
    try:
        print("tileSelection() called")
        #open_config()
        clients = load_client_credentials()

        global dropdown_content
        selected_elements = {} 
        if not dropdown_content:
            all_client_tiles = get_all_client_tiles()
            #dropdown_content = build_page_data()

        if request.method == 'GET':
            all_client_tiles = get_all_client_tiles()
            return render_template('tileSelection.html', hiddenLinks=False, all_client_tiles=all_client_tiles, selected_elements = selected_elements)
       
    except Exception as e: 
        print(e)  
        return render_template('tileSelection.html', hiddenLinks=False, selected_elements = selected_elements, error=True, errormessage="CUSTOMIZE: Add custom message here.", errorcode=e)

@app.route('/config_selection', methods=['GET','POST'])
def config_selection():
    print("config_selection() called")
    if request.method == 'GET':
        saved_selections = load_data()
        return render_template('config_selection.html', saved_selections=saved_selections)
    if request.method == 'POST':
        print(request.form)
        selected_title = request.form.get('selection')
        saved_selections = load_data()
        selected_items = None
        print(f"Selected title: {selected_title}")
        print(f"Saved selections: {saved_selections}")  

        for selection in saved_selections:
            if selection['title'] == selected_title:
                selected_items = selection['items']
                break
        
        print(f"Selected items: {selected_items}")
        last_selection_data = {"last_selection": selected_items}
        writeJson('last_selection.json', last_selection_data)
    return load_and_display_charts(selected_items)

@app.route('/save_selections', methods=['GET', 'POST'])
def save_selections():
    if request.method == 'POST':
        json_data = json.loads(request.form.get('json_data'))
        title = json_data['title']
        print(title)
        items = json_data['items']
        print(items)
        creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        saved_selections = load_data()
        saved_selections.append({'title': title, 'items': items, 'creation_date': creation_date})
        save_data(saved_selections)
        return redirect(url_for("config_selection"))

@app.route('/save_last_selection', methods=['POST'])
def save_last_selection():
    last_selection = request.json['last_selection']
    with open('last_selection.json', 'w') as f:
        json.dump({"last_selection": last_selection}, f)
    return 'Saved'

if __name__ == "__main__":
    app.run(host='localhost', debug=True)
