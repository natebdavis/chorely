import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = "http://127.0.0.1:8000";

// --- Types ---
// This defines the shape of the logged-in user's data we store
type AuthUser = {
  userid: number | null;
  username: string;
  token: string;
};

// This defines what the context exposes to the rest of the app
type AuthContextValue = {
  user: AuthUser | null;       // null means nobody is logged in
  login: (username: string, password: string) => Promise<string | null>;  // returns error message or null on success
  logout: () => Promise<void>;
  isLoading: boolean;          // true while we're checking AsyncStorage on app start
};

// --- Create the context ---
// We start with undefined — if something tries to use this outside AuthProvider, it will throw
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// --- AuthProvider ---
// This wraps the app and holds the auth state
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true); // start true so we check storage before rendering

  // On app start, check if there's a saved token in AsyncStorage
  // This is what keeps the user logged in after closing the app
  useEffect(() => {
    async function loadStoredUser() {
      try {
        const stored = await AsyncStorage.getItem("auth_user");
        if (stored) {
          setUser(JSON.parse(stored)); // restore the user from storage
        }
      } catch (e) {
        // if storage fails, just start logged out
      } finally {
        setIsLoading(false);
      }
    }
    loadStoredUser();
  }, []);

  // login() is called by the login screen
  // It hits the backend, gets a token, then calls /auth/me to get the user's info
  const login = async (username: string, password: string): Promise<string | null> => {
    try {
      // Step 1: POST to /auth/login
      // The backend expects form data (not JSON) because it uses OAuth2PasswordRequestForm
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const tokenResponse = await fetch(`${API_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData.toString(),
      });

      if (!tokenResponse.ok) {
        return "Incorrect username or password";
      }

      const tokenData = await tokenResponse.json();
      const token = tokenData.access_token; // the JWT token

      // Step 2: GET /auth/me using the token to get userid and username
      // We pass the token in the Authorization header as "Bearer <token>"
      const meResponse = await fetch(`${API_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!meResponse.ok) {
        return "Failed to load user profile";
      }

      const meData = await meResponse.json();

      const authUser: AuthUser = {
        token,
        userid: meData.userid,
        username: meData.username,
      };

      // Step 3: Save to AsyncStorage so it persists after app closes
      await AsyncStorage.setItem("auth_user", JSON.stringify(authUser));

      // Step 4: Update state so the rest of the app knows who's logged in
      setUser(authUser);

      return null; // null means success, no error
    } catch (e) {
      return "Could not connect to the server";
    }
  };

  // logout() clears the stored user from both state and AsyncStorage
  const logout = async () => {
    await AsyncStorage.removeItem("auth_user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

// --- useAuth hook ---
// Any component that needs auth info calls useAuth() to get it
export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside an AuthProvider");
  }
  return context;
}
