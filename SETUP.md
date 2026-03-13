# Quick Setup Guide

## Step 1: MySQL Setup
Open MySQL command line or MySQL Workbench and run:
```sql
CREATE DATABASE words_db;
```

## Step 2: Update Database Credentials
Open `app.py` and find this section (around line 12):
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # ← Change to your MySQL username
    'password': '',  # ← Change to your MySQL password
    'database': 'words_db'
}
```

Update `'user'` and `'password'` to match your MySQL installation.

## Step 3: Install Python Dependencies
Open your terminal/command prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

If that doesn't work, try:
```bash
pip install flask flask-cors mysql-connector-python
```

## Step 4: Run the Application
In the same terminal, run:
```bash
python app.py
```

You should see:
```
 * Running on http://localhost:5000
```

## Step 5: Open in Browser
Open your web browser and go to:
```
http://localhost:5000
```

## Troubleshooting

### If you see "404 Not Found":
1. Make sure Flask is actually running (check terminal output)
2. Try visiting `http://localhost:5000/test` - you should see `{"status":"Flask is running!"}`
3. Check that `templates/index.html` exists in the project folder

### If you see "Database connection failed":
1. Make sure MySQL is running
2. Check your username and password in `app.py` are correct
3. Make sure the `words_db` database exists

### If you see "ModuleNotFoundError":
1. Run `pip install -r requirements.txt` again
2. If using Python 3, you might need to use `pip3` instead of `pip`
3. Make sure you're in the project folder

### Port 5000 already in use:
Edit the last line of `app.py` and change the port:
```python
app.run(debug=True, host='localhost', port=5001)  # Changed 5000 to 5001
```
Then visit `http://localhost:5001`

## How to Use the App

1. **Type a word** in the "Word" input field
2. The app will **automatically search** if the word exists
3. **If it exists**: You'll see the existing data and the Add button will be disabled
4. **If it doesn't exist**: Fill in the Sentence and Theme, then click Add
5. **View all words** you've added in the list below

Enjoy!
