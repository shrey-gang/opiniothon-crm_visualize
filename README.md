# opiniothon-crm_visualize
Opiniothon

Targeted Problem Statements:
 A next generation customer relationship management tool
 A data visualization toolbox to visualize large data


Idea – 

Part 1 – Creating a promotion controller, which will interact with all the food/ecommerce suppliers, and get all the offers that they are providing and will send the few selected and most suitable offers to users/people in mail/messages based on a smart optimized logic. 

The shortlisting of offers to be sent to user will take in the below mentioned parameters in consideration – 
User’s past browsing history
User’s past order history
Previously used offers
Previous Offers that were not Opted (and other offers were choosen)
Location 

The algorithm will make sure of sending only relative and interesting offers to user and improving the order conversion rate, as it will be centralized platform for promotion for all the suppliers.

Part 2 – Creating a visualization platform for the suppliers to show the statistics related to their products/offers/conversionRate. Which will be useful for them to provide more relevant offers in future in order to improve their selling.



Implementation : 

Part 1 of the Problem has been completed, and All the API's endpoints are provided to access the data
Part 2 - a basic UI was designed (just for the feel, not connected with the API)


Technology Used : 

For Backend API's -
Flask Framework
Python
MongoDb for Database

For FrontEnd:
Javascript
PHP
Chart.js

WorkFlow :

This Application's workflow is as mentioned below:

Various Supplier's can register with the Platform using registerClient API
The Credentials will be given to them
Login is used for login and verification
Client will be able to create various Items and Categories on the platform
These details are centralized and unique, so the user's targeted messages will be based on the user details from all suppliers

Clients will have to submit their user's details, orderHistory, pastOrders, BorwsingHistory, offerDetails using 
/insertUserInfo, /createOffers

Finally On hitting the /shortlistMsgs api, all the shortlisted offer to each user will be sent back as the response.


This platform will be building and improving the database from client provided details, so will improvize on more user base details.



API routes are as mentinoed below :

1. 
/login :
RequestMethod: POST
RequestType: application/json
Body: 
{
 "EmailId": String,
 "Password", String
}

2. 
/registerClient :
RequestMethod: POST
RequestType: application/json
Body: 
{
 "Name":String,
 "Password": String,
 "EmailId": String
}


3.
/getProducts :
RequestMethod: POST
RequestType: application/json
RequestBody: 
{}
ResponseBody:
{
 Array[String]
}

4. 
/createProducts
RequestMethod: POST
RequestType: application/json
RequestBody: 
{
"ClientId": String,
 "ItemName":Array[String],
 "ParentCategoryName": String
}
ResponseBody:
{
 "Product Stored Successfully"
}

5.
/getProducts
RequestMethod: POST
RequestType: application/json
RequestBody: 
{}
ResponseBody:
{
 Array[String]
}

6.
/createCategories
RequestMethod: POST
RequestType: application/json
RequestBody: 
{
"CategoryName": String
}
ResponseBody:
{
 "Category Stored Successfully"
}

7.
/getCategories
RequestMethod: POST
RequestType: application/json
RequestBody: 
{}
ResponseBody:
{
 Array[String]
}

8.
/createOffers
RequestMethod: POST
RequestType: application/json
RequestBody: 
{
"ClientId": String,
    "OfferId":Int,
    "OfferName":String,
    "CouponCode": String,
    "DiscountPercent": Float,
    "ApplicableOnCategory":Boolean,
    "ApplicableOnSpecificProductsOnly":Boolean,
    "ProductId": Array[String],
    "CategoryId": String,
    "ValidStartDate":DateTime (dd/mm/yyyy HH:MM:SS.F),
    "ValidEndDate":DateTime (dd/mm/yyyy HH:MM:SS.F)
}
ResponseBody:
{
 "Offer Stored Successfully
}

9.
/shortlistMsgs
RequestMethod: POST
RequestType: application/json
RequestBody: 
{
}
ResponseBody:
{
 Array[{'UserName':String, 'UserId': String, 'OfferId': Int, 'ClientId': String}]
}
