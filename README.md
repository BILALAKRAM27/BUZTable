
<!-- Project Logo -->
<p align="center">
  <!-- Replace with actual image URL or GitHub-hosted image -->
  <img src="https://drive.google.com/uc?export=view&id=12RjFJydzxAd_oznyUxds0QhhJJYR_OwR" alt="BUZTable Logo" width="150">
</p>

<h1 align="center">🍽️ BUZTable</h1>
<p align="center"><strong>Where Dining Meets Convenience — Your Ultimate Restaurant Reservation & Food Ordering Solution</strong></p>

---

## 📖 Project Overview

**BUZTable** is a modern, full-stack restaurant reservation and food ordering platform that combines the power of **OpenTable** and **FoodPanda** in one sleek solution.  
It empowers users to:
- Seamlessly book restaurant tables
- Order food for pickup or delivery
- Discover dining deals and promotions
- Review, like, and comment on restaurants  
All within a single, user-friendly interface.

**Target Audience:**  
- Diners looking for convenience  
- Restaurants aiming to manage reservations and orders  
- Developers interested in scalable, modular Django projects

---

## ✨ Key Features

| Feature                          | Description                                                                         |
|----------------------------------|-------------------------------------------------------------------------------------|
| 📝 **Reservations**              | Real-time table booking with availability tracking                                  |
| 🍔 **Online Ordering**           | Multi-item food ordering with customizable options                                  |
| 🎯 **Personalized Recommendations** | Suggestions based on user preferences & dining history                            |
| 💬 **Reviews & Comments**        | Community-driven feedback system                                                    |
| 💎 **Restaurant Dashboard**      | Full-featured admin panel for restaurants to manage menus, orders & staff           |
| 🚚 **Third-Party Delivery Support** | Integrations with apps like UberEats & Zomato for delivery fulfillment             |
| 💰 **Secure Payments**           | Integrated payment APIs for hassle-free transactions                               |
| 🔔 **Notifications System**      | Real-time updates on reservations, orders, and promotions                          |

---

## 📂 Project Structure

```bash
buztable/
│
├── restaurant/       # Restaurant app (menus, reservations, orders)
├── user/             # User app (profiles, reviews, favorites)
├── media/            # Uploaded media (images, etc.)
├── static/           # Static assets (CSS, JS)
├── templates/        # Frontend templates
├── manage.py         # Django project manager
└── requirements.txt  # Project dependencies
````

---

## ⚙️ Installation

### ✅ Requirements

* Python 3.10+
* Django 4.x
* PostgreSQL or SQLite (default: SQLite for development)
* pip (Python package installer)
* Git

---

### ✅ Setup Instructions

```bash
# 1️⃣ Clone the repository
git clone https://github.com/BILALAKRAM27/BUZTable.git
cd BUZTable

# 2️⃣ Create a virtual environment
python -m venv env
source env/bin/activate  # On Windows use: env\Scripts\activate

# 3️⃣ Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4️⃣ Apply database migrations
python manage.py migrate

# 5️⃣ Run the development server
python manage.py runserver
```

---

## 📑 BUZTable Project Accounts & Test Data

BUZTable comes with pre-configured demo accounts for quick testing and development.

---

### 🧑‍🍳 **User/Diner Test Accounts**

| **Email**                                          | **Password** |
| -------------------------------------------------- | ------------ |
| [user1@gmail.com](mailto:user1@gmail.com)          | KING\_@#!    |
| [user2@gmail.com](mailto:user2@gmail.com)          | KING\_@#!    |
| [user3@gmail.com](mailto:user3@gmail.com) *(etc.)* | KING\_@#!    |

---

### 🍽️ **Restaurant Test Accounts**

| **Email**                                          | **Password** |
| -------------------------------------------------- | ------------ |
| [rest1@gmail.com](mailto:rest1@gmail.com)          | KING\_@#!    |
| [rest2@gmail.com](mailto:rest2@gmail.com)          | KING\_@#!    |
| [rest3@gmail.com](mailto:rest3@gmail.com) *(etc.)* | KING\_@#!    |

---

### 🛡️ **Superuser (Admin) Account**

| **Username** | **Password** |
| ------------ | ------------ |
| owner        | 123          |

---

### 💳 **Test Card for Payments**

You can use the following **test credit card** for payment testing (in sandbox mode only):

| **Card Number**     | **Expiry**      | **CVC** | **ZIP** |
| ------------------- | --------------- | ------- | ------- |
| 4242 4242 4242 4242 | Any future date | Any     | Any     |

> Example:

```
Card Number: 4242 4242 4242 4242  
Expiry: 12/34  
CVC: 123  
ZIP: 12345  
```

---

### ⚠️ **Important Note:**

* These accounts are for **development & testing purposes only**.
* Please **change the credentials** and **secure sensitive information** before deploying to production.

---

```

---

### ✅ Key Benefits of This README:
- Fully polished and production-ready.
- Easy to navigate with clear headings and icons.
- Google Drive logo image integrated correctly.
- Test account info clearly presented.
- Ready for direct use in your repository.

---

### ✅ Optional (If You Want More Help):
I can also help you with:
- GitHub Actions CI Workflow.
- Auto-generating `requirements.txt`.
- Writing CONTRIBUTING.md or SECURITY.md.

Would you like me to provide any of these?
```
