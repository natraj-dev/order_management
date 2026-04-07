#  Order Management System (FastAPI)

# Features

* JWT Authentication (Access + Refresh)
* Role-Based Access Control (Admin / Customer)
* Product Management (CRUD)
* Order Management System
* Payment Simulation
* Email Notification System (Real Email via SMTP)
* Background Tasks (FastAPI)

---

# Folder Structure

order_management/
│
├── app/
│   ├── main.py
│
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│
│   ├── db/
│   │   ├── session.py
│   │   ├── base.py
│
│   ├── models/
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── payment.py
│
│   ├── schemas/
│   │   ├── user.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── payment.py
│
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── product_service.py
│   │   ├── order_service.py
│   │   ├── payment_service.py
│   │   ├── email_service.py
│   │   ├── email_templates.py
│
│   ├── routers/
│   │   ├── auth.py
│   │   ├── product.py
│   │   ├── order.py
│   │   ├── payment.py
│
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── order_management.postman_collection.json              


---

##  Tech Stack

* FastAPI
* MySQL
* SQLAlchemy
* JWT (python-jose)
* Passlib (bcrypt)
* SMTP (Gmail)

---

##  Authentication

* Register / Login
* Access Token + Refresh Token
* Role-based authorization

---

###  Role

* Admin
* Customer

###  Product

* Add / Update / Delete (Admin)
* View products (Public)

###  Order

* Create order
* View orders
* Cancel order

###  Payment

* Simulated payment
* Order status update

###  Email

* Order confirmation
* Payment success
* Background processing

---
