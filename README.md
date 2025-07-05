<!-- Project Logo -->
<p align="center">
  <img src="https://drive.google.com/file/d/12RjFJydzxAd_oznyUxds0QhhJJYR_OwR/view?usp=drive_link" alt="BUZTable Logo" width="150">
</p>

<h1 align="center">🍽️ BUZTable</h1>
<p align="center">Where Dining Meets Convenience — Your Ultimate Restaurant Reservation & Food Ordering Solution</p>

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


## ⚙️ Installation

### ✅ Requirements
- Python 3.10+
- Django 4.x
- PostgreSQL or SQLite (default: SQLite for development)
- pip (Python package installer)
- Git

---

### ✅ Setup Instructions

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

