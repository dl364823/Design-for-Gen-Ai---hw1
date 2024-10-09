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



#This is the basic data representation
description_data = {
  "prompt1": "",
  "prompt2": "",
  "prompt3": "",
  "prompt4": "",
  "names": [],
  "generations": []
}

sample_description_data_1 = {
    "prompt1": "simplicity, speed, innovation...",
    "prompt2": "young people, professionals, families...",
    "prompt3": "reliability, stylishness, technological edge...",
    "prompt4": "short and simple, creative and unique, tech-oriented...",
    "names": [],
    "generations": [],
}


#### INIT with example data
description_data = sample_description_data_1

@app.route('/submit_prompts', methods=['GET', 'POST'])
def submit_prompts():
    global description_data
    data = request.get_json()   

    description_data["prompt1"] = data.get("prompt1", "")
    description_data["prompt2"] = data.get("prompt2", "")
    description_data["prompt3"] = data.get("prompt3", "")
    description_data["prompt4"] = data.get("prompt4", "")
    #description_data["keywords"] = data["keywords", ""]

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify(description_data)

@app.route('/get_names', methods=['GET', 'POST'])
def get_names():
    print("Received request for /get_names")
    global description_data
    prompt1 = description_data.get("prompt1", "")
    prompt2 = description_data.get("prompt2", "")
    prompt3 = description_data.get("prompt3", "")
    prompt4 = description_data.get("prompt4", "")
    description = f"{prompt1} {prompt2} {prompt3} {prompt4}"

    names = get_names_for_product(description)
    description_data["names"] = names

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify(description_data)


def parse_names_from_gpt_response(name_response):
    name_list = name_response.splitlines()
    new_name_list = []
    for i, item in enumerate(name_list): 
        item = item.strip()
        if item != "":
            item = item[item.index(".") + 1:]
            item = item.strip()
            new_name_list.append(item)
    return new_name_list


def get_names_for_product(description):
    prompt = (
        f"Give me 5 product names that represent the following description. "
        f"Format it like this: \n 1. name1 \n 2. name2 \n 3. name three.\n"
        f"Product description: {description}."
    )
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
      max_tokens=256,
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

@app.route('/store_selected_name', methods=['POST'])
def store_selected_name():
    global description_data
    data = request.get_json()
    selected_name = data.get("selected_name", "No Name Selected")
    description_data["selected_name"] = selected_name
    print(f"Stored selected_name: {selected_name}")
    return jsonify({"message": "success"})

@app.route('/image_prompts')
def image_prompts():
    selected_name = description_data.get('selected_name', 'No Name Selected')  
    return render_template('image_prompts.html', selected_name=selected_name)


@app.route('/generate_logos', methods=['POST'])
def generate_logos():
    global description_data
    data = request.get_json()  
    print("Received data for logo generation:", data) 
    # print(data)
    selected_name = data.get("selected_name")
    description_data["selected_name"] = selected_name
    image_prompt1 = data.get("image_prompt1")
    image_prompt2 = data.get("image_prompt2")
    image_prompt3 = data.get("image_prompt3")
    image_prompt4 = data.get("image_prompt4")
    logo_count = int(data.get("logo_count", 1))
    
    final_prompt = f"Create a logo for the product '{selected_name}'. "
    final_prompt += f"Image details: {image_prompt1}, {image_prompt2}, {image_prompt3}, {image_prompt4}."

    logos = generate_images_for_logo(final_prompt, logo_count)
    description_data["generations"] = logos
    #just send new images
    return jsonify(logos)


def generate_images_for_logo(prompt, count):
    images = []
    for i in range(count):
        response_image = client.images.generate(
        prompt=prompt,
        n=1,
        size="512x512",
        )

        url = response_image.data[0].url
        images.append({"prompt": prompt, "url": url})

    return images

@app.route('/view_logos')
def view_logos():
    global description_data  
    selected_name =  description_data.get("selected_name", "Unknown Product")
    logos = description_data.get("generations", [])
    print(f"Selected name in view_logos: {selected_name}")
    return render_template('view_logos.html', logos=logos, selected_name=selected_name)


@app.route('/')
def home():
    # you can pass in an existing article or a blank one.
    return render_template('home.html', data=description_data)


if __name__ == '__main__':
    # app.run(debug = True, port = 4000)    
    app.run(debug = True)




