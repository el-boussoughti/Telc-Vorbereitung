# Word & Sentence Manager

A simple web application to manage unique words with sentences and themes. Built with Flask backend and vanilla HTML/CSS/JavaScript frontend with MySQL database.

## Features

- ✅ Add unique words with sentences and themes
- ✅ Real-time word existence check as you type
- ✅ Automatic disable/enable of Add button based on word availability
- ✅ Display existing words with their sentences and themes
- ✅ Beautiful, responsive UI
- ✅ No frontend frameworks required (pure HTML/CSS/JS)

## Prerequisites

Before running this application, make sure you have installed:

1. **Python** (3.7 or higher)
   - Download from: https://www.python.org/downloads/

2. **MySQL Server**
   - Download from: https://dev.mysql.com/downloads/mysql/
   - During installation, note your username (default: `root`) and password

3. **pip** (usually comes with Python)
   - Verify: `pip --version`

## Setup Instructions

### 1. Create MySQL Database

Open MySQL command line or MySQL Workbench and run:

```sql
CREATE DATABASE words_db;
USE words_db;
```

### 2. Configure Database Connection

Edit the `app.py` file and update the `DB_CONFIG` dictionary with your MySQL credentials:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',           # Your MySQL username
    'password': 'your_password',  # Your MySQL password
    'database': 'words_db'
}
```

### 3. Install Python Dependencies

Open terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- Flask-CORS (for cross-origin requests)
- mysql-connector-python (for MySQL connection)

## Running the Application

### Step 1: Start Flask Backend

In your terminal/command prompt, run:

```bash
python app.py
```

You should see output like:
```
* Serving Flask app 'app'
* Debug mode: on
* Running on http://localhost:5000
```

### Step 2: Open in Browser

Open your web browser and go to:

```
http://localhost:5000
```

The application should now be running!

## How to Use

### Adding a Word

1. **Type a Word**: Start typing in the "Word (Unique)" input field
2. **See Real-time Feedback**: 
   - If the word already exists, you'll see it highlighted in red with the existing details
   - The "Add Word" button will be disabled
   - If the word is available, you'll see a green message saying it's unique
   - The "Add Word" button will be enabled
3. **Fill Other Fields**: Enter a sentence and theme
4. **Click Add Word**: Submit the form to add the word to the database
5. **Confirmation**: You'll see a success message and the word appears in the list

### Viewing All Words

The right panel shows all words currently in the database with:
- The word itself
- The sentence where it's used
- The theme/category

## Project Structure

```
.
├── app.py                 # Flask backend with all API routes
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend HTML with CSS and JavaScript
└── README.md             # This file
```

## API Endpoints

The application provides the following REST API endpoints:

### Check if Word Exists
- **Endpoint**: `POST /api/check-word`
- **Body**: `{"word": "example"}`
- **Response**: 
  - If exists: `{"exists": true, "word": "example", "sentence": "...", "theme": "..."}`
  - If not exists: `{"exists": false, "word": "example"}`

### Add New Word
- **Endpoint**: `POST /api/add-word`
- **Body**: `{"word": "example", "sentence": "Example sentence", "theme": "Category"}`
- **Response**: `{"success": true, "message": "Word added successfully"}`

### Get All Words
- **Endpoint**: `GET /api/get-all-words`
- **Response**: Array of word objects with id, word, sentence, and theme

## Troubleshooting

### "Connection refused" or "Cannot connect to MySQL"
- Make sure MySQL server is running
- Check your username and password in `app.py`
- Verify the database `words_db` was created

### "Module not found" error
- Run `pip install -r requirements.txt` again
- Make sure you're using Python 3.7 or higher

### Frontend won't load
- Check that Flask is running on `http://localhost:5000`
- Check browser console for any errors (F12 key)
- Try refreshing the page

### "Word already exists" error appears for new words
- The search is case-insensitive (as intended)
- Try clearing the form and starting fresh
- Check the words list panel to verify

## Database Schema

The application creates a `words` table with the following structure:

```sql
CREATE TABLE words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(255) UNIQUE NOT NULL,
    sentence TEXT NOT NULL,
    theme VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

## Notes

- Words are stored in lowercase for consistent searching
- The application prevents duplicate words at the database level (UNIQUE constraint)
- All searches are case-insensitive
- The frontend automatically refreshes the word list after adding a new word

## Future Enhancements

- Edit existing words
- Delete words
- Search/filter words by theme
- Export words to CSV
- Dark mode
- User authentication

---

Enjoy managing your words!
