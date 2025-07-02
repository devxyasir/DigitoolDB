# 📦 DigitoolDB

> A lightweight, beginner-friendly, document-oriented NoSQL database inspired by MongoDB — built in pure Python by [Jam Yasir](https://devsecure.netlify.app). Ideal for learning, rapid prototyping, and local application development.

---

## 🧠 Overview

**DigitoolDB** is a custom-built NoSQL-style database system, designed for local environments and written entirely in Python. It mimics MongoDB's document-oriented structure while remaining dependency-free and simple to use. Whether you're building educational projects, testing backend systems, or learning how databases work under the hood — DigitoolDB is a great starting point.

---

## 🚀 Key Features

- 📄 **MongoDB-like JSON document structure**
- 🐍 **Pure Python implementation** (no external database dependencies)
- 🧪 **Beginner-friendly Simple API**
- 🖥️ **Full Command Line Interface (`digi`)**
- 🧰 **REST interface (optional) for web usage**
- 🚀 **Built-in indexing** for faster querying
- 🛠️ **Modular Design** — extend or replace any part easily
- 💾 **Runs as a local daemon (`digid`)**
- 🔐 **Safe Local Storage** — perfect for isolated development

---

## 📁 Directory Structure

```

DigitoolDB/
├── src/
│   ├── server/      # digid server implementation
│   ├── client/      # digi CLI and API
│   └── common/      # shared utilities
├── config/          # configuration files
├── data/            # local database storage
├── tests/           # unit & integration tests
├── docs/            # documentation and guides
└── scripts/         # install & setup scripts

```

---

## 🛠 Installation

1. Make sure you have **Python 3.8+** installed
2. Clone the repo:
   ```bash
   git clone https://github.com/devxyasir/DigitoolDB.git
   cd DigitoolDB
```

3. Install (standard mode):

   ```bash
   pip install -r requirements.txt
   python setup.py install
   ```

> ✅ No MongoDB or external NoSQL engine required — everything runs natively.

---

## 🧪 Usage Examples

### ✅ Using the Simple Python API

```python
from src.client.simple_api import SimpleDB

with SimpleDB() as db:
    db.create_db('mydb')
    users = db.db('mydb').collection('users')
    users.insert({'name': 'Yasir', 'role': 'Developer'})
    print(users.find({'role': 'Developer'}))
```

---

### ⚙️ Using the Programmatic Client API

```python
from src.client.client import DigitoolDBClient

client = DigitoolDBClient()
client.connect()

client.create_database('mydb')
client.create_collection('mydb', 'users')
client.insert('mydb', 'users', {'name': 'Yasir'})
print(client.find('mydb', 'users', {'name': 'Yasir'}))

client.disconnect()
```

---

### 📡 Starting the Server

```bash
digid --config config/digid.conf
```

---

### 🧾 CLI Commands

```bash
# Insert a document
digi insert users '{"name": "Yasir"}'

# Query a document
digi find users '{"name": "Yasir"}'

# Update a document
digi update users '{"name": "Yasir"}' '{"$set": {"age": 30}}'

# Delete a document
digi delete users '{"name": "Yasir"}'
```

---

## ⚙️ Configuration

Configuration file example:

```json
{
  "data_dir": "./data",
  "port": 6543,
  "log_level": "INFO"
}
```

Location: `config/digid.conf` or use custom path with `--config`.

---

## 📚 Documentation

* [📘 Getting Started Guide](docs/getting_started.md)
* [🎓 Beginner's Guide](docs/beginners_guide.md)
* [📎 CLI Cheat Sheet](docs/cheat_sheet.md)
* [❓ FAQ](docs/faq.md)

---

## 🎉 Example Apps

| Name                  | Description                              |
| --------------------- | ---------------------------------------- |
| Simple API Demo       | Insert, query, update, delete via Python |
| Todo App              | Build a full-featured todo list app      |
| Data Analysis App     | Load and query structured data           |
| Web Dashboard (Flask) | Interface with DigitoolDB from a browser |

Check the `examples/` directory for code.

---

## 🧑‍💻 Author

**Jam Yasir** – AI & ML Engineer, Web & Security Developer
📍 Lodhran, Punjab, Pakistan
🌐 [Portfolio](https://devsecure.netlify.app)
📧 [jamyasir0534@gmail.com](mailto:jamyasir0534@gmail.com)
🔗 [GitHub](https://github.com/devxyasir) | [Hugging Face](https://huggingface.co/devxyasir)

---

## 🤝 Contributions

Pull requests are welcome! Whether you're fixing bugs, improving documentation, or adding features — your contributions help make this project even better.

To get started:

```bash
git clone https://github.com/devxyasir/DigitoolDB.git
git checkout -b your-feature-branch
```

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙌 A Message from the Author

> DigitoolDB was created to demystify the internals of NoSQL databases for learners, hobbyists, and Python developers. It’s intentionally minimal, yet extendable. Dive in, tweak it, break it, rebuild it — and most importantly, learn from it. 💡
>
> — *Jam Yasir (DevSecure)*

---
