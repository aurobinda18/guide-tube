# YouTube Tutor AI

## 🚀 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/YouTube_Tutor_AI.git
cd YouTube_Tutor_AI

2. Create virtual environment
bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
3. Install dependencies
bash
pip install -r requirements.txt
4. Set up environment variables
Create .env file (ask for the template)

5. Download NLTK data
bash
python download_nltk.py
6. Run the application
bash
python manage.py runserver
📁 Project Structure
analyzer/ - Core analysis modules

guide_tube/ - YouTube integration

check_*.py - Various utility checks

test_*.py - Test files

🔧 Requirements
Python 3.8+

See requirements.txt for dependencies

text

## 📤 **7. Update requirements.txt**
Make sure your `requirements.txt` is complete:
```bash
# Generate from current environment
pip freeze > requirements.txt
💡 Additional recommendations:
Share the .env.template file (without sensitive data):

text
API_KEY=your_key_here
SECRET_KEY=your_secret_here
DEBUG=True
Create a setup script (setup.sh or setup.bat):

bash
# setup.sh
echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "Setup complete!"
For your partner to get started:

bash
# Your partner should run:
git clone YOUR_REPO_URL
cd YouTube_Tutor_AI
# Follow README instructions