import { useState, useEffect } from "react";
import {
  Image,
  ImageBackground,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
  Alert,
  FlatList,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useAuth } from "../../components/AuthContext";
//const API_URL = "http://10.0.0.7:8000"
const API_URL = "http://127.0.0.1:8000"

export default function NotificationsScreen() {
  const { user, logout } = useAuth();
  const token = user?.token;

  const username = user?.username ?? "User";
  const userId = user?.userid ?? "N/A";
  const phone = user?.userid ?? "N/A"; //need to update to actual phone
  const email = user?.userid ?? "N/A"; //need to update to actual email

  const [menuVisible, setMenuVisible] = useState(false);
  const [activeTab, setActiveTab] = useState<"inbox" | "sent">("inbox");
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showSettingDropdown, setShowSettingDropdown] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [sentInvites, setSentInvites] = useState<SentInviteItem[]>([]);
  const [inviteStatuses, setInviteStatuses] = useState<Record<number, string>>({});

  type NotificationItem = {
  notificationid: number;
  userid: number;
  type: string;
  title: string;
  message: string;
  reference_id: number | null;
  time: string;
  is_read: boolean;
};

type SentInviteItem = {
  inviteid: number;
  householdid: number;
  inviter_userid: number;
  invitee_userid: number;
  status: string;
  created_at: string;
  responded_at: string | null;
};

const formatTime = (isoString: string) => {
  const date = new Date(isoString);

  return date.toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
};

const getDisplayTime = (item: SentInviteItem) => {
  if (item.responded_at) {
    return `Responded: ${formatTime(item.responded_at)}`;
  }
  return `Sent: ${formatTime(item.created_at)}`;
};

    const fetchNotifications = async () => {
      if (!token) return;

      try {
        const response = await fetch(`${API_URL}/notifications`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await response.json();

        if (response.ok) {
          setNotifications(data);
        }
      } catch (error) {
        console.log("Notification fetch error:", error);
      }
    };


  const fetchSentInvites = async () => {
    if (!token) 
      return;

    try {
      const response = await fetch(`${API_URL}/invites/outgoing`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

     if (response.ok) {
      const onlyMySentInvites = data.filter(
        (invite: SentInviteItem) => Number(invite.inviter_userid) === Number(user?.userid)
      );

      setSentInvites(onlyMySentInvites);
      } else {
        console.log("Sent invite error:", data);
      }
    } catch (error) {
      console.log("Error fetching sent invites:", error);
    }
  };

  useEffect(() => {
    if (activeTab === "sent") {
      fetchSentInvites();
      fetchNotifications();
      fetchInviteHistory();
     
       //fetchPendingInvites();
    }
  }, [activeTab, token]);


  const handleAcceptInvite = async (inviteid: number) => {
  if (!token) return;

  try {
    const response = await fetch(`${API_URL}/invites/${inviteid}/accept`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (response.ok) {
      Alert.alert("Success", "Invite accepted!");

      setInviteStatuses((prev) => ({...prev, [inviteid]: "ACCEPTED",}));

      setNotifications((prev) =>
        prev.map((item) =>
          item.reference_id === inviteid
            ? {
                ...item,
                type: "INVITE_ACCEPTED",
                title: "Invite Accepted",
                message: "You accepted this household invite.",
              }
            : item
        )
      );
    } else {
      Alert.alert("Error", data.detail || "Failed to accept invite.");
    }
  } catch (error) {
    console.log("Accept invite error:", error);
    Alert.alert("Error", "Something went wrong.");
  }
};


const handleCancelInvite = async (inviteid: number) => {
  if (!token) return;

  try {
    const response = await fetch(`${API_URL}/invites/${inviteid}/cancel`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (response.ok) {
      Alert.alert("Success", "Invite canceled.");

      setSentInvites((prev) =>
        prev.map((invite) =>
          invite.inviteid === inviteid
            ? { ...invite, status: "CANCELED" }
            : invite
        )
      );

    } else {
      Alert.alert("Error", data.detail || "Failed to cancel invite.");
    }
  } catch (error) {
    console.log("Cancel invite error:", error);
    Alert.alert("Error", "Something went wrong.");
  }
};



const handleDeclineInvite = async (inviteid: number) => {
  if (!token) return;

  try {
    const response = await fetch(`${API_URL}/invites/${inviteid}/decline`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (response.ok) {
      Alert.alert("Success", "Invite declined.");
      setInviteStatuses((prev) => ({...prev, [inviteid]: "DECLINED",}));

      setNotifications((prev) =>
        prev.map((item) =>
          item.reference_id === inviteid
            ? {
                ...item,
                type: "INVITE_DECLINED",
                title: "Invite Declined",
                message: "You declined this household invite.",
              }
            : item
        )
      );
    } else {
      Alert.alert("Error", data.detail || "Failed to decline invite.");
    }
  } catch (error) {
    console.log("Decline invite error:", error);
    Alert.alert("Error", "Something went wrong.");
  }
};

// const fetchPendingInvites = async () => {
//   if (!token) return;

//   try {
//     const response = await fetch(`${API_URL}/invites`, {
//       headers: {
//         Authorization: `Bearer ${token}`,
//       },
//     });

//     const data = await response.json();

//     if (response.ok) {
//       const statusMap: Record<number, string> = {};

//       data.forEach((invite: SentInviteItem) => {
//         statusMap[invite.inviteid] = invite.status;
//       });

//       setInviteStatuses(statusMap);
//     }
//   } catch (error) {
//     console.log("Pending invite fetch error:", error);
//   }
// };

const fetchInviteHistory = async () => {
  if (!token) return;

  try {
    const response = await fetch(`${API_URL}/invites/history`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (response.ok) {
      const statusMap: Record<number, string> = {};

      data.forEach((invite: SentInviteItem) => {
        statusMap[invite.inviteid] = invite.status;
      });

      setInviteStatuses(statusMap);
    } else {
      console.log("Invite history error:", data);
    }
  } catch (error) {
    console.log("Invite history fetch error:", error);
  }
};

useEffect(() => {
  fetchNotifications();
  fetchInviteHistory();
}, [token]);

const handleDeleteNotification = async (notificationid: number) => {
  if (!token) return;

  try {
    const response = await fetch(`${API_URL}/notifications/${notificationid}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();

    if (response.ok) {
      setNotifications((prev) =>
        prev.filter((item) => item.notificationid !== notificationid)
      );
    } else {
      Alert.alert("Error", data.detail || "Failed to delete notification.");
    }
  } catch (error) {
    console.log("Delete notification error:", error);
    Alert.alert("Error", "Something went wrong.");
  }
};

const handleDeleteSentInvite = async (inviteid: number) => {
  Alert.alert(
    "Delete Sent Invite",
    "Are you sure you want to delete this sent invite from your history?",
    [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          setSentInvites((prev) =>
            prev.filter((item) => item.inviteid !== inviteid)
          );
        },
      },
    ]
  );
};

  return (
    <ImageBackground
      source={require("../../assets/images/background.png")}
      style={styles.background}
      resizeMode="cover"
    >
      <View style={styles.headerContainer}>
        <View style={styles.greetingContainer}>
          <TouchableOpacity
            onPress={() => setMenuVisible(true)}
            style={styles.avatarButton}
          >
            <Image
              source={require("../../assets/images/default_profile.png")}
              style={styles.avatar}
            />
          </TouchableOpacity>

          <Text style={styles.greetingText}>Hi, {username}</Text>
        </View>

        <Text style={styles.title}>Notifications</Text>
      </View>

      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.tabContainer}>
          <TouchableOpacity
            style={[styles.tabButton, activeTab === "inbox" && styles.activeTab]}
            onPress={() => setActiveTab("inbox")}
          >
            <Text
              style={[
                styles.tabText,
                activeTab === "inbox" && styles.activeTabText,
              ]}
            >
              Inbox
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tabButton, activeTab === "sent" && styles.activeTab]}
            onPress={() => setActiveTab("sent")}
          >
            <Text
              style={[
                styles.tabText,
                activeTab === "sent" && styles.activeTabText,
              ]}
            >
              Sent
            </Text>
          </TouchableOpacity>
        </View>

          {activeTab === "sent" ? (
            sentInvites.length === 0 ? (
              <View style={styles.emptyCard}>
                <Ionicons name="paper-plane-outline" size={42} color="#4A90E2" />

                <Text style={styles.emptyTitle}>No sent notifications yet</Text>

                <Text style={styles.emptyText}>
                  Invites and requests you send to others will appear here.
                </Text>
              </View>
            ) : (
              sentInvites.map((item) => (
                <View key={item.inviteid} style={styles.notificationCard}>
                  <Text style={styles.notificationTitle}>Household Invite Sent</Text>

                  <Text style={styles.notificationMessage}>  Invite sent to User ID: {item.invitee_userid} </Text>
                  <Text style={styles.timeText}>{getDisplayTime(item)} </Text>

                  <Text style={styles.statusText}>Status: {item.status}</Text>
                    {item.status === "PENDING" ? (
                      <TouchableOpacity
                        style={[styles.cancelInviteButton, styles.declineButton]}
                        onPress={() => handleCancelInvite(item.inviteid)}
                      >
                        <Text style={styles.inviteButtonText}>Cancel Invite</Text>
                      </TouchableOpacity>
                    ) : item.status === "CANCELED" ? (
                      <Text style={styles.declinedStatus}>Canceled</Text>
                    ) : item.status === "ACCEPTED" ? (
                      <Text style={styles.acceptedStatus}>Accepted</Text>
                    ) : item.status === "DECLINED" ? (
                      <Text style={styles.declinedStatus}>Declined</Text>
                    ) : null}
                </View>
              ))
            )

        )  : notifications.length === 0 ? (
          <View style={styles.emptyCard}>
            <Ionicons name="mail-outline" size={42} color="#4A90E2" />

            <Text style={styles.emptyTitle}>No inbox notifications yet</Text>

            <Text style={styles.emptyText}>
              Invites, chore requests, and updates you receive will appear here.
            </Text>
          </View>
       ) : (
    notifications.map((item) => (
      <View key={item.notificationid} style={styles.notificationCard}>
        
       <View style={styles.notificationHeader}>
          <Text style={styles.notificationTitle}>{item.title}</Text>

          <TouchableOpacity
            onPress={() => handleDeleteNotification(item.notificationid)}
          >
            <Ionicons name="trash-outline" size={22} color="#dc2626" />
          </TouchableOpacity>
        </View>


        <Text style={styles.notificationMessage}>{item.message}</Text>
        <Text style={styles.timeText}>{formatTime(item.time)}</Text>

        {item.type === "INVITE" && item.reference_id !== null && inviteStatuses[item.reference_id] === "PENDING" ? (
        
    
        
        <View style={styles.inviteButtonRow}>
          <TouchableOpacity
            style={[styles.inviteButton, styles.acceptButton]}
            onPress={() => handleAcceptInvite(item.reference_id!)}
          >
            <Text style={styles.inviteButtonText}>Accept</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.inviteButton, styles.declineButton]}
            onPress={() => handleDeclineInvite(item.reference_id!)}
          >
            <Text style={styles.inviteButtonText}>Decline</Text>
          </TouchableOpacity>
        </View>
          ) : item.reference_id !== null &&
              inviteStatuses[item.reference_id] === "DECLINED" ? (
            <Text style={styles.declinedStatus}>Declined</Text>
          ) : item.reference_id !== null &&
              inviteStatuses[item.reference_id] === "ACCEPTED" ? (
            <Text style={styles.acceptedStatus}>Accepted</Text>
          ) : null}
    </View>
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
          <Pressable style={styles.menuContainer}>
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
                  name={showProfileDropdown? "chevron-up-outline": "chevron-down-outline"}
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
              <Text style={[styles.menuText, { color: "#ff8080" }]}>
                Logout
              </Text>
            </TouchableOpacity>
          </Pressable>
        </Pressable>
      </Modal>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
  },
  headerContainer: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    paddingTop: 60,
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
  avatarButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    overflow: "hidden",
  },
  avatar: {
    width: "100%",
    height: "100%",
    borderRadius: 23,
    backgroundColor: "#333",
  },
  greetingText: {
    paddingLeft: 4,
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  title: {
    paddingTop: 15,
    fontSize: 30,
    fontWeight: "bold",
    alignSelf: "center",
    color: "rgba(235, 235, 235, 0.92)",
  },
  container: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: 190,
    paddingBottom: 110,
  },
  tabContainer: {
    flexDirection: "row",
    backgroundColor: "rgba(1, 11, 31, 0.85)",
    borderRadius: 16,
    padding: 6,
    marginBottom: 24,
  },
  tabButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  activeTab: {
    backgroundColor: "#4A90E2",
  },
  tabText: {
    color: "#cbd5e1",
    fontSize: 16,
    fontWeight: "700",
  },
  activeTabText: {
    color: "#fff",
  },
  emptyCard: {
    backgroundColor: "rgba(255, 255, 255, 0.92)",
    borderRadius: 22,
    padding: 28,
    alignItems: "center",
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#111827",
    marginTop: 14,
    marginBottom: 8,
    textAlign: "center",
  },
  emptyText: {
    fontSize: 14,
    lineHeight: 20,
    color: "#4B5563",
    textAlign: "center",
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
  menuHeader: {
    paddingTop: 40,
    alignItems: "center",
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
  menuUsername: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 8,
  },
  menuId: {
    color: "#cbd5e1",
    fontSize: 14,
    fontWeight: "700",
    marginBottom: 10,
    paddingHorizontal: 8,
    paddingTop: 30,
  },
  divider: {
    height: 2,
    backgroundColor: "#2E2E32",
    marginVertical: 10,
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
  notificationCard: {
    backgroundColor: "white",
    padding: 14,
    borderRadius: 10,
    marginBottom: 12,
},
notificationTitle: {
  fontSize: 16,
  fontWeight: "700",
  color: "#111",
},
notificationMessage: {
  fontSize: 14,
  color: "#555",
  marginTop: 4,
},
inviteButtonRow: {
  flexDirection: "row",
  gap: 10,
  marginTop: 14,
},
inviteButton: {
  flex: 1,
  paddingVertical: 10,
  borderRadius: 10,
  alignItems: "center",
},
cancelInviteButton:{
  marginTop: 10,
  flex: 1,
  paddingVertical: 10,
  borderRadius: 10,
  alignItems: "center",
},
acceptButton: {
  backgroundColor: "#16a34a",
},
declineButton: {
  backgroundColor: "#dc2626",
},
inviteButtonText: {
  color: "white",
  fontWeight: "700",
},
statusText: {
  marginTop: 8,
  fontSize: 13,
  fontWeight: "700",
  color: "#4A90E2",
},
declinedStatus: {
  marginTop: 12,
  color: "#dc2626",
  fontWeight: "700",
},
acceptedStatus: {
  marginTop: 12,
  color: "#16a34a",
  fontWeight: "700",
},
notificationHeader: {
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
  gap: 12,
},
timeText: {
  fontSize: 12,
  color: "#888",
  marginTop: 6,
},
});