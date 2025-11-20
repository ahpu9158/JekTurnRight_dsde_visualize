# Rain water prediction Visualization

---

## 📦 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/ahpu9158/JekTurnRight_dsde_visualize.git
cd JekTurnRight_dsde_visualize
```

### 2️⃣ Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        
venv\Scripts\activate           
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the App

To launch the Streamlit application:

```bash
streamlit run main.py
```

After running, Streamlit will open the app in your browser automatically.
If not, open the URL shown in the terminal (usually [http://localhost:8501](http://localhost:8501)).

---

## 📁 Project Structure

```
project/
│
├── main.py                     # main Streamlit app
│
├── pages/                      # other pages
├── data/                       # (optional) raw data files
├── requirements.txt
└── README.md
```

---

## 🛠 Development

To automatically reload Streamlit when files change:

```bash
streamlit run main.py --server.runOnSave=true
```

---

