# Run Project with Docker Compose

Run the Expo frontend and FastAPI backend in one command.

---

## 1. Prerequisites

- [Docker](https://www.docker.com/get-started)  
- [Docker Compose](https://docs.docker.com/compose/install/)  
- [Visual Studio Code](https://code.visualstudio.com/download)
- [Android Studio](https://developer.android.com/studio)
- [Node.js](https://nodejs.org/en/download)
- [Python](https://www.python.org/downloads/)

---

## 2. Set Environment Variables

- Copy the `.env` file into the project's root and backend folder.

## 3. Start the Project

- In Visual Studio Code open the root folder containing the project.

- Run the following command in terminal in the root folder to build and start both frontend and backend containers:

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

# Alternatives (Run Each Seperately):

---

# Run Backend Seperately

## 1. Start the Backend

- In Visual Studio Code open the root folder containing the project.

- Run the following commands in the terminal from the root folder to start the backend server.

```bash
cd backend

.venv\Scripts\activate

pip install -r requirements.txt

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 2. Interact with and view status of backend

- Go to http://127.0.0.1:8000/ to check if backend is running correctly

- Alternatively go to http://127.0.0.1:8000/docs#/ to be brought to a GUI to interact with each of the controller's methods

- For each method that has a lock symbol to its right, a user must be logged in and authorized to access these methods:

    * Create a dummy account using the `/user/create` function (click on the method and press try it out)
    * Get a session token by using the `/auth/login` function, output should be displayed on the bottom copy the string that says "access token"
    * Scroll up to the top of the screen and press button on the right that says `Authorize`, enter your credentials and paste the token in the last two fields

- All locked methods should be accessable. 

## 3. Stop the Backend

- In Visual Studio Terminal press `Ctrl` + `C`

# Run Frontend Seperately

## 1. Prepare Frontend

- In Visual Studio Code open the root folder containing the project.

- Run the following commands in the terminal from the root folder to start the frontend.

```bash
cd frontend

npm install
```

## 2. Prepare Android Emulator

- Launch Android Studio
- Go to Tools → Device Manager
- Click "Create Device"
- Choose a device (e.g., Pixel 4)
- Select a system image (recommended: API 30+)
- Click Finish
- Click the Play button next to your device

## 3. Start Expo

- In Visual Studio Code Run

```bash
npx expo start
```

- When Expo is finished building app press `a` in terminal to run it on emulator.

### Troubleshooting

- Expo CLI not Found, Run:

```bash
npm install -g expo-cli
```

- Andriod SDK not found
    * Make sure envirnoment variables are set in windows:
    ```bash
    ANDROID_HOME=C:\Users\<your-user>\AppData\Local\Android\Sdk
    ```
    * Add to PATH:
    ```bash
    %ANDROID_HOME%\platform-tools
    ```
    * [Useful Resource](https://www.java.com/en/download/help/path.html)







