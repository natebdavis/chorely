import {
  ImageBackground,
  ScrollView,
  StyleSheet,
  Text,
  View,
  Image, 
  Modal, 
  Pressable, 
  TouchableOpacity
} from "react-native";
import { useEffect, useState } from "react";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { ChoreItem } from "../../components/ChoreItem";
import type { Chore } from "../../components/ChoreContext";
import { useAuth } from "../../components/AuthContext";

type BackendChore = {
  choreid: number | null;
  name: string;
  description: string;
  request_date: number | null;
  due_date: number | null;
  assignee: string | null;
  status: string | null;
};

type Member = {
  userid: number;
  username: string;
  fname: string;
  lname: string;
};

const API_BASE = "https://chorely-beta-release.onrender.com";

function formatUnixTimestamp(timestamp: number | null) {
  if (!timestamp) {
    return "Unknown";
  }

  return new Date(timestamp * 1000).toLocaleString([], {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function ChoreBoard() {
  const {user, logout } = useAuth();
  const username = user?.username ?? "User";
  const userId = user?.userid ?? "N/A";
  const phone = user?.userid ?? "N/A"; //need to update to actual phone
  const email = user?.userid ?? "N/A"; //need to update to actual email

  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showSettingDropdown, setShowSettingDropdown] = useState(false);
  const [chores, setChores] = useState<Chore[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDropdownFor, setShowDropdownFor] = useState<string | null>(null);
  const [menuVisible, setMenuVisible] = useState(false);

  const handleStatusChange = async (choreId: string, newStatus: string, assigneeId?: number | null) => {
    try {
      const response = await fetch(`${API_BASE}/chores/${choreId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user?.token}`,
        },
        body: JSON.stringify({
          status: newStatus,
          assignee_id: assigneeId ?? null,
        }),
      });

      if (response.ok) {
        const assignedMember = members.find((m) => m.userid === assigneeId);
        setChores((prev) =>
          prev.map((c) =>
            c.id === choreId
              ? {
                  ...c,
                  status: newStatus,
                  assignedTo: assignedMember
                    ? `${assignedMember.fname} ${assignedMember.lname}`
                    : c.assignedTo,
                }
              : c
          )
        );
      }
    } catch (e) {
      // silently fail
    }
  };

  useEffect(() => {
    if (!user?.householdid) {
      setLoading(false);
      return;
    }

    async function loadChores() {
      try {
        const response = await fetch(`${API_BASE}/chores`, {
          headers: { Authorization: `Bearer ${user?.token}` },
        });

        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`);
        }

        const data: BackendChore[] = await response.json();
        setChores(
          data.map((backendChore) => ({
            id: String(
              backendChore.choreid ??
                `${backendChore.name}-${backendChore.due_date ?? "demo"}`
            ),
            name: backendChore.name,
            description: backendChore.description,
            assignedTo: backendChore.assignee ?? "Unassigned",
            requestDate: formatUnixTimestamp(backendChore.request_date),
            dueDate: formatUnixTimestamp(backendChore.due_date),
            status: backendChore.status ?? "Unknown",
          }))
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    async function loadMembers() {
      try {
        const response = await fetch(`${API_BASE}/households/members`, {
          headers: { Authorization: `Bearer ${user?.token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setMembers(data);
        }
      } catch (e) {
        // silently fail
      }
    }

    loadChores();
    loadMembers();
  }, []);

  return (
    <ImageBackground
      source={require("../../assets/images/background.png")}
      style={styles.background}
      resizeMode="cover"
    >

       <View style={styles.headerContainer}>
          <View style={styles.greetingContainer}>

            <TouchableOpacity onPress={() => setMenuVisible(true)} style={styles.avatarButton}>
              <Image
                source={require("../../assets/images/default_profile.png")}
                style={styles.avatar}
              />
            </TouchableOpacity>

             <Text style={styles.greetingText}>Hi, {username}</Text>
              
              <View style = {styles.headerSpacer} />
          </View>
           <Text style={styles.title}>Chore Board</Text>
        </View>


      <ScrollView contentContainerStyle={styles.container}>

        {!user?.householdid ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>No Household</Text>
            <Text style={styles.emptyText}>
              You must join a household to view chores.
            </Text>
          </View>
        ) : loading ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Loading chores...</Text>
          </View>
        ) : error ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Failed to load chores</Text>
            <Text style={styles.emptyText}>{error}</Text>
          </View>
        ) : chores.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>No chores yet</Text>
            <Text style={styles.emptyText}>
              Create a chore to get started.
            </Text>
          </View>
        ) : (
          chores.map((chore) => (
            <ChoreItem
              key={chore.id}
              chore={chore}
              onComplete={() => {}}
              onStatusChange={handleStatusChange}
              showDropdownFor={showDropdownFor}
              onToggleDropdown={setShowDropdownFor}
              members={members}
            />
          ))
        )}
      </ScrollView>
      
      <Modal
        visible={menuVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setMenuVisible(false)}
      >
        <Pressable
          style={styles.modalOverlay}
          onPress={() => setMenuVisible(false)}
        >
          <View style={styles.menuContainer}>

            <View style={styles.menuHeader}>
              <Image
                source={require("../../assets/images/default_profile.png")}
                style={styles.menuAvatar}
              />

              <Text style={styles.menuUsername}>Hello, {username}!</Text>
              <Text style={styles.menuId}>ID: {userId}</Text>

            </View>
            <View style={styles.divider} />


            <TouchableOpacity
              style={styles.menuItem}
              onPress={() => setShowProfileDropdown((prev) => !prev)}
            >
              <Ionicons name="person-outline" size={20} color="#fff" />
              <Text style={styles.menuText}>Personal Information</Text>

              <View style={{ marginLeft: "auto" }}>
                <Ionicons
                  name={showProfileDropdown ? "chevron-up-outline" : "chevron-down-outline"}
                  size={18}
                  color="#fff"
                />
              </View>
            </TouchableOpacity>

              {showProfileDropdown && (
                <View style={styles.profileDropdown}>
                  <Text style={styles.profileDetail}>
                    <Text style={styles.profileLabel}>Username: </Text>
                    {username}
                  </Text>

                  <Text style={styles.profileDetail}>
                    <Text style={styles.profileLabel}>Email: </Text>
                    {email}
                  </Text>

                  <Text style={styles.profileDetail}>
                    <Text style={styles.profileLabel}>Phone: </Text>
                    {phone}
                  </Text>

                  <Text style={styles.profileDetail}>
                    <Text style={styles.profileLabel}>User ID: </Text>
                    {userId}
                  </Text>
                </View>
              )}

            <TouchableOpacity
              style={styles.menuItem}
              onPress={() => setShowSettingDropdown((prev) => !prev)}
            >
              <Ionicons name="settings-outline" size={20} color="#fff" />
              <Text style={styles.menuText}>Edit Profile</Text>

              <View style={{ marginLeft: "auto" }}>
                <Ionicons
                  name={showSettingDropdown ? "chevron-up-outline" : "chevron-down-outline"}
                  size={18}
                  color="#fff"
                />
              </View>
            </TouchableOpacity>
            
            {showSettingDropdown && (
                <View style={styles.profileDropdown}>
                  <Text style={styles.profileDetail}>
                    <Text style={styles.profileLabel}>Change Username </Text>
                  </Text>

                  <Text style={styles.profileDetail}>
                    <Text style={styles.profileLabel}>Change Password </Text>
                  </Text>

                </View>
              )}

          <TouchableOpacity
                style={styles.menuItem}
                onPress={() => {
                setMenuVisible(false);
                router.push("/");
              }}
              >
              <Ionicons name="home-outline" size={20} color="#fff" />
              <Text style={styles.menuText}>Chore Board</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.menuItem}
                onPress={() => {
                setMenuVisible(false);
                router.push("/household");
                }}
              >
              <Ionicons name="home" size={20} color="#fff" />
              <Text style={styles.menuText}>Household</Text>
              </TouchableOpacity>


              <TouchableOpacity
              style={styles.menuItem}
                onPress={() => {
                setMenuVisible(false);
                router.push("/leaderboard");
                }}
              >
              <Ionicons name="trophy" size={20} color="#fff" />
              <Text style={styles.menuText}>Leaderboard</Text>
              </TouchableOpacity>


            <TouchableOpacity
              style={styles.menuItem}
              onPress={() => {
                setMenuVisible(false);
                router.push("/notifications");
              }}
            >
              <Ionicons name="notifications-outline" size={20} color="#fff" />
              <Text style={styles.menuText}>Notifications</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.menuItem}
              onPress={async () => {
                setMenuVisible(false);
                await logout();
                router.replace("/login");
              }}
            >
              <Ionicons name="log-out-outline" size={20} color="#ff8080" />
              <Text style={[styles.menuText, { color: "#ff8080" }]}>Logout</Text>
            </TouchableOpacity>
          </View>
        </Pressable>
      </Modal>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
  },
  container: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: 190,
    paddingBottom: 110,
  },
  title: {
    paddingTop: 15,
    fontSize: 30,
    fontWeight: "bold",
    alignSelf: "center", 
    color: "rgba(235, 235, 235, 0.92)",
    marginBottom: 10,
  },
  emptyState: {
    backgroundColor: "rgba(255, 255, 255, 0.92)",
    borderRadius: 20,
    padding: 24,
    alignItems: "center",
    marginTop: 20,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#111827",
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 14,
    lineHeight: 20,
    color: "#4B5563",
    textAlign: "center",
  },
  avatarButton: {
    width: 50,
    height: 50,
    borderRadius: 23,
    overflow: "hidden",
  },
  avatar: {
    width: "100%",
    height: "100%",
    borderRadius: 23,
    backgroundColor: "#333",
  },
  headerSpacer: {
    width: 46,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.35)",
    flexDirection: "row",
  },
  menuContainer: {
    width: "80%",
    height: "100%",
    backgroundColor: "#1C1C1E",
    paddingTop: 90,
    paddingHorizontal: 16,
    borderTopRightRadius: 20,
    borderBottomRightRadius: 20,
    borderRightWidth: 1,
    borderColor: "#2E2E32",
  },
  menuUsername: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 10,
    paddingHorizontal: 8,
    paddingTop: 30,
  },
  menuId: {
    color: "#fff",
    fontSize: 14,
    fontWeight: "700",
    marginBottom: 10,
    paddingHorizontal: 8,
    paddingTop: 30,
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 10,
  },
  menuText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "500",
  },
  menuHeader: {
    paddingTop: 40,
    alignItems: "center",   // centers horizontally
    justifyContent: "center",
    marginBottom: 25,
  },
  menuAvatar: {
    width: 90,
    height: 90,
    borderRadius: 40,
    marginBottom: 10,
    backgroundColor: "#333",
  },
  divider: {
    height: 2,
    backgroundColor: "#2E2E32",
    marginVertical: 10,
  },
  profileDropdown: {
    marginTop: 6,
    marginBottom: 10,
    marginHorizontal: 8,
    paddingVertical: 12,
    paddingHorizontal: 14,
    borderRadius: 12,
  },
  profileDetail: {
    color: "#fff",
    fontSize: 14,
    marginBottom: 8,
    lineHeight: 20,
  },
  profileLabel: {
    fontWeight: "700",
    color: "#4A90E2",
  },
  headerContainer: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    paddingTop: 60, // space for status bar
    paddingBottom: 16,
    paddingHorizontal: 20,
    zIndex: 10,
},
greetingContainer: {
  flexDirection: "row",
  alignItems: "center",
  backgroundColor: "#010b1f", 
  paddingVertical: 10,
  paddingHorizontal: 16,
  borderRadius: 999, 
  alignSelf: "flex-start", 
},
greetingText: {
  paddingLeft: 4, 
  color: "#fff",
  fontSize: 16,
  fontWeight: "600",
},
headerRow: {
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "space-between",
},
});
