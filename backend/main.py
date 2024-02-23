import uvicorn
from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from typing import List
import lancedb
import pyarrow as pa
import json

uri = "data/sample-lancedb"
db = lancedb.connect(uri)



app = FastAPI()
client = OpenAI(api_key="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")
tbl = db.open_table("my_table")


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
    current_data = read_json(filename)
    current_data.append(data)
    write_json(current_data, filename)
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


def get_embeddings(s):
    response = client.embeddings.create(
        input=s,
        model="text-embedding-3-large"
    )
    return response.data[0].embedding

def add_new_vector(v, review_text):
    tbl.add([v, review_text])

def query_results(query):
    query_embedding = get_embeddings(query)
    results = tbl.search(query_embedding) \
    .metric("cosine") \
    .limit(5) \
    .to_list()
    return results


@app.get("/")
async def index():
   return {"message": "Hello World"}

@app.post("/reviews/")
async def process_reviews(reviews_list: List[Review]):
    for reviewOb in reviews_list:
        embedding = get_embeddings(reviewOb.review)
        closest_vectors = query_results(reviewOb.review)
        print(closest_vectors)
        #add_new_vector(embedding, reviewOb.review, reviewOb.source, "Payments issues", reviewOb.id)
        #await asyncio.sleep(1)
    return {"message": "Reviews processed successfully"}

if __name__ == "__main__":
   uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)