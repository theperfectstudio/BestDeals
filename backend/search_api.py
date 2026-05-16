from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import json
import os
import requests

# =====================================================
# APP
# =====================================================

app = FastAPI()

# =====================================================
# CORS
# =====================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

# =====================================================
# EARNKARO TOKEN
# =====================================================

EARNKARO_TOKEN = "YOUR_EARNKARO_JWT_TOKEN"

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(__file__)

ROOT_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..")
)

DEALS_FILE = os.path.join(
    ROOT_DIR,
    "deals.json"
)

# =====================================================
# LOAD DEALS
# =====================================================

def load_deals():

    try:

        with open(
            DEALS_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return []

# =====================================================
# HOME
# =====================================================

@app.get("/")

def home():

    return {
        "status":"running"
    }

# =====================================================
# SEARCH
# =====================================================

@app.get("/search")

def search(q:str=""):

    deals = load_deals()

    if not q:

        return deals[:50]

    query = q.lower()

    results = []

    for deal in deals:

        title = deal.get(
            "title",
            ""
        ).lower()

        caption = deal.get(
            "caption",
            ""
        ).lower()

        if (

            query in title

            or

            query in caption

        ):

            results.append(deal)

    return results

# =====================================================
# EARNKARO CONVERT
# =====================================================

@app.get("/convert")

def convert(url:str):

    try:

        response = requests.post(

            "https://webapi.earnkaro.com/api/affiliate/link-converter",

            headers={

                "Authorization":
                f"Bearer {EARNKARO_TOKEN}",

                "Content-Type":
                "application/json"
            },

            json={
                "url":url
            },

            timeout=20
        )

        data = response.json()

        print(data)

        if(

            "data" in data

            and

            "shortUrl" in data["data"]

        ):

            return {

                "success":True,

                "affiliate_url":
                data["data"]["shortUrl"]
            }

        return {

            "success":False,

            "affiliate_url":url
        }

    except Exception as e:

        print("ERROR:",e)

        return {

            "success":False,

            "affiliate_url":url
        }