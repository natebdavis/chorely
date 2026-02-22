# Run Project with Docker Compose

Run the Expo frontend and FastAPI backend in one command.

---

## 1. Prerequisites

- [Docker](https://www.docker.com/get-started)  
- [Docker Compose](https://docs.docker.com/compose/install/)  
- Optional: [Expo Go](https://expo.dev/client) on your phone  

---

## 2. Set Environment Variables

- Copy the `.env` file into the project's root folder.

## 3. Start the Project

Run the following command in the root folder to build and start both frontend and backend containers:

```bash
docker-compose up --build
```

* **Backend API:** http://localhost:8000
* **Frontend (Expo DevTools):** http://localhost:19002
* **Expo Go on phone:**
  * Scan the QR code shown in DevTools
  * Make sure your phone is on the same network as your computer
* **Hot Reload:** Both backend and frontend code changes will automatically reload.

## 4. Stop the Project

To stop and remove the containers:

```bash
docker-compose down
```

* This stops both backend and frontend containers
* Removes containers from Docker, but keeps images for faster rebuilds

