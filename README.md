# TaskFlow

TaskFlow is a real-time collaborative task board (similar to Trello) designed to demonstrate authentication, RESTful APIs, and WebSocket-based real-time updates working together in a single cohesive application.

## Tech Stack
* **Framework:** FastAPI
* **Database:** SQLite (via aiosqlite for async support)
* **ORM:** SQLAlchemy (Async)
* **Migrations:** Alembic
* **Authentication:** JWT (JSON Web Tokens) with bcrypt password hashing

## Features
* **Secure Authentication:** User signup and login utilizing JWT.
* **Role-Based Access Control (RBAC):** Board members can be `OWNER`, `MEMBER`, or `VIEWER`. 
* **REST API:** Create, read, update, and delete boards and tasks.
* **Real-time WebSockets:** Any changes to tasks (create/update/delete) are instantly broadcasted to all active users viewing that specific board.

---

## Prerequisites
* Python 3.13+ 
* Optional: A REST client like Postman or Insomnia, or you can use the built-in Swagger UI.

---

## Local Setup

**1. Clone or navigate to the project directory**
```bash
cd taskflow
```

**2. Create a virtual environment**
```bash
python3 -m venv venv
```

**3. Activate the virtual environment**
* On **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```
* On **Windows**:
  ```bash
  venv\Scripts\activate
  ```

**4. Install dependencies**
```bash
pip install -r requirements.txt
```

**5. Set up the database**
This project uses Alembic for database migrations. To create the SQLite database (`taskflow.db`) and apply the initial schema, run:
```bash
alembic upgrade head
```

---

## Running the Application

To start the FastAPI development server, run:
```bash
uvicorn app.main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

---

## Using the API & WebSockets

### REST API Documentation
FastAPI automatically generates interactive API documentation. Once the server is running, visit:
* **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

You can use the **Authorize** button in the top right of the Swagger UI to log in. Under the hood, this hits the `/api/v1/auth/login` endpoint and stores your JWT token for subsequent requests.

### WebSocket Connections
To receive real-time updates for a board, connect a WebSocket client to:
```text
ws://127.0.0.1:8000/ws/boards/{board_id}?token={your_jwt_token}
```
* **Security Note:** You must pass a valid JWT token via the query string. The server will reject the connection if the token is invalid or if you are not a member of the requested `board_id`.
* **Data Flow:** WebSockets are strictly read-only feeds. Perform mutations (create/edit tasks) via the REST API; the WebSocket server will automatically push a JSON event downstream to all connected clients.

---

## Project Structure

```text
taskflow/
├── app/
│   ├── main.py              # Application entry point
│   ├── core/                # Settings, Security, DB session
│   ├── models/              # SQLAlchemy database tables
│   ├── schemas/             # Pydantic validation models
│   ├── api/                 # REST endpoints (auth, boards, tasks)
│   └── websockets/          # WebSocket connection manager & routes
├── tests/                   # Pytest test suite
├── alembic/                 # Database migration scripts
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```
