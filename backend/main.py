import uvicorn
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel
from typing import List
import lancedb
import pyarrow as pa
import json
from collections import Counter
import requests
from dotenv import load_dotenv
import os
# lance db uri
uri = "data/sample-lancedb"
db = lancedb.connect(uri)


class Review(BaseModel):
    id: str
    review: str
    source: str


class ServerResponse(BaseModel):
    id: str
    source: str
    tagId: str
    type: str


app = FastAPI()
load_dotenv()

# Accessing environment variables
devrev_token = os.getenv("DEVREV_TOKEN")
api_key = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=api_key)
tbl = db.open_table("review_table")
filename = 'database.json'
devrevApiUrl = "https://api.devrev.ai/"

headers = {
    "User-Agent": "MyApp/1.0",
    "Authorization": devrev_token
}


def read_json(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    return data


def write_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def append_to_json(data, filename):
    write_json(data, filename)
    print("Data appended successfully.")


def get_cluster(prompt):

    # messages = [
    #     {"role": "system", "content": "Given a customer review, you need to do topic modelling based on the review and predict its cluster name, which should be short and broad.The topic name should not exceed 2 words. Examples of cluster names include 'Payments issues', 'Delivery issues', 'UI issues', etc. Ensure that related issues, such as 'payment gateway issue' and 'slow payments', fall under the same cluster name for cohesion."}
    # ]

    messages = [
        {"role": "system", "content": "I need you to do topic modelling for me. Given a review, you need to come up with a name of the cluster the review might belong to. Example, review: the payments gateway crashed right when I proceeded to checkout. Your cluster name could probably be 'Payments'. Just give the cluster name as the response. I want you to keep each topic name just 1 word so that similar issues can be clubbed together.Eg: Payments/Performance/UI/Pricing etc"}
    ]
    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def confirm_cluster(prompt):
    messages = [
        {"role": "system", "content": "I need you to do topic modelling for me. Given a review and a cluster name, you need to say yes if the review can be put into the said cluster, otherwise say no. Example, 'review: the payments gateway crashed right when I proceeded to checkout. can this review be in the cluster: 'Payments issues'?'. Your answer would be 'Yes' in this case. Just give 'Yes' or 'No' as the response.Think carefully before responding, even if there is some logical relation between the review received with the cluster name given, then say 'Yes'.Try your best always to give 'Yes', only if there is no corelation at all, then say no."}
    ]
    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def get_sentiment(prompt):
    messages = [
        {"role": "system", "content": "I need you to classify a review into any of these three classes: Positive, Negative or Neutral. Example, review: 'I had a terribly good delivery experience'. Your classification would be 'Positive'. Example, review: 'An item was missing in the delivery but I could not even reach the customer support to get it resolved!'. Your classification would be 'Negative'. Just give the class name as the response."}
    ]
    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def get_type(prompt):
    messages = [
        {"role": "system", "content": "I need you to classify a review into any of the three classes: Feature, Issue or None. Example, review: 'the payments gateway crashed right when I proceeded to checkout.' You should classify it into 'Issue'. Example, review: 'It was a good experience overall but it would have been better to have a share basket option provided, really convenient.'. You should classify it as 'Feature' as the user is requesting for a new feature. Just give any of three classes above as the response."}
    ]
    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def get_title(prompt):
    messages = [
        {"role": "system", "content": "I need you to return an appropriate title to a review that I would give you. The title should be short, crisp and should be relevant to the review body. It should highlight in brief what the review is about. Example: I have a recurring issue with payments, I can't go to the payments page after checkout, it just crashes all the time!. Your response might be 'Payment page crash'.Just return the title in your response - not more than 5 words."}
    ]
    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def get_answer(query):

    query_embedding = get_embeddings(query)
    closest_vectors = query_results(query_embedding)
    prompt = "Question: " + query + ". Data: "

    for i in range(len(closest_vectors)):
        print(closest_vectors[i]['review'])
        prompt += closest_vectors[i]['review']


    messages = [
        {"role": "system", "content": """I need you to answer a question based on the data that I will provide. You just need to frame an answer with the data provided to you. The answer should be crisp and relevant to the question asked. Example: Question: What are the top issues or complaints that the users reported? Data: I'm impressed by the customer service of this app. Had an issue with an order, and they resolved it promptly and courteously. Great job in prioritizing customer satisfaction!, The app frequently freezes and crashes, especially when browsing through categories or adding items to the cart. Makes the shopping experience frustrating and time-consuming., The app's interface is cluttered and confusing. It's hard to find items quickly, and sometimes the search function doesn't work properly. Definitely needs a redesign., Extremely disappointed with the delivery service. I've had multiple instances where my groceries arrived late, and some items were missing. Needs improvement., Disappointed with the freshness of the produce received. Some items were already nearing expiration, which is unacceptable. Need to work on sourcing fresher products. Your answer should be along the lines of Users reported dissatisfaction with:
Delivery service: Late deliveries and missing items.
App performance: Frequent freezes and crashes, especially during browsing.
Interface usability: Cluttered and confusing interface, unreliable search function.
Product quality: Received produce nearing expiration... you could make the summary more crisp - like bullet points. Keep in mind that you need to summarize it, not just list out the problems as they are."""}
    ]
    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return completion.choices[0].message.content

def get_embeddings(s):
    response = client.embeddings.create(
        input=s,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding


def add_new_vector(v, review_text, id):
    tbl.add([{"vector": v, "review": review_text, "id": id}])


def query_results(query_embedding):
    results = tbl.search(query_embedding) \
        .metric("cosine") \
        .limit(5) \
        .to_list()
    # print(results)
    return results


def check_if_processed(id_to_check, review_list):
    for review in review_list:
        if review['id'] == id_to_check:
            return True
    return False


def find_clusters_by_ids(id_list, dict_list):
    clusters = []
    for item in dict_list:
        if item['id'] in id_list:
            clusters.append(item['cluster'])
    return clusters


def find_max_occuring_cluster(cluster_list):
    cluster_counts = Counter(cluster_list)
    max_cluster = cluster_counts.most_common(1)
    if max_cluster:
        # Return the cluster name with the highest count
        return max_cluster[0][0]
    else:
        return None


def fetchTagFromClusterName(clusterName):
    try:
        tagsFetchUrl = devrevApiUrl + "tags.list?name=" + clusterName
        tagsResponse = requests.get(tagsFetchUrl, headers=headers)
        tagsResponse.raise_for_status()  # Raise an exception for 4xx or 5xx errors
        print("tags get response")
        tagsRes = tagsResponse.json()
        if (len(tagsRes["tags"]) == 0):
            tagsPostUrl = devrevApiUrl + "" + "tags.create"
            json_body = {
                "name": clusterName
            }
            createTagRes = requests.post(
                tagsPostUrl, json=json_body, headers=headers)
            createTagRes.raise_for_status()  # Raise an exception for 4xx or 5xx errors
            return createTagRes.json()['tag']['id']
        else:
            return tagsResponse.json()['tags'][0]['id']
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def index():
    return {"message": "Hello World"}


@app.get("/insights")
async def insights(query: str):
    response = get_answer(query)
    return {"response": response}


@app.post("/reviews/")
async def process_reviews(reviews_list: List[Review]):
    threshold = 0.5
    response_list = []

    # get all current datapoints: read json once
    data = read_json(filename)
    print("data is", data)
    for reviewOb in reviews_list:

        # check if review is not processed already
        if not check_if_processed(reviewOb.id, data):
            dataOb = {}
            response = {}
            # get title of the review
            title = get_title(reviewOb.review)

            # get the sentiment of the review
            sentiment = get_sentiment(reviewOb.review)

            # get the type: feature/issue/none
            review_type = get_type(reviewOb.review)

            # if type is a feature or an issue: go to next step
            if review_type in ['Feature', 'Issue']:

                # get embedding of the review
                embedding = get_embeddings(reviewOb.review)

                # get top 5 closest neighbours of the review from the db
                closest_vectors = query_results(embedding)
                # print("closest vectors",closest_vectors)
                filtered_vectors = [
                    obj for obj in closest_vectors if obj['_distance'] < threshold]

                # if closest review is greater than 0.5, skip the next steps, directly go to new cluster step
                if len(filtered_vectors) != 0:
                    print(filtered_vectors[0]['_distance'])
                    ids = []
                    for i in range(len(filtered_vectors)):
                        ids.append(filtered_vectors[i]['id'])
                    print(ids)

                    # get the 5 classes of these 5 reviews from the json

                    clusters = find_clusters_by_ids(ids, data)
                    # the maximum class would be the cluster of the new vector
                    max_cluster = find_max_occuring_cluster(clusters)
                    # confirmation = confirm_cluster(reviewOb.review + '. Can this review be in the cluster: ' + max_cluster + ' ?')

                    # if confirmation == 'Yes':
                    dataOb['cluster'] = max_cluster
                    # else:
                    #     new_cluster_name = get_cluster(reviewOb.review)
                    #     dataOb['cluster'] = new_cluster_name

                else:
                    # if the closest review is also pre far, just get the cluster name for it
                    new_cluster_name = get_cluster(reviewOb.review)
                    dataOb['cluster'] = new_cluster_name

            # make an object with the id, review, sentiment, type, cluster name and append to the json data list
            dataOb['id'] = reviewOb.id
            dataOb['review'] = reviewOb.review
            dataOb['sentiment'] = sentiment
            dataOb['review_type'] = review_type
            dataOb['source'] = reviewOb.source
            dataOb['title'] = title

            data.append(dataOb)
            if review_type != 'None':
                add_new_vector(embedding, reviewOb.review, reviewOb.id)
            else:
                dataOb['cluster'] = "Miscellaneous"

            response['id'] = dataOb['id']
            response['source'] = dataOb['source']
            response['tagId'] = ""
            if review_type != 'None':
                response['tagId'] = fetchTagFromClusterName(dataOb['cluster'])
            response['type'] = dataOb['review_type']
            print("sending out response", response)
            response_list.append(response)

    # append the json data list to the file
    append_to_json(data, filename)
    return response_list

    # return {"message": "Reviews processed successfully"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
