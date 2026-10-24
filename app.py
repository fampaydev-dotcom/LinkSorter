from flask import Flask, request, render_template_string, redirect, abort, send_from_directory
import os
import json
import uuid

app = Flask(__name__)
ADMIN_KEY = "srkxkeybro"
DATA_FILE = "data.json"
UPLOAD_FOLDER = "uploads"

# Ensure upload folder and data file exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ==========================================
# 1. MAIN FRONTEND (Landing Page)
# ==========================================
FRONTEND_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{{ bot_name }}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        
        body {
            /* Background Image Set */
            background-color: #0f172a; /* Fallback dark color */
            background-image: url('/back.jpeg'); 
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            
            height: 100vh; display: flex; justify-content: center; align-items: center;
            flex-direction: column; color: white; padding: 20px; position: relative;
        }
        
        /* Overlay taaki background ke upar text clear dikhe */
        body::before {
            content: '';
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(15, 23, 42, 0.75); /* 75% dark overlay */
            z-index: 1;
        }

        .card {
            background: rgba(15, 23, 42, 0.95); 
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 24px; padding: 40px 20px; width: 100%; max-width: 380px;
            text-align: center; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(10px); z-index: 10;
        }
        
        .profile-container {
            width: 100px; height: 100px; margin: 0 auto 20px;
            border-radius: 50%; border: 3px solid #1e293b; padding: 3px; background: #0f172a;
        }
        .profile-img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
        
        h1 { font-size: 24px; font-weight: 800; margin-bottom: 5px; letter-spacing: 0.5px; }
        .username { color: #94a3b8; font-size: 14px; margin-bottom: 25px; font-weight: 600; }
        .sub-text { font-size: 14px; font-weight: 600; margin-bottom: 8px; line-height: 1.4; }
        .trust-text { font-size: 14px; font-weight: 600; margin-bottom: 30px; }
        
        .start-btn {
            display: block; width: 100%; background: #0ea5e9; color: white; text-decoration: none;
            padding: 16px; border-radius: 12px; font-size: 16px; font-weight: 800;
            letter-spacing: 1px; box-shadow: 0 0 20px rgba(14, 165, 233, 0.4);
            transition: all 0.3s ease; border: none; cursor: pointer;
        }
        .start-btn:hover { background: #0284c7; box-shadow: 0 0 30px rgba(14, 165, 233, 0.6); transform: translateY(-2px); }
        
        .powered-by { color: #64748b; font-size: 12px; margin-top: 25px; font-weight: 500; }
    </style>
</head>
<body>
    <div class="card">
        <div class="profile-container">
            <!-- Agar Image.jpeg na mile toh dummy image load hogi -->
            <img src="/{{ profile_pic }}" alt="Profile" class="profile-img" onerror="this.src='https://cdn-icons-png.flaticon.com/512/149/149071.png';">
        </div>
        <h1>{{ bot_name }}</h1>
        <div class="username">{{ bot_username }}</div>
        <div class="sub-text">{{ sub_text_1 }}</div>
        <div class="trust-text">{{ sub_text_2 }}</div>
        <a href="{{ redirect_url }}" target="_blank" class="start-btn">START BOT</a>
        <div class="powered-by">Powered by Telegram</div>
    </div>
</body>
</html>
"""

# ==========================================
# 2. ADMIN PANEL
# ==========================================
ADMIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Control</title>
    <style>
        body { background: #0f172a; color: white; font-family: sans-serif; padding: 20px; }
        .container { max-width: 800px; margin: auto; }
        .box { background: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        input, select { width: 100%; padding: 10px; margin: 8px 0 15px; border-radius: 5px; border: none; background: #334155; color: white; box-sizing: border-box;}
        button { padding: 12px; background: #0ea5e9; color: white; border: none; border-radius: 5px; font-weight: bold; cursor: pointer; width: 100%;}
        button:hover { background: #0284c7; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #334155; }
        a.btn { background: #ef4444; padding: 5px 10px; color: white; text-decoration: none; border-radius: 5px; font-size: 12px;}
        a.btn-edit { background: #eab308; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Admin Control Panel</h1>
        
        <div class="box">
            <h2>Create / Edit Bot Link</h2>
            <form method="POST" enctype="multipart/form-data">
                <input type="hidden" name="action" value="save">
                <input type="hidden" name="slug" id="edit_slug" value="">
                
                <label>Custom Slug (Link name):</label>
                <input type="text" name="custom_slug" id="custom_slug" required placeholder="e.g. bot1">
                
                <label>Bot Name:</label>
                <input type="text" name="bot_name" id="bot_name" required placeholder="ADULT VIDEOS 😍">
                
                <label>Bot Username:</label>
                <input type="text" name="bot_username" id="bot_username" required placeholder="@adultvid12k_bot">
                
                <label>Redirect URL (Start Button):</label>
                <input type="url" name="redirect_url" id="redirect_url" required placeholder="https://t.me/...">
                
                <label>Sub Text 1:</label>
                <input type="text" name="sub_text_1" id="sub_text_1" value="START BOT AND WATCH FREE DEMO ❤️">
                
                <label>Sub Text 2:</label>
                <input type="text" name="sub_text_2" id="sub_text_2" value="100% TRUSTED BOT 🔥">
                
                <label>Profile Pic (Optional - upload new):</label>
                <input type="file" name="profile_pic" accept="image/*">
                
                <button type="submit">Save Bot Link</button>
            </form>
        </div>

        <div class="box">
            <h2>Your Links</h2>
            <table>
                <tr>
                    <th>Slug (Link)</th>
                    <th>Bot Name</th>
                    <th>Actions</th>
                </tr>
                {% for slug, data in bots.items() %}
                <tr>
                    <td><a href="/{{ slug }}" target="_blank" style="color:#0ea5e9;">/{{ slug }}</a></td>
                    <td>{{ data.bot_name }}</td>
                    <td>
                        <a href="#" class="btn btn-edit" onclick="editBot('{{ slug }}', '{{ data.bot_name }}', '{{ data.bot_username }}', '{{ data.redirect_url }}')">Edit</a>
                        <a href="/?admin={{ admin_key }}&delete={{ slug }}" class="btn" onclick="return confirm('Delete this link?')">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <script>
        function editBot(slug, name, username, url) {
            document.getElementById('edit_slug').value = slug;
            document.getElementById('custom_slug').value = slug;
            document.getElementById('bot_name').value = name;
            document.getElementById('bot_username').value = username;
            document.getElementById('redirect_url').value = url;
            window.scrollTo(0,0);
        }
    </script>
</body>
</html>
"""

@app.route('/<path:path>')
def serve_static(path):
    # Check if file exists in root folder (jaise back.jpeg ya Image.jpeg)
    if os.path.exists(path) and os.path.isfile(path):
        return send_from_directory('.', path)
    # Agar file nahi hai, toh slug page handle karega
    return show_bot(path)

@app.route('/', methods=['GET', 'POST'])
def main():
    # Check if it's admin route
    admin = request.args.get('admin')
    
    if admin == ADMIN_KEY:
        bots = load_data()
        
        # Handle Delete
        del_slug = request.args.get('delete')
        if del_slug and del_slug in bots:
            del bots[del_slug]
            save_data(bots)
            return redirect(f"/?admin={ADMIN_KEY}")

        # Handle Form Submit
        if request.method == 'POST' and request.form.get('action') == 'save':
            slug = request.form.get('custom_slug').strip().replace(' ', '-').lower()
            old_slug = request.form.get('slug')
            
            existing_data = bots.get(slug, {})
            profile_pic = existing_data.get('profile_pic', 'Image.jpeg')

            if 'profile_pic' in request.files:
                file = request.files['profile_pic']
                if file.filename != '':
                    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    profile_pic = filepath

            bots[slug] = {
                'bot_name': request.form.get('bot_name'),
                'bot_username': request.form.get('bot_username'),
                'redirect_url': request.form.get('redirect_url'),
                'sub_text_1': request.form.get('sub_text_1'),
                'sub_text_2': request.form.get('sub_text_2'),
                'profile_pic': profile_pic
            }
            
            if old_slug and old_slug != slug and old_slug in bots:
                del bots[old_slug]
                
            save_data(bots)
            return redirect(f"/?admin={ADMIN_KEY}")

        return render_template_string(ADMIN_HTML, bots=bots, admin_key=ADMIN_KEY)
    
    # If main URL is opened without slug
    elif request.path == '/':
        abort(400, description="400 Bad Request. This URL is invalid.")
        
    return "Not Found", 404

@app.route('/<slug>')
def show_bot(slug):
    # Flask routing fix: agar static file serve ho gayi ho toh wapas mat aana
    if os.path.exists(slug) and os.path.isfile(slug):
        return send_from_directory('.', slug)

    bots = load_data()
    if slug in bots:
        data = bots[slug]
        return render_template_string(FRONTEND_HTML, **data)
    else:
        abort(404, description="Bot Link Not Found")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)