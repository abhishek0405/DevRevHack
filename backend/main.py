import uvicorn
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from typing import List
import lancedb
import pyarrow as pa
import json
from collections import Counter

uri = "data/sample-lancedb"
db = lancedb.connect(uri)

class Review(BaseModel):
    id: str
    review: str
    source: str

app = FastAPI()
client = OpenAI(api_key="")
tbl = db.open_table("review_table")
filename = 'database.json'

class Review(BaseModel):
    id: str
    review: str
    source: str


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
    messages = [
        {"role": "system", "content": "I need you to do topic modelling for me. Given a review, you need to come up with a name of the cluster the review might belong to. Example, review: the payments gateway crashed right when I proceeded to checkout. Your cluster name could probably be 'Payments issues'. Just give the cluster name as the response."}
    ]
    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages= messages
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content


def confirm_cluster(prompt):
    messages = [
        {"role": "system", "content": "I need you to do topic modelling for me. Given a review and a cluster name, you need to say yes if the review can be put into the said cluster, otherwise say no. Example, 'review: the payments gateway crashed right when I proceeded to checkout. can this review be in the cluster: 'Payments issues'?'. Your answer would be 'Yes' in this case. Just give 'Yes' or 'No' as the response."}
    ]
    messages.append({"role": "user", "content": prompt})
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages= messages
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
    messages= messages
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
    messages= messages
    )

    print(completion.choices[0].message.content)
    return completion.choices[0].message.content

def get_embeddings(s):
    response = client.embeddings.create(
        input=s,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def add_new_vector(v, review_text, id):
    tbl.add([{ "vector": v, "review": review_text, "id": id}])

def query_results(query_embedding):
    results = tbl.search(query_embedding) \
    .metric("cosine") \
    .limit(5) \
    .to_list()
    print(results)
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
        return max_cluster[0][0]  # Return the cluster name with the highest count
    else:
        return None


@app.get("/")
async def index():
   return {"message": "Hello World"}

@app.post("/reviews/")
async def process_reviews(reviews_list: List[Review]):

    
    # get all current datapoints: read json once
    data = read_json(filename)

    for reviewOb in reviews_list:

        # check if review is not processed already
        if not check_if_processed(reviewOb.id, data):
            dataOb = {}
            # get the sentiment of the review
            sentiment = get_sentiment(reviewOb.review)

            # get the type: feature/issue/none
            review_type = get_type(reviewOb.review)


            # if type is a feature or an issue: go to next step
            if review_type in ['Feature', 'Issue']:


                # get embedding of the review
                    embedding = get_embeddings(reviewOb.review)
                    print(embedding)

                # get top 5 closest neighbours of the review from the db
                    closest_vectors = query_results(embedding)



                # if closest review is greater than 0.5, skip the next steps, directly go to new cluster step
                    if len(closest_vectors) != 0:
                        if closest_vectors[0]['_distance']  <= 0.5:
                            ids = []
                            for i in range(len(closest_vectors)):
                                ids.append(closest_vectors[i]['id'])
                            print(ids)

                            # get the 5 classes of these 5 reviews from the json

                            clusters = find_clusters_by_ids(ids, data)
                             # the maximum class would be the cluster of the new vector
                            max_cluster = find_max_occuring_cluster(clusters)
                            confirmation = confirm_cluster(reviewOb.review + '. Can this review be in the cluster: ' + max_cluster + ' ?')

                            if confirmation == 'Yes':
                                dataOb.cluster = max_cluster
                            else:
                                new_cluster_name = get_cluster(reviewOb.review)
                                dataOb.cluster = new_cluster_name
                        else:
                            new_cluster_name = get_cluster(reviewOb.review)
                            dataOb.cluster = new_cluster_name
                    else:
                        # if the closest review is also pre far, just get the cluster name for it
                        new_cluster_name = get_cluster(reviewOb.review)
                        dataOb.cluster = new_cluster_name

            # make an object with the id, review, sentiment, type, cluster name and append to the json data list
            dataOb.id = reviewOb.id
            dataOb.review = reviewOb.review
            dataOb.sentiment = sentiment
            dataOb.review_type = review_type
            dataOb.source = reviewOb.source

            data.append(dataOb)
            add_new_vector(embedding, reviewOb.review, reviewOb.id)

    # append the json data list to the file
    append_to_json(data, filename)

        
    return {"message": "Reviews processed successfully"}

if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)