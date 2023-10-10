# Firebase-Emulator
A prototype system that emulates Firebase using Flask, WebSockets, and MongoDB


Firebase Emulator:

1. To install the required python libraries execute this command:
pip install -r requirements.txt

2. Make sure the database "dsci551" is present with the books collection

3. To run the flask app:
python3 server_app.py

4. To execute the commands:
Open a new ec2 terminal window and use the sample commands below:

Note: The handle command functionality requires the CURL commands to be inside another curl command.



#Sample Commands:

All data: (GET)

curl -X POST -d "command=curl -X GET 'http://localhost:27017/dsci551/books3.json'" http://localhost:5000/handle_command

curl -X POST -d "command=curl -X GET 'http://localhost:27017/dsci551/books3/1933988746.json'" http://localhost:5000/handle_command

curl -X POST -d "command=curl -X GET 'http://localhost:27017/dsci551/books3/1933988746/price.json'" http://localhost:5000/handle_command

curl -X POST -d "command=curl -X GET 'http://localhost:27017/dsci551/books3.json?limitToFirst=5'" http://localhost:5000/handle_command

curl -X POST -d "command=curl -X GET 'http://localhost:27017/dsci551/books3.json?limitToLast=2'" http://localhost:5000/handle_command


Error:
curl -X POST -d "command=curl -X GET 'http://localhost:27017/dsci551/books3.json?limitToFirst=2&limitToLast=3'" http://localhost:5000/handle_command

curl -X POST -d "command=curl -X GET 'http://localhost:27017/dsci551/books3.json?limitToLast=ab'" http://localhost:5000/handle_command


PUT:
curl -X POST -d "command=curl -X PUT 'http://localhost:27017/dsci551/books3/1935182420.json' -d '{\"title\": \"Updated Book Title\", \"author\": \"Updated Book Author\", \"price\": 29.99, \"description\": \"Updated Book Description\"}'" http://localhost:5000/handle_command

PATCH:
curl -X POST -d "command=curl -X PATCH 'http://localhost:27017/dsci551/books3/1935182420.json' -d '{\"title\":\"Flex 4 in Action Edition 2\"}' " http://localhost:5000/handle_command


#CRUD operations:

Add Book:   
curl -H "Content-Type: application/json" -X POST -d '{"isbn" : "19323945249", "title" : "Codec: Encoders and Decoders", "author": "John Doe", "price" : 10, "description": "short desc"}' http://localhost:5000/add_book

Update Book:
curl -X PUT -H "Content-Type: application/json" -d '{"isbn": "19323945249", "title": "Updated Book Title", "author": "Updated Book Author", "price": 29.99, "description": "Updated Book Description"}' http://localhost:5000/update_book


View Book Details:  
curl http://localhost:5000/book/19323945249

Delete Book:    
curl -X DELETE http://localhost:5000/delete_book/19323945249


Test data:
curl -X POST -d "command=curl -X GET 'http://localhost:27017/dsci551/test.json'" http://localhost:5000/handle_command

curl -X POST -d "command=curl -X PUT 'http://localhost:27017/dsci551/test/55f14313c7447c3da7052518.json' -d '{\"name\":\"Impossible_Burgers\"}' " http://localhost:5000/handle_command

curl -X POST -d "command=curl -X PATCH 'http://localhost:27017/dsci551/test/55f14313c7447c3da7052518.json' -d '{\"URL\": \"https://www.example.com\", \"name\": \"Example Restaurant\", \"type_of_food\": \"Italian\", \"rating\": 4.5, \"address\": \"123 Main St\", \"outcode\": \"12345\", \"postcode\": \"ABC123\"}'" http://localhost:5000/handle_command
