from pymongo import MongoClient
from flask import Flask, jsonify, request, abort, make_response
from flask_socketio import SocketIO, emit
import json
import mongodb_functions as mf


# define app
app = Flask(__name__)
async_mode = None
socket_ = SocketIO(app, async_mode=async_mode)
# connect to local MongoDB instance
client = MongoClient('localhost', 27017)
db = client['dsci551']

# get list of collections in database
collections = db.list_collection_names()
books_collection = db["books3"]


@app.route('/')
def index():
    books = books_collection.find({}, {"_id": 0})
    books_data = []
    for book in books:
        data = book[list(book.keys())[0]]
        book_data = dict({"ISBN": str(list(book.keys())[0]), "title": data["name"], "author": data["author"],
                          "price": data["price"], "description": data["description"]})
        books_data.append(book_data)
    return jsonify(books_data)

# APP route
@app.route('/book/<isbn>')
def book_detail(isbn):
    document = books_collection.find(
        {str(isbn): {"$exists": True}}, {"_id": 0})
    book_data = {}
    for book in document:
        data = book[list(book.keys())[0]]
        book_data = dict({"ISBN": list(book.keys())[0], "title": data["name"], "author": data["author"], "price": data["price"], "description": data["description"]})
    return jsonify(book_data)


@app.route("/handle_command", methods=["POST"])
def handle_command():
    command = request.form["command"]
    print(command)
    results = mf.command_process(command)
    return (jsonify(results))



# HTTP fetch process
@app.route('/add_book', methods=['POST'])
def add_book():
    try:
        new_book = request.json
        # check if the ISBN number alreadys exists or not
        books = dict()
        for book in books_collection.find({}, {"_id": 0}):
            books.update(book)
        isbn = new_book["isbn"]
        name = new_book["title"]
        author = new_book["author"]
        price = new_book["price"]
        description = new_book["description"]
        if isbn in list(books.keys()):
            error_message = "This ISBN number already exists."
            response = make_response(jsonify({"error": error_message}), 400)
            return response
        # Do something with the new_book data here
        new_data = {isbn: {"name":name, "author": author, "price": price, 
            "description": description}}
        books_collection.insert_one(new_data)
        success_message = "Success!"
        response = make_response(jsonify({"message": success_message}), 200)
        return response
    
    except Exception as e:
        error_message = str(e)
        response = make_response(jsonify({"error": error_message}), 400)
        return response

@app.route('/update_book', methods=['PUT'])
def update_book():
    try:
        new_book = request.json
        # check if the ISBN number already exists or not
        books = dict()
        for book in books_collection.find({}, {"_id": 0}):
            books.update(book)
        isbn = new_book["isbn"]
        name = new_book["title"]
        author = new_book["author"]
        price = new_book["price"]
        description = new_book["description"]
        if isbn not in list(books.keys()):
            error_message = "Invalid ISBN number!"
            response = make_response(jsonify({"error": error_message}), 400)
            return response
        # Do something with the new_book data here
        new_data = {"$set": {isbn: {"name":name, "author": author, "price": price, 
            "description": description}}}
        filter = {isbn: {"$exists": True}}
        books_collection.update_one(filter, new_data)
        success_message = "Success!"
        response = make_response(jsonify({"message": success_message}), 200)
        return response
    
    except Exception as e:
        error_message = str(e)
        response = make_response(jsonify({"error": error_message}), 400)
        return response

@app.route('/delete_book/<isbn>', methods=['DELETE'])
def delete_book(isbn):
    try:
        print(isbn)
        books = dict()
        for book in books_collection.find({}, {"_id": 0}):
            books.update(book)
        if isbn not in list(books.keys()):
            error_message = "Invalid ISBN number!"
            response = make_response(jsonify({"error": error_message}), 400)
            return response
        filter = {isbn: {"$exists": True}}
        books_collection.delete_one(filter)
        success_message = "Success!"
        response = make_response(jsonify({"message": success_message}), 200)
        return response
    except Exception as e:
        error_message = str(e)
        response = make_response(jsonify({"error": error_message}), 400)
        return response
    
# run app
if __name__ == '__main__':
    socket_.run(app, debug=True)
