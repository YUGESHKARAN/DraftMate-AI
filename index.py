import os
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from middleware.auth_token import token_required


from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from langsmith import Client
from dotenv import load_dotenv
from config.input_guardrail import is_valid_post_description

import json
import redis

load_dotenv()

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

MAX_QUERY_LENGTH = os.getenv('MAX_QUERY_LENGTH')
frontend_url = os.getenv('FRONTEND_END_URL')

CORS(app, resources={
    r"/": {"origins": [frontend_url,"https://blog-frontend-teal-ten.vercel.app","http://localhost:5173"]},
    r"/enhance-content": {"origins": [frontend_url, "https://blog-frontend-teal-ten.vercel.app","http://localhost:5173"]}
})

client = Client()
CORS(app)


MAX_HISTORY =  6
chat_message = []

template = """
You are DraftMateAI, an AI content co-worker for a Technical Community Platform.

Your responsibility is to transform a creator's raw technical post into a clean,
professional, publication-ready Markdown article while preserving the author's
original meaning and intent.

==================================================
VALIDATION RULES
==================================================

The input MUST be a technical post related to one or more of:

- Software Development
- Web Development
- Mobile Development
- Programming
- Artificial Intelligence
- Machine Learning
- Data Science
- DevOps
- Cloud Computing
- Cybersecurity
- Databases
- System Design
- Open Source
- Developer Tools
- Technical Research
- Technical Learning
- Technical Findings
- Technical Project Showcase

If the input is not a valid technical post description, respond ONLY with:

Please provide a valid technical post description.

Do NOT:

- Answer questions
- Generate unrelated content
- Create tutorials from scratch
- Introduce new technologies not mentioned
- Invent repositories, links, metrics, results, or claims
- Change the author's intended message

==================================================
CONTENT ENHANCEMENT RULES
==================================================

Improve:

- Clarity
- Grammar
- Readability
- Formatting
- Structure
- Professional tone

Preserve:

- Technical accuracy
- Original meaning
- Original technologies
- Original links
- Original project details

Keep the final length reasonably similar to the input.

==================================================
MARKDOWN OUTPUT STANDARD
==================================================

Generate clean Markdown using only relevant sections.

Preferred structure:

# Title

## Overview

Short refined introduction.

## Tech Stack

Generate valid technology badges ONLY for technologies explicitly mentioned.
Example:

![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=white)
![Node.js](https://img.shields.io/badge/Node.js-339933?logo=node.js&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white)


## Key Features

- Feature 1
- Feature 2
- Feature 3

## Technical Highlights

- Important implementation details
- Architecture decisions
- Optimizations
- Findings



## Conclusion

Short closing summary when appropriate.

==================================================
BADGE RULES
==================================================

When technologies are mentioned, generate Shields.io badges.

Examples:

React
https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=white

Node.js
https://img.shields.io/badge/Node.js-339933?logo=node.js&logoColor=white

Express
https://img.shields.io/badge/Express-000000?logo=express&logoColor=white

MongoDB
https://img.shields.io/badge/MongoDB-47A248?logo=mongodb&logoColor=white

Python
https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white

FastAPI
https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white

Docker
https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white

Generate badges ONLY for technologies explicitly mentioned in the input.

Do NOT invent technologies.

==================================================
LINK RULES
==================================================

If the original content contains URLs:

Convert them into Markdown links.
Note:
 1. If no URL provided by the user, do not create a Resources section.

==================================================
STYLE RULES
==================================================

- Use concise professional language
- Prefer bullet points for features and findings
- Use headings consistently
- Avoid excessive marketing language
- Avoid emojis unless already present
- Keep content publication-ready
- Produce valid Markdown only

==================================================
Chat History:

{chat_history}

User Post Description:

{description}

==================================================

Refined Markdown Output:
"""


llm = "openai/gpt-oss-20b"
# llm = "openai/gpt-oss-120b"
model = ChatGroq(model=llm)
# model = ChatGroq(model="llama-3.1-8b-instant")


prompt = ChatPromptTemplate.from_template(template)


@app.route("/")
@limiter.limit("20 per minute")
def welcome():
    return jsonify({"message":"Welcome to the DraftMate AI!"})

# @app.route("/enhance-content", methods=['POST'])
# @limiter.limit("20 per minute")
# @token_required
# def generate_content():
#     global chat_message
#     try:
#         data = request.json
#         description = data.get("description","")

#         if  len(description) > int(MAX_QUERY_LENGTH):
#             return jsonify({"content":"query limit exceed, keep context limit maximum of 2500 words."}), 200

#         if len(chat_message) ==0 and  not is_valid_post_description(description):
#             return jsonify({
#                 "content": "Please provide a valid technical post description."
#             }), 200

#         # query = prompt.invoke({"description":description, "chat_history":chat_message})

#         chat_message.append({"user":description})
#         chain = prompt | model | StrOutputParser()
#         result = chain.invoke({"description":description, "chat_history":chat_message}) 
#         chat_message.append({"assistant":result})

#         chat_message = chat_message[-MAX_HISTORY:]

#         # print("chat history:", chat_message)
#         return jsonify({"content":result}),200
#     except Exception as e:
#         print(f"error {str(e)}")
#         return jsonify({"error":str(e)}), 500


r = redis.Redis.from_url(os.getenv("REDIS_URL"), decode_responses=True)
MAX_HISTORY = 6
HISTORY_TTL = 60 * 10  # 10 min, tune as needed

def get_history(tenant_id, author_id):
    key = f"draftmate:history:{tenant_id}:{author_id}"
    raw = r.get(key)
    return json.loads(raw) if raw else []

def save_history(tenant_id, author_id, history):
    key = f"draftmate:history:{tenant_id}:{author_id}"
    r.setex(key, HISTORY_TTL, json.dumps(history[-MAX_HISTORY:]))


@app.route("/enhance-content", methods=['POST'])
@limiter.limit("20 per minute")
@token_required
def generate_content():
    try:
        data = request.json
        description = data.get("description", "")

        # ASSUMPTION: token_required sets request.user = decoded JWT payload
        # (adjust this one line if your middleware attaches it differently,
        # e.g. g.user, request.decoded_token, etc.)
        user = getattr(request, "user", None)
        if not user:
            return jsonify({"error": "unauthenticated"}), 401

        author_id = user.get("authorId")
        tenant_id = user.get("tenantId")
        if not author_id or not tenant_id:
            return jsonify({"error": "unauthenticated"}), 401

        if len(description) > int(MAX_QUERY_LENGTH):
            return jsonify({"content": "query limit exceed, keep context limit maximum of 2500 words."}), 200

        history = get_history(tenant_id, author_id)

        if len(history) == 0 and not is_valid_post_description(description):
            return jsonify({"content": "Please provide a valid technical post description."}), 200

        history.append({"user": description})
        chain = prompt | model | StrOutputParser()
        result = chain.invoke({"description": description, "chat_history": history})
        history.append({"assistant": result})

        save_history(tenant_id, author_id, history)

        return jsonify({"content": result}), 200
    except Exception as e:
        print(f"error {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ =="__main__":
    app.run(host="0.0.0.0", debug=False)

