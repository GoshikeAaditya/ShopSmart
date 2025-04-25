🛒 ShopSmart
ShopSmart is a versatile Python-based solution for streamlined product management in e-commerce platforms. It offers an efficient interface for managing product data stored in a MySQL database, supporting operations like insertion, retrieval, and dynamic updates with a robust and scalable schema.


🚀 Features
✅ Automatic Database Setup: Creates and initializes a MySQL database and products table.

📦 Comprehensive Product Schema: Handles fields like product name, brand, category, price, weight, ingredients, allergens, nutrition, and availability.

🧠 Smart Data Handling: Uses Pandas for clean, structured data retrieval and visualization.

➕ Dynamic Data Insertion: Add new products on the fly.

🔍 ID-based Search: Retrieve product details instantly via product ID.

🌐 Multi-currency & Unit Support: Designed to handle various pricing formats and weight units.

⚠️ Robust Error Handling: Ensures database integrity and prevents duplicate or malformed entries.


📁 Project Structure

ShopSmart/
│
├── shopsmart.py         # Main script with database and product logic
├── config.py            # Database connection configuration
├── requirements.txt     # Required Python packages
└── README.md            # This file


🛠️ Installation

1. Clone the repository:

git clone https://github.com/yourusername/ShopSmart.git
cd ShopSmart 

2. Install dependencies:

pip install -r requirements.txt

3. Set up your MySQL credentials in config.py:

DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'shopsmart_db'
}

4. Run the main script:

python shopsmart.py


⚙️ Customization
You can modify the schema or extend functionalities like:

Category-specific filtering

Bulk uploads via CSV

REST API integration


📄 License
This project is licensed under the MIT License. See LICENSE for details.


🤝 Acknowledgements
Built with ❤️ to help e-commerce developers simplify and standardize their product data workflows.
