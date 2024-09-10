from flask import Flask
from flask import render_template
from flask import Response, request, jsonify
app = Flask(__name__)

#for gpt
import os
from openai import OpenAI

import openai_secrets

client = OpenAI(api_key=openai_secrets.SECRET_KEY)

# client = OpenAI(
#   organization='org-KcC98ej4Dhc4OJy3ncs75U3T',
#   project='$PROJECT_ID',
# )



#for dalle
import json
from base64 import b64decode
from pathlib import Path



#Thid is the basic data representation
description_data = {
  "description":"",
  "seedwords":"",
  "names":[],
  "generations":[]
}

# This is what the representation looks like when there are keywords and images generated
# sample_headline_data_2 = {
#    "generations": [
#       {
#          "prompt": "Santos’s Lies Were Known to Some Well-Connected Republicans",
#          "url": "static/generated_images/Santo-1673801357/Santo-1673801357-0.png"
#       },
#       {
#          "prompt": "Santos’s Lies Were Known to Some Well-Connected Republicans",
#          "url": "static/generated_images/Santo-1673801375/Santo-1673801375-0.png"
#       }
#    ],
#    "headline": "Santos’s Lies Were Known to Some Well-Connected Republicans",
#    "keywords": [
#       "Santos",
#       "Lying",
#       "Republican",
#       "2022",
#       "Suspicion",
#       "Campaign",
#       "Upperechelons",
#       "Republicans",
#       "Turned a Blind Eye",
#       "Connection"
#    ],
#    "summary": "George Santos inspired no shortage of suspicion during his 2022 campaign, including in the upper echelons of his own party, yet many Republicans looked the other way."
# }



sample_description_data_1 = {
    "description": "A home milkshake maker",
    "seedwords": "fast, healthy, compact.",
    "names": [],
    "generations": [],
}


#### INIT with example data
description_data = sample_description_data_1





@app.route('/submit_description', methods=['GET', 'POST'])
def submit_description():
    global description_data
    data = request.get_json()   

    description_data["description"] = data["description"]
    description_data["seedwords"] = data["seedwords"]

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify(headline_data)


@app.route('/get_images', methods=['GET', 'POST'])
def get_images():
    global headline_data
    data = request.get_json()   
    # print(data)
    prompt = data["prompt"]
    new_images = generate_images(prompt)

    for i in new_images:
        headline_data["generations"].append(i) 

    #just send new images
    return jsonify(new_images)


def generate_images(prompt):
    response_image = client.images.generate(
      prompt=prompt,
      n=1,
      size="256x256",
    )

    url = response_image.data[0].url

    images = [
        {
            "prompt": prompt,
            "url": url, #image_file.as_posix(),
        }
    ]
    # print(url_for_flask)
    return images




@app.route('/get_names', methods=['GET', 'POST'])
def get_names():
    global description_data

    description = description_data["description"]
    seedwords = headline_data["seedwords"]

    names = get_keywords_for_product(description, seedwords)
    description_data["names"] = names

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify(description_data)


def parse_names_from_gpt_response(name_response):
    name_list = name_response.splitlines()
    new_name_list = []
    for i, item in enumerate(keyword_list):
        item = item.strip()
        if item != "":
            item = item[item.index(".") + 1:]
            item = item.strip()
            new_name_list.append(item)
    return new_name_list


def get_names_for_product(description, seedwords):
    prompt = "Give me 10 product names that represent the description and seedwords. and format it like this: \n 1. name1 \n 2.name2 \n 3. name three. Product description: "+description+". Product seedwords: "+seedwords+"."
    print(prompt)


    response_raw = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {
          "role": "user",
          "content": prompt
        }
      ],
      # temperature=0,
      max_tokens=100,
      # top_p=1,
      # frequency_penalty=0,
      # presence_penalty=0
    )

    response = response_raw.choices[0].message.content  

    print(response)

    name_list = []
    try:
        name_list = parse_names_from_gpt_response(response)
    except:        
        print("ERROR: gpt name response won't parse")
        print(response)

    return name_list


@app.route('/')
def home():
    # you can pass in an existing article or a blank one.
    return render_template('home.html', data=description_data)


if __name__ == '__main__':
    # app.run(debug = True, port = 4000)    
    app.run(debug = True)




