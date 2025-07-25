Product-Recommendation-System
Final year project using python and meta-path for recommendations
Product Recommendation System Using Meta-Path Discovery

Hi!  This is my final year B.Tech (CSE) project. The goal of this system is to recommend products to users based on their interests and personality traits — even when there’s very little user data available. Unlike traditional systems that rely only on purchase history, this approach dives deeper by using **Meta-Path Discovery** within a **Heterogeneous Information Network (HIN)** to find smarter, more meaningful connections.

💡 Highlights

- Solves the cold-start problem (when a new user has little or no data)
- Uses SVM (Support Vector Machine) for making predictions
- Combines interest + personality data for better personalization
- Visualizes accuracy and recommendation performance
- Includes multiple user roles: Admin, Remote User, and Service Provider
Tools & Technologies Used

| Category      | Tools/Technologies         |
|---------------|-----------------------------|
| Frontend      | HTML, CSS, JavaScript       |
| Backend       | Python, Django              |
| Database      | MySQL (via WAMP Server)     |
| ML Algorithm  | Support Vector Machine (SVM)|
| IDE/Tools     | Visual Studio Code, GitHub  |

Modules Overview

1. Admin – Handles user registrations, logins, and backend data  
2. Service Provider– Uploads datasets, trains the model, manages recommendations  
3. Remote User – Users get product recommendations after login  
4. Meta-Path Discovery – Core logic for linking users and products  
5. Personality Module – Analyzes personality traits for better predictions  
6. Feedback System – Learns from user choices and improves results

📁 Project Folder Structure

├── /code │   ├── main.py │   ├── metapath_discovery.py ├── /data │   ├── user_profiles.csv │   ├── product_dataset.csv ├── /templates │   └── HTML + CSS files ├── requirements.txt ├── README.md


How to Run the Project

1. Clone this repo:
   ```bash
   git clone https://github.com/yourusername/Product-Recommendation-System
   cd Product-Recommendation-System

2. Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate    or venv\Scripts\activate on Windows

3. Install required packages:

pip install -r requirements.txt

4. Run the Django server:

python manage.py runserver

5. Open your browser: Visit http://127.0.0.1:8000 and explore the app.


Results

We tested this system using dummy datasets. Compared to standard filtering methods, this approach gave more diverse and accurate recommendations, especially in cold-start scenarios. The project also includes visual charts and graphs to show performance metrics.

 Why I Built This

Recommender systems are everywhere — shopping apps, OTT platforms, and more. I wanted to go beyond simple filtering and try combining behavior + personality to build a system that actually understands users better. This project helped me improve my skills in machine learning, data analysis, and full-stack development.

📎 References

Wang et al. — Meta-Path based Recommendation Models

Tkalcic et al. — Personality-Aware Systems

IEEE-based final year project papers and online resources


Thanks for checking out my project!
Feel free to connect with me on LinkedIn or view more at GitHub.

> **Product Recommendation System Using Meta-Path Discovery**  
> Built a user-personality-based recommendation engine using Python, SVM, and HIN logic. Solved cold-start issues and improved accuracy.  
> GitHub: [github.com/rayapatitrilok/Product-Recommendation-System](https://github.com/rayapatitrilok/Product-Recommendation-System)
