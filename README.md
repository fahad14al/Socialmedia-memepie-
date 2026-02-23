# MemePie 🥧

MemePie is a fully-featured, Django-based social media web application designed for meme enthusiasts. It provides a platform to share, discover, interact with memes, and connect with other users in a dynamic community.

## 🚀 Features

- **User Accounts & Profiles**: Secure user registration, authentication, customizable profiles (bio, profile picture).
- **Meme Sharing**: Upload memes with titles and descriptions.
- **Social Interactions**: Like, comment, and save memes. Follow/unfollow other users.
- **Dynamic Feed**: Personalized timeline showing content from followed users.
- **Direct Messaging**: Real-time 1-on-1 private messaging system between users.
- **Notifications**: Stay updated with interactions on your posts and profile.
- **Responsive Design**: Beautiful, modern frontend tailored for varying screen sizes.
- **Search Engine**: Discover users and memes through the integrated search functionality.
- **Dark Mode**: Toggleable dark themes.

## 🛠️ Technology Stack

- **Backend**: Python, Django 6.0
- **Database**: SQLite (Local Development) / PostgreSQL (Production)
- **Frontend**: HTML5, CSS3, JavaScript
- **Configuration**: `django-environ` (12-Factor App methodology for environment variables)

## 🏗️ Local Development Setup

### 1. Clone the repository
```bash
git clone https://github.com/fahad14al/Socialmedia-memepie-.git
cd Socialmedia-memepie-
```

### 2. Create and activate a virtual environment
**Windows**:
```powershell
python -m venv myenv
myenv\Scripts\activate
```
**Linux / macOS**:
```bash
python3 -m venv myenv
source myenv/bin/activate
```

### 3. Install dependencies
```bash
cd memepie
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Copy `.env.example` and rename it to `.env`:
```bash
cp .env.example .env
```
Ensure you have `DEBUG=True` in your `.env` for local development.

### 5. Apply database migrations
```bash
python manage.py migrate
```

### 6. Create a superuser (Optional but recommended)
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000` in your web browser.

## 🌍 Production Deployment

MemePie is production-ready. 
1. Set `DEBUG=False` in your deployment environment variables.
2. Provide a strong `SECRET_KEY`.
3. Set your production domain in `ALLOWED_HOSTS`.
4. Configure your `DATABASE_URL` for PostgreSQL mapping.
5. Run `python manage.py collectstatic` to gather static assets.

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
