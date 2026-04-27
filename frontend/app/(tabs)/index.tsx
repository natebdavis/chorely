import {
  ImageBackground,
  ScrollView,
  StyleSheet,
  Text,
  View,
  Image,
  Modal,
  Pressable,
  TouchableOpacity,
  Alert,
} from "react-native";
import { useEffect, useState, useCallback } from "react";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { ChoreItem } from "../../components/ChoreItem";
import type { Chore } from "../../components/ChoreContext";
import { useAuth } from "../../components/AuthContext";
import * as ImagePicker from "expo-image-picker";



type BackendChore = {
  choreid: number | null;
  name: string;
  description: string;
  request_date: string | null;
  due_date: string | null;
  assignee: string | null;
  status: string | null;
};

type Member = {
  userid: number;
  username: string;
  fname: string;
  lname: string;
};

//const API_BASE = "https://chorely-beta-release.onrender.com";
//const API_BASE = "http://127.0.0.1:8000"
const API_BASE = "https://chorely-final-1v-release.onrender.com"

function formatISODate(isoString: string | null) {
  if (!isoString) return "Unknown";
  return new Date(isoString).toLocaleString([], {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function ChoreBoard() {
  const {user, logout,updateProfilePic } = useAuth();
  const username = user?.username ?? "User";
  const userId = user?.userid ?? "N/A";
  const phone = user?.phone_num ?? "N/A"; 
  const email = user?.email ?? "N/A";

  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showSettingDropdown, setShowSettingDropdown] = useState(false);
  const [chores, setChores] = useState<Chore[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDropdownFor, setShowDropdownFor] = useState<string | null>(null);
  const [menuVisible, setMenuVisible] = useState(false);
  const [selectedDate, setSelectedDate] = useState<Date | null>(new Date());
  const [weekOffset, setWeekOffset] = useState(0);
  const [overdueOnly, setOverdueOnly] = useState(false);

  const getWeekDates = useCallback((offset: number): Date[] => {
    const today = new Date();
    const dayOfWeek = today.getDay();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - dayOfWeek + offset * 7);
    startOfWeek.setHours(0, 0, 0, 0);
    return Array.from({ length: 7 }, (_, i) => {
      const d = new Date(startOfWeek);
      d.setDate(startOfWeek.getDate() + i);
      return d;
    });
  }, []);

  const isSameDay = (a: Date, b: Date) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();

  const weekDates = getWeekDates(weekOffset);
  const today = new Date();

  const filteredChores = overdueOnly
    ? chores.filter((c) => {
        if (!c.dueDateTimestamp) return false;
        if (c.status === "COMPLETE") return false;
        return new Date(c.dueDateTimestamp) < new Date();
      })
    : selectedDate
    ? chores.filter((c) => {
        if (!c.dueDateTimestamp) return false;
        const choreDate = new Date(c.dueDateTimestamp);
        return isSameDay(choreDate, selectedDate);
      })
    : chores;

  const DAY_LABELS = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
  const MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

  const profileImageSource = user?.profile_url
  ? { uri: user.profile_url }
  : require("../../assets/images/default_profile.png"); 

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
            requestDate: formatISODate(backendChore.request_date),
            dueDate: formatISODate(backendChore.due_date),
            dueDateTimestamp: backendChore.due_date,
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

  const handleUploadProfilePic = async () => {
  const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();

  if (!permission.granted) {
    Alert.alert("Permission Required", "Please allow photo access.");
    return;
  }

  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ['images'],
    allowsEditing: true,
    aspect: [1, 1],
    quality: 0.8,
  });

  if (result.canceled) return;

  const image = result.assets[0];

  const formData = new FormData();

  formData.append("file", {
    uri: image.uri,
    name: "profile.jpg",
    type: "image/jpeg",
  } as any);

  try {
    const response = await fetch(`${API_BASE}/user/upload-image`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${user?.token}`,
        "Content-Type": "multipart/form-data",
      },
      body: formData,
    });

    if (!response.ok) {
      Alert.alert("Error", "Failed to upload profile picture.");
      return;
    }

    // const data = await response.json();//testing
    // console.log("upload response:", JSON.stringify(data));  // add this to see what comes back
    // updateProfilePic(data.url ?? data.profile_url ?? data.image_url ?? null);//testing

    const picResponse = await fetch(`${API_BASE}/user/profile-pic`, {
      headers: {
        Authorization: `Bearer ${user?.token}`,
      },
    });

    if (picResponse.ok) {
      const picData = await picResponse.json();
      updateProfilePic(picData.url);
    }

    //const data = await response.json();

   // updateProfilePic(data.url ?? data.profile_url ?? null);

    Alert.alert("Success", "Profile picture updated.");
  } catch (error) {
    console.log("Upload profile picture error:", error);
    Alert.alert("Error", "Something went wrong while uploading.");
  }
};


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
                //source={require("../../assets/images/default_profile.png")}
                source={profileImageSource}
                style={styles.avatar}
              />
            </TouchableOpacity>

             <Text style={styles.greetingText}>Hi, {username}</Text>
              
          </View>
           <Text style={styles.title}>
            {overdueOnly
              ? "Overdue Chores"
              : selectedDate
              ? isSameDay(selectedDate, today)
                ? "Today's Chores"
                : selectedDate.toLocaleDateString([], { weekday: "long", month: "short", day: "numeric" })
              : "All Chores"}
          </Text>

        <View style={styles.calendarStrip}>
          <View style={styles.calendarNav}>
            <TouchableOpacity onPress={() => setWeekOffset((w) => w - 1)} style={styles.navArrow}>
              <Text style={styles.navArrowText}>‹</Text>
            </TouchableOpacity>
            <Text style={styles.calendarMonth}>
              {MONTH_NAMES[weekDates[0].getMonth()]} {weekDates[0].getFullYear()}
              {weekDates[0].getMonth() !== weekDates[6].getMonth()
                ? ` – ${MONTH_NAMES[weekDates[6].getMonth()]}`
                : ""}
            </Text>
            <TouchableOpacity onPress={() => setWeekOffset((w) => w + 1)} style={styles.navArrow}>
              <Text style={styles.navArrowText}>›</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => { setSelectedDate(null); setOverdueOnly(false); }}
              style={[styles.allButton, !selectedDate && !overdueOnly && styles.allButtonActive]}
            >
              <Text style={styles.allButtonText}>All</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => { setOverdueOnly((v) => !v); setSelectedDate(null); }}
              style={[styles.allButton, overdueOnly && styles.overdueButtonActive]}
            >
              <Text style={styles.allButtonText}>Overdue</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.calendarDays}>
            {weekDates.map((date, i) => {
              const isSelected = selectedDate ? isSameDay(date, selectedDate) : false;
              const isToday = isSameDay(date, today);
              return (
                <TouchableOpacity
                  key={i}
                  style={[styles.dayCell, isSelected && styles.dayCellSelected]}
                  onPress={() => {
                    setOverdueOnly(false);
                    setSelectedDate((prev) =>
                      prev && isSameDay(prev, date) ? null : date
                    );
                  }}
                >
                  <Text style={[styles.dayLabel, isSelected && styles.dayLabelSelected]}>
                    {DAY_LABELS[date.getDay()]}
                  </Text>
                  <Text style={[styles.dayNumber, isSelected && styles.dayNumberSelected]}>
                    {date.getDate()}
                  </Text>
                  {isToday && !isSelected && <View style={styles.todayDot} />}
                </TouchableOpacity>
              );
            })}
          </View>
        </View>
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
        ) : filteredChores.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>
              {overdueOnly
                ? "No overdue chores"
                : selectedDate
                ? "No chores on this day"
                : "No chores yet"}
            </Text>
            <Text style={styles.emptyText}>
              {overdueOnly
                ? "Nothing's past due — nice."
                : selectedDate
                ? "Try selecting a different date or tap All to see everything."
                : "Create a chore to get started."}
            </Text>
          </View>
        ) : (
          filteredChores.map((chore) => (
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
              <TouchableOpacity onPress={handleUploadProfilePic} style={styles.menuAvatarWrapper}>
                <Image source={profileImageSource} style={styles.menuAvatar} />

                <View style={styles.menuEditPencil}>
                  <Ionicons name="pencil" size={14} color="#fff" />
                </View>
              </TouchableOpacity>

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
    paddingTop: 290,
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
    borderRadius: 45,
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
    paddingTop: 60,
    paddingBottom: 12,
    paddingHorizontal: 20,
    zIndex: 10,
  },
  calendarStrip: {
    marginTop: 10,
    backgroundColor: "rgba(1, 11, 31, 0.85)",
    borderRadius: 16,
    paddingVertical: 8,
    paddingHorizontal: 8,
  },
  calendarNav: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 6,
    paddingHorizontal: 4,
  },
  navArrow: {
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  navArrowText: {
    color: "#fff",
    fontSize: 22,
    fontWeight: "300",
  },
  calendarMonth: {
    flex: 1,
    color: "#fff",
    fontSize: 13,
    fontWeight: "600",
    textAlign: "center",
  },
  allButton: {
    backgroundColor: "rgba(255,255,255,0.15)",
    borderRadius: 10,
    paddingHorizontal: 10,
    paddingVertical: 3,
    marginLeft: 6,
  },
  allButtonActive: {
    backgroundColor: "#4A90E2",
  },
  overdueButtonActive: {
    backgroundColor: "#E14B4B",
  },
  allButtonText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "700",
  },
  calendarDays: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  dayCell: {
    flex: 1,
    alignItems: "center",
    paddingVertical: 6,
    borderRadius: 10,
  },
  dayCellSelected: {
    backgroundColor: "#4A90E2",
  },
  dayLabel: {
    color: "rgba(255,255,255,0.55)",
    fontSize: 11,
    fontWeight: "500",
    marginBottom: 2,
  },
  dayLabelSelected: {
    color: "#fff",
  },
  dayNumber: {
    color: "#fff",
    fontSize: 15,
    fontWeight: "600",
  },
  dayNumberSelected: {
    color: "#fff",
  },
  todayDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: "#4A90E2",
    marginTop: 2,
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
menuAvatarWrapper: {
  width: 90,
  height: 90,
  borderRadius: 45,
  marginBottom: 10,
  position: "relative",
},
menuEditPencil: {
  position: "absolute",
  right: 0,
  bottom: 0,
  width: 26,
  height: 26,
  borderRadius: 13,
  backgroundColor: "#4A90E2",
  alignItems: "center",
  justifyContent: "center",
  borderWidth: 2,
  borderColor: "#1C1C1E",
},
});
