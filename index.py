import os
from flask import Flask, request, jsonify
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
    r"/": {"origins": [frontend_url,"http://localhost:5173"]},
    r"/enhance-content": {"origins": [frontend_url,"http://localhost:5173"]}
})

client = Client()
CORS(app)



chat_message = []
# template = """
#        You are  social media content creator. responsible for transforming given scripts into professional social media contents similar like LinkedIn post along with professional emojies and with tags.
#        make sure to check the chat history for context before generating new content.
#        Chat Message History:
#        {chat_history}
#         Note: 
#         1. The content you are delivering is directly add to the post without any adjustments. make sure to always genrate as a final response without any options.
#         2. The response format should be Markdown language.
#         3. If necessary produce the content in bullet points.
#         script: {description}
               
# """

template = """
You are an AI assistant designed for a **Tech Community Platform**.

Your job is to **enhance and refine a post description written by a creator before publishing it**.

Your task is ONLY to improve the given post content.

--------------------------------------------------

IMPORTANT RULES:

1. The input must be a **technical post description** related to software development, programming, AI, data science, system design, or technology.

2. If the input is NOT a valid technical post description, reply ONLY with:

"Please provide a valid technical post description."

3. Never answer questions.
4. Never generate unrelated information.
5. Never introduce new topics that are not present in the input.
6. Only improve the clarity, structure, and readability of the given description.

--------------------------------------------------

WRITING GUIDELINES:

- Maintain the same meaning as the original content
- Keep the response word limit similar to the input.
- Write in clear, professional, natural language
- Output must be **ready to publish**
- Use **Markdown formatting**
- Use bullet points if helpful

--------------------------------------------------

Chat History:
{chat_history}

--------------------------------------------------

User Post Description:
{description}

--------------------------------------------------

Your Output:
"""

model = ChatGroq(model="llama-3.1-8b-instant")

prompt = ChatPromptTemplate.from_template(template)


@app.route("/")
@limiter.limit("20 per minute")
@token_required
def welcome():
    return jsonify({"message":"welcome to chat backend content manipulator"})

@app.route("/enhance-content", methods=['POST'])
@limiter.limit("20 per minute")
@token_required
def generate_content():
    try:
        data = request.json
        description = data.get("description","")

        if len(description) > int(MAX_QUERY_LENGTH):
            return jsonify({"content":"query limit exceed, keep context limit maximum of 700 words."}), 200

        if not is_valid_post_description(description):
            return jsonify({
                "content": "Please provide a valid technical post description."
            }), 200

        query = prompt.invoke({"description":description, "chat_history":chat_message})

        chat_message.append({"user":query.messages[0].content})
        chain = prompt | model | StrOutputParser()
        result = chain.invoke({"description":description, "chat_history":chat_message}) 
        chat_message.append({"assistant":result})

        # print("chat history:", chat_message)
        return jsonify({"content":result}),200
    except Exception as e:
        return jsonify({"error":str(e)}), 500


if __name__ =="__main__":
    app.run(host="0.0.0.0", debug=False)

