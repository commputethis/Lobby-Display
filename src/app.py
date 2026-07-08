#!/usr/bin/env python3
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sqlite3
import json
import atexit
import subprocess
from werkzeug.utils import secure_filename
from datetime import datetime
from mdns import MDNSBroadcaster

app = Flask(__name__)

DATA_DIR = os.environ.get('LOBBY_DATA_DIR', '/opt/lobby-display')
UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
DB_PATH = os.path.join(DATA_DIR, 'database.db')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DEFAULT_CONFIG = {
    'device_name': 'Lobby Display',
    'resolution': '1920x1080',
    'rotation': 0,
    'default_duration': 10,
    'fade_transition': True,
    'current_playlist': 'default'
}

mdns = None

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)
    global mdns
    if mdns and mdns.running:
        mdns.update_name(cfg['device_name'])

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS playlists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE IF NOT EXISTS playlist_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playlist_id INTEGER,
            image_id INTEGER,
            order_index INTEGER,
            duration INTEGER DEFAULT NULL,
            FOREIGN KEY (playlist_id) REFERENCES playlists(id),
            FOREIGN KEY (image_id) REFERENCES images(id)
        );
    ''')
    conn.execute("INSERT OR IGNORE INTO playlists (name) VALUES ('default')")
    conn.commit()
    conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_mdns():
    global mdns
    cfg = get_config()
    mdns = MDNSBroadcaster(cfg['device_name'], port=5000)
    mdns.start()
    atexit.register(lambda: mdns.stop() if mdns else None)

@app.context_processor
def inject_config():
    return dict(config=get_config(), mdns_hostname=mdns.get_hostname() if mdns else None)

@app.route('/')
def index():
    conn = get_db()
    playlists = conn.execute('SELECT * FROM playlists').fetchall()
    current = get_config()['current_playlist']
    conn.close()
    return render_template('index.html', playlists=playlists, current=current)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files.getlist('files')
        playlist_id = request.form.get('playlist_id')
        
        conn = get_db()
        uploaded = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
                
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                cursor = conn.execute(
                    'INSERT INTO images (filename, original_name) VALUES (?, ?)',
                    (filename, file.filename)
                )
                
                if playlist_id:
                    max_order = conn.execute(
                        'SELECT MAX(order_index) FROM playlist_items WHERE playlist_id = ?',
                        (playlist_id,)
                    ).fetchone()[0] or 0
                    conn.execute(
                        'INSERT INTO playlist_items (playlist_id, image_id, order_index) VALUES (?, ?, ?)',
                        (playlist_id, cursor.lastrowid, max_order + 1)
                    )
                
                uploaded.append(filename)
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'files': uploaded})
    
    conn = get_db()
    playlists = conn.execute('SELECT * FROM playlists').fetchall()
    conn.close()
    return render_template('upload.html', playlists=playlists)

@app.route('/playlists', methods=['GET', 'POST'])
def playlists():
    conn = get_db()
    
    if request.method == 'POST':
        action = request.json.get('action')
        
        if action == 'create':
            name = request.json.get('name')
            try:
                conn.execute('INSERT INTO playlists (name) VALUES (?)', (name,))
                conn.commit()
                return jsonify({'success': True})
            except sqlite3.IntegrityError:
                return jsonify({'error': 'Playlist exists'}), 400
        
        elif action == 'delete':
            playlist_id = request.json.get('id')
            conn.execute('DELETE FROM playlist_items WHERE playlist_id = ?', (playlist_id,))
            conn.execute('DELETE FROM playlists WHERE id = ?', (playlist_id,))
            conn.commit()
            return jsonify({'success': True})
        
        elif action == 'set_active':
            playlist_id = request.json.get('id')
            playlist = conn.execute('SELECT name FROM playlists WHERE id = ?', (playlist_id,)).fetchone()
            if playlist:
                cfg = get_config()
                cfg['current_playlist'] = playlist['name']
                save_config(cfg)
                return jsonify({'success': True})
    
    playlists = conn.execute('''
        SELECT p.*, COUNT(pi.id) as item_count 
        FROM playlists p 
        LEFT JOIN playlist_items pi ON p.id = pi.playlist_id 
        GROUP BY p.id
    ''').fetchall()
    conn.close()
    
    return render_template('playlists.html', playlists=playlists)

@app.route('/playlist/<int:playlist_id>')
def playlist_detail(playlist_id):
    conn = get_db()
    playlist = conn.execute('SELECT * FROM playlists WHERE id = ?', (playlist_id,)).fetchone()
    
    items = conn.execute('''
        SELECT pi.*, i.filename, i.original_name,
               COALESCE(pi.duration, ?) as effective_duration
        FROM playlist_items pi
        JOIN images i ON pi.image_id = i.id
        WHERE pi.playlist_id = ?
        ORDER BY pi.order_index
    ''', (get_config()['default_duration'], playlist_id)).fetchall()
    
    all_images = conn.execute('SELECT * FROM images').fetchall()
    conn.close()
    
    return render_template('playlist_detail.html', 
                         playlist=playlist, items=items, 
                         all_images=all_images, 
                         default_duration=get_config()['default_duration'])

@app.route('/playlist/<int:playlist_id>/update', methods=['POST'])
def update_playlist(playlist_id):
    data = request.json
    conn = get_db()
    
    if 'items' in data:
        for item in data['items']:
            conn.execute(
                'UPDATE playlist_items SET order_index = ?, duration = ? WHERE id = ?',
                (item['order'], item.get('duration'), item['id'])
            )
    
    if 'add_images' in data:
        for image_id in data['add_images']:
            max_order = conn.execute(
                'SELECT MAX(order_index) FROM playlist_items WHERE playlist_id = ?',
                (playlist_id,)
            ).fetchone()[0] or 0
            conn.execute(
                'INSERT INTO playlist_items (playlist_id, image_id, order_index) VALUES (?, ?, ?)',
                (playlist_id, image_id, max_order + 1)
            )
    
    if 'remove_item' in data:
        conn.execute('DELETE FROM playlist_items WHERE id = ?', (data['remove_item'],))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        cfg = get_config()
        old_name = cfg['device_name']
        
        cfg['device_name'] = request.form.get('device_name', cfg['device_name'])
        cfg['resolution'] = request.form.get('resolution', cfg['resolution'])
        cfg['rotation'] = int(request.form.get('rotation', cfg['rotation']))
        cfg['default_duration'] = int(request.form.get('default_duration', 10))
        cfg['fade_transition'] = request.form.get('fade_transition') == 'on'
        
        save_config(cfg)
        
        result = {'success': True}
        if cfg['device_name'] != old_name:
            result['new_hostname'] = mdns.get_hostname() if mdns else None
            
        return jsonify(result)
    
    return render_template('settings.html')

@app.route('/api/slideshow-data')
def slideshow_data():
    conn = get_db()
    cfg = get_config()
    playlist_name = cfg['current_playlist']
    
    playlist = conn.execute('SELECT * FROM playlists WHERE name = ?', (playlist_name,)).fetchone()
    
    if not playlist:
        conn.close()
        return jsonify({'images': [], 'settings': cfg})
    
    items = conn.execute('''
        SELECT i.filename, i.original_name,
               COALESCE(pi.duration, ?) as duration
        FROM playlist_items pi
        JOIN images i ON pi.image_id = i.id
        WHERE pi.playlist_id = ?
        ORDER BY pi.order_index
    ''', (cfg['default_duration'], playlist['id'])).fetchall()
    
    conn.close()
    
    images = [{
        'url': f'/uploads/{item["filename"]}',
        'name': item['original_name'],
        'duration': item['duration']
    } for item in items]
    
    return jsonify({'images': images, 'settings': cfg})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete-image/<int:image_id>', methods=['POST'])
def delete_image(image_id):
    conn = get_db()
    image = conn.execute('SELECT filename FROM images WHERE id = ?', (image_id,)).fetchone()
    
    if image:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], image['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
        conn.execute('DELETE FROM playlist_items WHERE image_id = ?', (image_id,))
        conn.execute('DELETE FROM images WHERE id = ?', (image_id,))
        conn.commit()
    
    conn.close()
    return jsonify({'success': True})

@app.route('/images', methods=['GET'])
def list_images():
    """List all images with delete option"""
    conn = get_db()
    images = conn.execute('''
        SELECT i.*, COUNT(pi.id) as playlist_count 
        FROM images i 
        LEFT JOIN playlist_items pi ON i.id = pi.image_id 
        GROUP BY i.id
        ORDER BY i.uploaded_at DESC
    ''').fetchall()
    conn.close()
    return render_template('images.html', images=images)

if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        init_db()
    
    init_mdns()
    
    cfg = get_config()
    hostname = mdns.get_hostname() if mdns else 'localhost'
    
    print(f"\n{'='*50}")
    print(f"Lobby Display: {cfg['device_name']}")
    print(f"Access via: http://{hostname}:5000")
    print(f"Or via IP: http://0.0.0.0:5000")
    print(f"{'='*50}\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)