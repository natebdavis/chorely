import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import AsyncStorage from "@react-native-async-storage/async-storage";

const API_URL = "https://chorely-beta-release.onrender.com";

type AuthUser = {
  userid: number | null;
  username: string;
  householdid: number | null;
  token: string;
  profile_url: string | null;
};

type AuthContextValue = {
  user: AuthUser | null;
  login: (username: string, password: string) => Promise<string | null>;
  logout: () => Promise<void>;
  isLoading: boolean;
  updateProfilePic: (profileUrl: string | null) => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // when app starts, restore saved session from AsyncStorage
  useEffect(() => {
    async function loadStoredUser() {
      try {
        const stored = await AsyncStorage.getItem("auth_user");
        if (stored) {
          setUser(JSON.parse(stored));
        }
      } catch (e) {
        // if storage fails, start logged out
      } finally {
        setIsLoading(false);
      }
    }
    loadStoredUser();
  }, []);

  const login = async (username: string, password: string): Promise<string | null> => {
    try {
      //POST /auth/login with form data to get JWT token
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
      const token = tokenData.access_token;

      // GET /user with token to get userid, username, householdid
      const meResponse = await fetch(`${API_URL}/user`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!meResponse.ok) {
        return "Failed to load user profile";
      }

      const meData = await meResponse.json();
      console.log("meData:", JSON.stringify(meData));//new testing

      let profileUrl: string | null = meData.profile_url ?? null; //new

      const picResponse = await fetch(`${API_URL}/user/profile-pic`, { //new
        headers: { Authorization: `Bearer ${token}` },//new
      });//new
      console.log("pic status:", picResponse.status);
      const picText = await picResponse.text();
      console.log("pic raw response:", picText);
      
      if (picResponse.ok) {//new
        //const picData = await picResponse.json();//new
        //profileUrl = picData.url ?? null;//new
        const picData = await picResponse.json();
        //console.log("pic data:", JSON.stringify(picData));
        console.log("picData full response:", JSON.stringify(picData));
        profileUrl = picData.url ?? null;
      }
      console.log("final profileUrl being saved:", profileUrl);


      const authUser: AuthUser = {
        token,
        userid: meData.userid,
        username: meData.username,
        householdid: meData.householdid ?? null,
        profile_url: meData.profile_url ?? null,
      };

      // save to AsyncStorage so session doesnt end when app is closed
      await AsyncStorage.setItem("auth_user", JSON.stringify(authUser));
      setUser(authUser);

      return null; // null = success
    } catch (e) {
      return "Could not connect to the server";
    }
  };

    const updateProfilePic = async (profileUrl: string | null) => {//new
    setUser((prevUser) => {
      if (!prevUser) return prevUser;

      const updatedUser = {
        ...prevUser,
        profile_url: profileUrl,
      };

      AsyncStorage.setItem("auth_user", JSON.stringify(updatedUser));

      return updatedUser;
    });//new
  };

  const logout = async () => {
    await AsyncStorage.removeItem("auth_user");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading, updateProfilePic }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside an AuthProvider");
  }
  return context;
}
