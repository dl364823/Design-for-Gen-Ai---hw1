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
headline_data = {
  "headline":"",
  "summary":"",
  "keywords":[],
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



sample_headline_data_1 = {

    "headline": "See a new comet before it vanishes for 400 years",
    "summary": "CAPE CANAVERAL, Fla. (AP) — A newly discovered comet is swinging through our cosmic neighborhood for the first time in more than 400 years. Stargazers across the Northern Hemisphere should catch a glimpse as soon as possible — either this week or early next — because it will be another 400 years before the wandering ice ball returns. The comet, which is kilometer-sized (1/2-mile), will sweep safely past Earth on Sept. 12, passing within 78 million miles (125 million kilometers).",
    "keywords": [],
    "generations": [],
}



#### INIT with example data
headline_data = sample_headline_data_1





@app.route('/submit_headline', methods=['GET', 'POST'])
def submit_headline():
    global headline_data
    data = request.get_json()   

    headline_data["headline"] = data["headline"]
    headline_data["summary"] = data["summary"]

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




@app.route('/get_keywords', methods=['GET', 'POST'])
def get_keywords():
    global headline_data

    headline = headline_data["headline"]
    summary = headline_data["summary"]

    keywords = get_keywords_for_headline(headline, summary)
    headline_data["keywords"] = keywords 

    #send back the WHOLE array of data, so the client can redisplay it
    return jsonify(headline_data)


def parse_keywords_from_gpt_response(keyword_response):    
    keyword_list = keyword_response.splitlines()
    new_keyword_list = []
    for i, item in enumerate(keyword_list):
        item = item.strip()
        if item != "":
            item = item[item.index(".") + 1:]
            item = item.strip()
            new_keyword_list.append(item)
    return new_keyword_list


def get_keywords_for_headline(headline, summary):
    prompt = "Give me 10 keywords that represent this news headline and summary and format it like this: \n 1. keyword1 \n 2. keyword2 \n 3. keyword three. News headline: "+headline+". News summary: "+summary+"."
    print(prompt)


    response_raw = client.chat.completions.create(
      model="gpt-3.5-turbo",
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

    keyword_list = []
    try:
        keyword_list = parse_keywords_from_gpt_response(response)
    except:        
        print("ERROR: gpt keyword response won't parse")
        print(response)

    return keyword_list


@app.route('/')
def home():
    # you can pass in an existing article or a blank one.
    return render_template('home.html', data=headline_data)   


if __name__ == '__main__':
    # app.run(debug = True, port = 4000)    
    app.run(debug = True)




