# Run Project with Docker Compose

Run the Expo frontend and FastAPI backend in one command.

---

## 1. Prerequisites

- [Docker](https://www.docker.com/get-started)  
- [Docker Compose](https://docs.docker.com/compose/install/)  

---

## 2. Set Environment Variables

- Copy the `.env` file into the project's root folder.

## 3. Start the Project

Run the following command in the root folder to build and start both frontend and backend containers:

```bash
docker-compose up --build
```

* **Backend API:** http://localhost:8000
* **Frontend (Expo DevTools):** http://localhost:8081
* **Hot Reload:** Both backend and frontend code changes will automatically reload.

## 4. Stop the Project

To stop and remove the containers:

```bash
docker-compose down
```

* This stops both backend and frontend containers
* Removes containers from Docker, but keeps images for faster rebuilds

## Notes:

Don't know how to get Expo Go Running. Can still run App with Android Emulator.

