from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import sys
import datetime
import html
# Get the absolute path to the project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Add the project root to the path
sys.path.insert(0, BASE_DIR)

app = Flask(__name__, template_folder=TEMPLATE_DIR)
CORS(app)

# SQLite Database Configuration
DB_FILE = os.path.join(BASE_DIR, 'words_db.sqlite')
PUBLIC_DIR = os.path.join(BASE_DIR, 'public')

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = sqlite3.connect(DB_FILE)
        connection.row_factory = sqlite3.Row
        return connection
    except Exception as e:
        print(f"Error connecting to SQLite: {e}")
        return None

def init_db():
    """Initialize the database and create table if it doesn't exist"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE NOT NULL,
                    sentence TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    text_title TEXT NOT NULL,
                    module TEXT NOT NULL,
                    teil TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("PRAGMA table_info(words)")
            columns = {row[1] for row in cursor.fetchall()}
            if 'text_title' not in columns:
                cursor.execute("ALTER TABLE words ADD COLUMN text_title TEXT NOT NULL DEFAULT 'Unassigned'")
                columns.add('text_title')
            if 'module' not in columns:
                cursor.execute("ALTER TABLE words ADD COLUMN module TEXT NOT NULL DEFAULT 'unassigned'")
                columns.add('module')
            if 'teil' not in columns:
                cursor.execute("ALTER TABLE words ADD COLUMN teil TEXT NOT NULL DEFAULT 'teil1'")
                columns.add('teil')
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_words_module_teil ON words(module, teil)")
            cursor.execute("DROP INDEX IF EXISTS idx_words_text_title")
            indexes = cursor.execute("PRAGMA index_list('words')").fetchall()
            for index in indexes:
                name = index[1]
                unique = index[2]
                if unique:
                    info = cursor.execute(f"PRAGMA index_info('{name}')").fetchall()
                    columns_in_index = [row[2] for row in info]
                    if columns_in_index == ['word']:
                        cursor.execute(f"DROP INDEX IF EXISTS {name}")
            connection.commit()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            cursor.close()
            connection.close()

def build_scope_filter(scope, module, teil, params):
    if scope == 'module+teil':
        if not module or not teil:
            return None
        params.extend([module.lower(), teil.lower()])
        return " AND LOWER(module) = ? AND LOWER(teil) = ?"
    return ""

@app.route('/')
def index():
    """Serve the main page"""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering template: {e}")
        return f"Error loading page: {e}", 500


@app.route('/fav.png')
def favicon():
    """Serve favicon from public assets"""
    try:
        return send_from_directory(PUBLIC_DIR, 'fav.png')
    except Exception as e:
        print(f"Error serving favicon: {e}")
        return '', 404

@app.route('/test')
def test():
    """Test route to verify Flask is working"""
    return jsonify({'status': 'Flask is running!'})

@app.route('/api/check-word', methods=['POST'])
def check_word():
    """Check if a word exists in the database"""
    data = request.get_json()
    word = data.get('word', '').strip().lower()
    scope = data.get('scope', 'all')
    module = data.get('module', '').strip().lower()
    teil = data.get('teil', '').strip().lower()
    
    if not word:
        return jsonify({'exists': False, 'word': word})

    if scope == 'module+teil' and (not module or not teil):
        return jsonify({'error': 'Module and Teil required for this scope'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor()
    try:
        query = "SELECT * FROM words WHERE LOWER(word) = ?"
        params = [word]
        scope_clause = build_scope_filter(scope, module, teil, params)
        if scope_clause is None:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Module and Teil required for this scope'}), 400
        query += scope_clause
        cursor.execute(query, tuple(params))
        result = cursor.fetchone()
        
        if result:
            return jsonify({
                'exists': True,
                'id': result['id'],
                'word': result['word'],
                'sentence': result['sentence'],
                'theme': result['theme'],
                'text_title': result['text_title'],
                'module': result['module'],
                'teil': result['teil']
            })
        else:
            return jsonify({'exists': False, 'word': word})
    except Exception as e:
        print(f"Error checking word: {e}")
        return jsonify({'error': 'Error checking word'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/check-text-title', methods=['POST'])
def check_text_title():
    """Check if a text title already has a word"""
    data = request.get_json()
    text_title = data.get('text_title', '').strip()
    scope = data.get('scope', 'all')
    module = data.get('module', '').strip().lower()
    teil = data.get('teil', '').strip().lower()

    if not text_title:
        return jsonify({'exists': False, 'text_title': ''})

    if scope == 'module+teil' and (not module or not teil):
        return jsonify({'error': 'Module and Teil required for this scope'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor()
    try:
        query = "SELECT * FROM words WHERE LOWER(text_title) = ?"
        params = [text_title.lower()]
        scope_clause = build_scope_filter(scope, module, teil, params)
        if scope_clause is None:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Module and Teil required for this scope'}), 400
        query += scope_clause
        cursor.execute(query, tuple(params))
        result = cursor.fetchone()

        if result:
            return jsonify({
                'exists': True,
                'id': result['id'],
                'word': result['word'],
                'sentence': result['sentence'],
                'theme': result['theme'],
                'text_title': result['text_title']
            })
        return jsonify({'exists': False, 'text_title': text_title})
    except Exception as e:
        print(f"Error checking text title: {e}")
        return jsonify({'error': 'Error checking text title'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/add-word', methods=['POST'])
def add_word():
    """Add a new word to the database"""
    data = request.get_json()
    word = data.get('word', '').strip().lower()
    sentence = data.get('sentence', '').strip()
    theme = data.get('theme', '').strip()
    text_title = data.get('text_title', '').strip()
    module = data.get('module', '').strip()
    teil = data.get('teil', '').strip()
    scope = data.get('scope', 'all')
    
    if not word or not sentence or not theme or not text_title or not module or not teil:
        return jsonify({'error': 'All fields are required'}), 400

    if scope == 'module+teil' and (not module or not teil):
        return jsonify({'error': 'Module and Teil required for this scope'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    try:
        word_query = "SELECT id FROM words WHERE LOWER(word) = ?"
        word_params = [word.lower()]
        word_clause = build_scope_filter(scope, module, teil, word_params)
        if word_clause is None:
            return jsonify({'error': 'Module and Teil required for this scope'}), 400
        word_query += word_clause
        cursor.execute(word_query, tuple(word_params))
        if cursor.fetchone():
            return jsonify({'error': 'Word already exists'}), 409

        title_query = "SELECT id FROM words WHERE LOWER(text_title) = ?"
        title_params = [text_title.lower()]
        title_clause = build_scope_filter(scope, module, teil, title_params)
        if title_clause is None:
            return jsonify({'error': 'Module and Teil required for this scope'}), 400
        title_query += title_clause
        cursor.execute(title_query, tuple(title_params))
        if cursor.fetchone():
            return jsonify({'error': 'Text title already in use'}), 409

        cursor.execute(
            "INSERT INTO words (word, sentence, theme, text_title, module, teil) VALUES (?, ?, ?, ?, ?, ?)",
            (word, sentence, theme, text_title, module, teil)
        )
        connection.commit()
        return jsonify({'success': True, 'message': 'Word added successfully'})
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'Word already exists'}), 409
        print(f"Error adding word: {e}")
        return jsonify({'error': 'Error adding word'}), 500
    except Exception as e:
        print(f"Error adding word: {e}")
        return jsonify({'error': 'Error adding word'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/get-all-words', methods=['GET'])
def get_all_words():
    """Get all words from the database"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id, word, sentence, theme, text_title, module, teil FROM words ORDER BY created_at DESC")
        words = cursor.fetchall()
        
        result = [
            {
                'id': word['id'],
                'word': word['word'],
                'sentence': word['sentence'],
                'theme': word['theme'],
                'text_title': word['text_title'],
                'module': word['module'],
                'teil': word['teil']
            }
            for word in words
        ]
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching words: {e}")
        return jsonify({'error': 'Error fetching words'}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/api/export-words', methods=['GET'])
def export_words():
    """Export words as a downloadable table"""
    fmt = request.args.get('format', 'word')
    scope = request.args.get('scope', 'all')
    module = request.args.get('module', '').strip()
    teil = request.args.get('teil', '').strip()

    format_map = {
        'word': {'mime': 'application/msword', 'extension': 'doc'},
        'excel': {'mime': 'application/vnd.ms-excel', 'extension': 'xls'},
        'txt': {'mime': 'text/plain', 'extension': 'txt'}
    }

    if fmt not in format_map:
        return jsonify({'error': 'Unsupported format'}), 400

    if scope not in {'all', 'module', 'module+teil'}:
        return jsonify({'error': 'Invalid export scope'}), 400

    if scope in {'module', 'module+teil'} and not module:
        return jsonify({'error': 'Module is required for this scope'}), 400

    if scope == 'module+teil' and not teil:
        return jsonify({'error': 'Teil is required for this scope'}), 400

    query = "SELECT word, text_title, theme, module, teil FROM words"
    conditions = []
    values = []

    if scope in {'module', 'module+teil'}:
        conditions.append("module = ?")
        values.append(module)

    if scope == 'module+teil':
        conditions.append("teil = ?")
        values.append(teil)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY created_at DESC"

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor()
    try:
        cursor.execute(query, tuple(values))
        rows = cursor.fetchall()

        def escape_value(value):
            return html.escape(str(value)) if value is not None else ''

        headers = ['Word from the text', 'Text title', 'Theme', 'Module', 'Teil']

        bom = '\ufeff'
        if fmt == 'txt':
            lines = ['\t'.join(headers)]
            for row in rows:
                line = '\t'.join([
                    escape_value(row['word']),
                    escape_value(row['text_title']),
                    escape_value(row['theme']),
                    escape_value(row['module']),
                    escape_value(row['teil'])
                ])
                lines.append(line)
            payload = (bom + '\n'.join(lines)).encode('utf-8')
        else:
            header_cells = ''.join(f"<th>{cell}</th>" for cell in headers)
            body_rows = ''.join(
                f"<tr><td>{escape_value(row['word'])}</td>"
                f"<td>{escape_value(row['text_title'])}</td>"
                f"<td>{escape_value(row['theme'])}</td>"
                f"<td>{escape_value(row['module'])}</td>"
                f"<td>{escape_value(row['teil'])}</td></tr>"
                for row in rows
            )
            table = (
                "<html><head><meta charset=\"utf-8\"></head><body>"
                f"<table><thead><tr>{header_cells}</tr></thead>"
                f"<tbody>{body_rows}</tbody></table>"
                "</body></html>"
            )
            payload = table.encode('utf-8')

        meta = format_map[fmt]
        timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        filename = f"telc-words-{scope}-{timestamp}.{meta['extension']}"
        headers = {
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Type': f"{meta['mime']}; charset=utf-8"
        }
        return Response(payload, headers=headers)
    except Exception as e:
        print(f"Error exporting words: {e}")
        return jsonify({'error': 'Error exporting words'}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/api/themes', methods=['GET'])
def get_theme_suggestions():
    """Return theme suggestions based on prefix"""
    prefix = request.args.get('q', '').strip()
    if not prefix:
        return jsonify([])

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor()
    try:
        like_pattern = f"{prefix.lower()}%"
        cursor.execute("""
            SELECT DISTINCT theme
            FROM words
            WHERE LOWER(theme) LIKE ?
            ORDER BY theme
            LIMIT 8
        """, (like_pattern,))
        results = [row['theme'] for row in cursor.fetchall()]
        return jsonify(results)
    except Exception as e:
        print(f"Error fetching themes: {e}")
        return jsonify({'error': 'Error fetching themes'}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/api/update-word', methods=['PUT'])
def update_word():
    """Update an existing word"""
    data = request.get_json()
    word_id = data.get('id')
    word = data.get('word', '').strip().lower()
    sentence = data.get('sentence', '').strip()
    theme = data.get('theme', '').strip()
    text_title = data.get('text_title', '').strip()
    module = data.get('module', '').strip()
    teil = data.get('teil', '').strip()
    scope = data.get('scope', 'all')

    if not word_id or not word or not sentence or not theme or not text_title or not module or not teil:
        return jsonify({'error': 'All fields are required'}), 400

    if scope == 'module+teil' and (not module or not teil):
        return jsonify({'error': 'Module and Teil required for this scope'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor()
    try:
        word_query = "SELECT id FROM words WHERE LOWER(word) = ?"
        word_params = [word.lower()]
        word_clause = build_scope_filter(scope, module, teil, word_params)
        if word_clause is None:
            return jsonify({'error': 'Module and Teil required for this scope'}), 400
        word_query += word_clause + " AND id != ?"
        word_params.append(word_id)
        cursor.execute(word_query, tuple(word_params))
        if cursor.fetchone():
            return jsonify({'error': 'Word already exists'}), 409

        title_query = "SELECT id FROM words WHERE LOWER(text_title) = ?"
        title_params = [text_title.lower()]
        title_clause = build_scope_filter(scope, module, teil, title_params)
        if title_clause is None:
            return jsonify({'error': 'Module and Teil required for this scope'}), 400
        title_query += title_clause + " AND id != ?"
        title_params.append(word_id)
        cursor.execute(title_query, tuple(title_params))
        if cursor.fetchone():
            return jsonify({'error': 'Text title already in use'}), 409

        cursor.execute(
            "UPDATE words SET word = ?, sentence = ?, theme = ?, text_title = ?, module = ?, teil = ? WHERE id = ?",
            (word, sentence, theme, text_title, module, teil, word_id)
        )
        if cursor.rowcount == 0:
            return jsonify({'error': 'Word not found'}), 404
        connection.commit()
        return jsonify({'success': True, 'message': 'Word updated successfully'})
    except sqlite3.IntegrityError as e:
        if 'UNIQUE constraint failed' in str(e):
            return jsonify({'error': 'Word already exists'}), 409
        print(f"Error updating word: {e}")
        return jsonify({'error': 'Error updating word'}), 500
    except Exception as e:
        print(f"Error updating word: {e}")
        return jsonify({'error': 'Error updating word'}), 500
    finally:
        cursor.close()
        connection.close()


@app.route('/api/delete-word/<int:word_id>', methods=['DELETE'])
def delete_word(word_id):
    """Delete a word by its ID"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM words WHERE id = ?", (word_id,))
        if cursor.rowcount == 0:
            return jsonify({'error': 'Word not found'}), 404
        connection.commit()
        return jsonify({'success': True, 'message': 'Word deleted successfully'})
    except Exception as e:
        print(f"Error deleting word: {e}")
        return jsonify({'error': 'Error deleting word'}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    print(f"[v0] Flask app starting...")
    print(f"[v0] Template folder: {TEMPLATE_DIR}")
    print(f"[v0] Database file: {DB_FILE}")
    init_db()
    print(f"[v0] Server running on http://0.0.0.0:3000")
    app.run(debug=True, host='0.0.0.0', port=3000, use_reloader=False)
