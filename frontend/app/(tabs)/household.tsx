import {
  useState, 
  useEffect
} from "react"; 
import {
  View, 
  Text, 
  StyleSheet, 
  TouchableOpacity, 
  Alert,
  TextInput,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Modal,
  Pressable,
  Image,
  ScrollView,
  ImageBackground
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
//const API_URL = "https://chorely-beta-release.onrender.com";
//const API_URL = "http://10.0.0.7:8000"
const API_URL = "http://127.0.0.1:8000"

import { useAuth } from "../../components/AuthContext";

interface Member {
  userid: number;
  username: string;
  fname: string;
  lname: string;
}


export default function Household() {
  const [loading, setLoading] = useState(false);
  const [hasHousehold, setHasHousehold] = useState(false);
  const [members, setMembers] = useState<Member[]>([]);

  const [joinUserId, setJoinUserId] = useState("");
  const [isAddingUser, setIsAddingUser] = useState(false);

  const [householdid, setHouseholdid] = useState<string | null>(null);
  const [memberCount, setMemberCount] = useState<number | null>(null);

  const {user, logout } = useAuth(); //get the 'user' object from useAuth instead of 'token' directly
  const token = user?.token; //grab the token from the user object

  //new UI 
  const [searchQuery, setSearchQuery] = useState("");
  const [showDropdownFor, setShowDropdownFor] = useState<string | null>(null);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showHomeDropdown, setShowHomeDropdown] = useState(false);
  const [showSettingDropdown, setShowSettingDropdown] = useState(false);
  const [menuVisible, setMenuVisible] = useState(false);
  const username = user?.username ?? "User";
  const userId = user?.userid ?? "N/A";
  const phone = user?.phone_num ?? "N/A";
  const email = user?.email ?? "N/A";

  const [searchResults, setSearchResults] = useState<Member[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [invitingUserId, setInvitingUserId] = useState<number | null>(null);
  const [isOwner, setIsOwner] = useState(false);

  const profileImageSource = user?.profile_url
  ? { uri: user.profile_url }
  : require("../../assets/images/default_profile.png");

const fetchMembers = async () => {
    if (!token) 
      return;
    try {
      const response = await fetch(`${API_URL}/households/members`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMembers(data);
        setHasHousehold(true); //shows the list if user is in household

        const owner = data[0]; 
        if (owner && owner.userid === user?.userid) {
          setIsOwner(true);
        } else {
          setIsOwner(false);
        }

      } else {
        setHasHousehold(false);
      }
    } catch (error) {
      console.log("Error fetching members:", error);
    }
  };

  const fetchHouseholdInfo = async () => {
    if (!token) return;

    try {
      const response = await fetch(`${API_URL}/households`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setHouseholdid(String(data.householdid));
        setMemberCount(data.member_count);
        setHasHousehold(true);
      } else {
        setHouseholdid(null);
        setMemberCount(null);
      }
    } catch (error) {
      console.log("Error fetching household info:", error);
    }
  };

  useEffect(() => {
  fetchMembers();
  fetchHouseholdInfo();
}, [token]);

  const handleCreateHousehold = async () => {
    try {
      setLoading(true);

      if (!token) {
        Alert.alert("Error", "Please log in again.");
        return;
      }

      const response = await fetch(`${API_URL}/households`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        Alert.alert("Error", data.detail || "Failed to create household");
        return;
      }

      setHouseholdid(String(data.householdid));
      setMemberCount(data.member_count);
      setHasHousehold(true);

      Alert.alert(
        "Success",
        `Household created successfully.\nHousehold ID: ${data.householdid}\nMembers: ${data.member_count}`
      );

      await fetchMembers();
      await fetchHouseholdInfo();

      console.log("Created household:", data);
    } catch (error) {
      console.log("Create household error:", error);
      Alert.alert("Error", "Something went wrong while creating the household.");
    } finally {
      setLoading(false);
    }
  };

const handleJoinHousehold = async () => {
    if (!joinUserId) {
      Alert.alert("Required Field Missing!", "Please enter a User ID first.");
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/households/join`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ userid: parseInt(joinUserId, 10) }), 
      });

      const data = await response.json();

      if (!response.ok) {
        Alert.alert("Error", data.detail || "Failed to add user.");
        return;
      }

      Alert.alert("Success", "User added to the household!");
      setJoinUserId(""); // Clear the input box
      fetchMembers(); // Refresh the list to show the new member

    } catch (error) {
      console.log("Join error:", error);
      Alert.alert("Error", "Something went wrong while adding the user.");
    } finally {
      setLoading(false);
    }
  };

  const handleLeaveHousehold = async () => {
  if (!token || !user?.userid) {
    Alert.alert("Error", "User information is missing. Please log in again.");
    return;
  }

  try {
    setLoading(true);

    const response = await fetch(`${API_URL}/households/leave`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        userid: user.userid,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      Alert.alert("Error", data.detail || "Failed to leave household.");
      return;
    }

    Alert.alert("Success", data.message || "You have left the household.");

    setHasHousehold(false);
    setMembers([]);
    setHouseholdid(null);
    setMemberCount(null);
    setIsAddingUser(false);
    setJoinUserId("");
  } catch (error) {
    console.log("Leave household error:", error);
    Alert.alert("Error", "Something went wrong while leaving the household.");
  } finally {
    setLoading(false);
  }
};


const handleRemoveMember = (member: Member) => {
  if (!token) {
    Alert.alert("Error", "Please log in again.");
    return;
  }

  Alert.alert(
    "Remove Member",
    `Are you sure you want to remove ${member.fname} ${member.lname} from the household?`,
    [
      {
        text: "Cancel",
        style: "cancel",
      },
      {
        text: "Remove",
        style: "destructive",
        onPress: async () => {
          try {
            setLoading(true);

            const response = await fetch(`${API_URL}/households/remove`, {
              method: "DELETE",
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
              },
              body: JSON.stringify({
                userid: member.userid,
              }),
            });

            const data = await response.json();

            if (!response.ok) {
              Alert.alert("Error", data.detail || "Failed to remove member.");
              return;
            }

            Alert.alert("Success", data.message || "User removed successfully.");

            await fetchMembers();
            await fetchHouseholdInfo();
          } catch (error) {
            console.log("Remove member error:", error);
            Alert.alert("Error", "Something went wrong while removing the member.");
          } finally {
            setLoading(false);
          }
        },
      },
    ]
  );
};

  
const showMember = ({ item }: { item: Member }) => {
  const isCurrentUser = item.userid === user?.userid;

  return (
    <View style={styles.memberCard}>
      <View style={styles.memberInfo}>
        <Text style={styles.memberName}>
          {item.fname} {item.lname}
          {isCurrentUser ? " (You)" : ""}
        </Text>

        <Text style={styles.memberDetails}>Username: {item.username}</Text>
      </View>

      {isOwner && !isCurrentUser && (
        <TouchableOpacity
          style={styles.removeMemberButton}
          onPress={() => handleRemoveMember(item)}
          disabled={loading}
        >
          <Text style={styles.removeMemberButtonText}>Remove</Text>
        </TouchableOpacity>
      )}
    </View>
  );
};


  const handleSearchUsers = async (query: string) => {
    setSearchQuery(query);

    if (!token) {
    console.log("No token found for user search");
    setSearchResults([]);
    return;
    }
    
    if (query.trim().length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/user/search?q=${encodeURIComponent(query.trim())}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });


      if (response.ok) {
        const data = await response.json();
        setSearchResults(data);
      } else {
        setSearchResults([]);
      }
    } catch (error) {
      console.log("Search error:", error);
      setSearchResults([]);
    }
  };

  useEffect(() => {
  const timeout = setTimeout(() => {
    if (searchQuery.length >= 2) {
      handleSearchUsers(searchQuery);
    } else {
      setSearchResults([]); 
    }
  }, 300);

  return () => clearTimeout(timeout);
  }, [searchQuery]);


  const handleSendInvite = async (inviteeUserId: number) => {
    try {
      setInvitingUserId(inviteeUserId);

      const response = await fetch(`${API_URL}/households/invite`,  {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          userid: inviteeUserId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        Alert.alert("Error", data.detail || "Failed to send invite.");
        return;
      }

      Alert.alert("Success", "Invite sent successfully.");
      setSearchQuery("");
      setSearchResults([]);
    } catch (error) {
      console.log("Send invite error:", error);
      Alert.alert("Error", "Something went wrong while sending the invite.");
    } finally {
      setInvitingUserId(null);
    }
  };


  return (
   <ImageBackground
         source={require("../../assets/images/background.png")}
         style={styles.background}
         resizeMode="cover"
    >
          {/* --- NEW HEADER START --- */}
        <View style={styles.headerContainer}>
          <View style={styles.greetingContainer}>
            <TouchableOpacity onPress={() => setMenuVisible(true)} style={styles.avatarButton}>
              <Image
                source={profileImageSource} 
                style={styles.avatar}
              />
            </TouchableOpacity>
            
            <Text style={styles.greetingText}>Hi, {username}</Text>
            
          </View>

          <View style={styles.householdInfoContainer}>
            <Text style={styles.subTitleText}>
                House ID: {householdid ?? "N/A"}
            </Text>
            <Text style={styles.subTitleText}>
                Number of Members: {members.length}
            </Text>
          </View>
        </View>
        {/* --- NEW HEADER END --- */}

    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      {hasHousehold ? (
        
        <View style={styles.listContainer}>
            
            {/* Search Bar */}
                <View style={styles.searchContainer}>
                  <View style = {styles.searchSection}>
                     <Ionicons 
                          name="search-outline" 
                          size={20} 
                          color="#888" 
                           style={styles.searchIcon} 
                        />
                    <TextInput
                        style={styles.searchInput}
                        placeholder="Search members to invite..."
                        placeholderTextColor="#888"
                        value={searchQuery}
                        onChangeText={handleSearchUsers}
                    />
                    </View>
                 
                  {searchLoading && (
                      <Text style={styles.searchStatusText}>Searching...</Text>
                    )}

                    {!searchLoading && searchQuery.trim().length >= 2 && searchResults.length === 0 && (
                      <Text style={styles.searchStatusText}>No matching users found.</Text>
                    )}

                    {searchResults.length > 0 && (
                <View style={styles.searchResultsWrapper}>
                  <ScrollView
                    style={styles.searchResultsScroll}
                    nestedScrollEnabled={true}
                  >
                    {searchResults.map((item) => (
                      <View key={item.userid} style={styles.searchResultCard}>
                        <View>
                          <Text style={styles.searchResultUsername}>@{item.username}</Text>
                          <Text style={styles.searchResultName}>
                            {item.fname} {item.lname}
                          </Text>
                        </View>

                        <TouchableOpacity
                          style={styles.inviteButton}
                          onPress={() => handleSendInvite(item.userid)}
                          disabled={invitingUserId === item.userid}
                        >
                          <Text style={styles.inviteButtonText}>
                            {invitingUserId === item.userid ? "Sending..." : "send invite"}
                          </Text>
                        </TouchableOpacity>
                      </View>
                    ))}
                  </ScrollView>
                </View>
              
              )}
         
                </View>

                

           <Text style={styles.subTitleText}>Members</Text>

          {/*This is the card list that displays each user under members*/}
          <FlatList
            data={members}
            keyExtractor={(item) => item.userid.toString()}
            renderItem={showMember}
            contentContainerStyle={{ paddingBottom: 100 }} 
            style={{ flex: 1 }}
          />
          

        </View>
      ) : (
        <View style={styles.centerContent}>
          <Text style={styles.text}>You are not in a household yet.</Text>
          <TouchableOpacity
            style={[styles.button, loading && styles.disabledButton]}
            onPress={handleCreateHousehold}
            disabled={loading}
          >
            <Text style={styles.buttonText}>
              {loading ? "Creating..." : "Create a Household"}
            </Text>
          </TouchableOpacity>
        </View>
      )}
    </KeyboardAvoidingView>

        {/* --- NEW MODAL START --- */}
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
                source={profileImageSource} 
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

              {/* new household tab where users can leave a household*/}
             <TouchableOpacity
              style={styles.menuItem}
              onPress={() => setShowHomeDropdown((prev) => !prev)}
            >
              <Ionicons name="home" size={20} color="#fff" />
              <Text style={styles.menuText}>Household</Text>
              <View style={{ marginLeft: "auto" }}>
                <Ionicons
                  name={showSettingDropdown ? "chevron-up-outline" : "chevron-down-outline"}
                  size={18}
                  color="#fff"
                />
              </View>
            </TouchableOpacity>

            
            {showHomeDropdown && (
              <View style={styles.profileDropdown}>
                <TouchableOpacity onPress={handleLeaveHousehold}>
                <Text style={[styles.menuText, { color: "#ff8080" }]}>Leave Household</Text>
                </TouchableOpacity>
              </View>
            )}
                 {/* end household dropdown */}

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
      {/* --- NEW MODAL END --- */}


    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1,
    //backgroundColor: "#121212", 
    paddingHorizontal: 24,
    paddingTop: 50,
  },
  background: {
    flex: 1,
  },
  centerContent: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  listContainer: {
    flex: 1,
    width: "100%",
  },
  titleText: {
    fontSize: 24,
    fontWeight: "bold",
    color: "white",
    marginBottom: 20,
    textAlign: "center",
  },
  title: {
    paddingTop: 15,
    fontSize: 30,
    fontWeight: "bold",
    alignSelf: "center", 
    color: "rgba(235, 235, 235, 0.92)",
    marginBottom: 10,
  },
  subTitleText: {
    fontSize: 15,
    fontWeight: "bold",
    color: "white",
    marginBottom: 10,
    textAlign: "left"
  },
  text: { 
    fontSize: 18,
    color: "white",
    marginBottom: 20,
    textAlign: "center",
  },
  memberCard: {
    backgroundColor: "#ffffff",
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#333",
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  memberName: {
    color: "#000000",
    fontSize: 18,
    fontWeight: "600",
  },
  memberDetails: {
    color: "#000000",
    fontSize: 14,
    marginTop: 4,
  },
  floatingButton: {
    position: "absolute",
    top:"4.5%",
    //bottom: "20%",
    right: -10,
    backgroundColor: "#000000",
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 8,
  },
  floatingButtonText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 16,
  },
  addMemberContainer: {
    position: "absolute",
    bottom: "20%",
    left: 0,
    right: 0,
    backgroundColor: "#2d2c2c",
    padding: 20,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    borderWidth: 1,
    borderColor: "#797171",
    shadowColor: "#000",
  },
  input: {
    backgroundColor: "#121212",
    color: "white",
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderRadius: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: "#333",
    marginBottom: 12,
  },
  actionRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  actionButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  cancelButton: {
    backgroundColor: "#444",
    marginRight: 8,
  },
  submitButton: { //add user button 
    backgroundColor: "#2b75d5",
    marginLeft: 8,
  },
  button: {
    backgroundColor: "#2b75d5",
    paddingVertical: 15,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 12,
    width: "100%",
  },
  leaveButton: {
    backgroundColor: "transparent",
    borderWidth: 1,
    borderColor: "#ff4444",
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignSelf: "center",
    marginBottom: 20,
  },
  leaveButtonText: {
    color: "#ff4444",
    fontWeight: "bold",
    fontSize: 14,
  },
  disabledButton: {
    backgroundColor: "#080a7e",
  },
  searchContainer: {
    paddingHorizontal: 0,
    paddingVertical: 12,
    width: '100%',
    marginTop: 10,
    marginBottom: 10,
    paddingTop: "45%"
  },
  searchInput: {
      backgroundColor: '#ffffff00',
      borderRadius: 8,
      padding: 12,
      color: "white",
      fontSize: 16,
      flex: 1,
  },
  buttonText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 16,
  },
  searchSection: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#ccc',
    paddingHorizontal: 10,
},
searchIcon: {
    marginRight: 10,
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
  householdInfoContainer: {
  marginTop: 18,
  paddingLeft: 6,
},
searchResultsContainer: {
  marginTop: 8,
  marginBottom: 16,
},

searchResultCard: {
  flexDirection: "row",
  justifyContent: "space-between",
  alignItems: "center",
  backgroundColor: "rgba(255,255,255,0.95)",
  borderRadius: 10,
  paddingVertical: 12,
  paddingHorizontal: 14,
  marginBottom: 10,
},

searchResultUsername: {
  fontSize: 16,
  fontWeight: "700",
  color: "#111",
},

searchResultName: {
  fontSize: 14,
  color: "#555",
  marginTop: 2,
},

inviteButton: {
  backgroundColor: "#2b75d5",
  paddingVertical: 8,
  paddingHorizontal: 14,
  borderRadius: 8,
},

inviteButtonText: {
  color: "white",
  fontWeight: "bold",
  fontSize: 14,
},

searchStatusText: {
  color: "white",
  fontSize: 14,
  marginTop: 8,
  marginBottom: 12,
},
searchDropdown: {
  backgroundColor: "#1e1e1e",
  borderRadius: 8,
  borderWidth: 1,
  borderColor: "#333",
  marginTop: 4,
  overflow: "hidden",
},
searchResultItem: {
  paddingVertical: 10,
  paddingHorizontal: 14,
  borderBottomWidth: 1,
  borderBottomColor: "#2a2a2a",
},
noResultsText: {
  color: "#888",
  padding: 14,
  textAlign: "center",
},
searchResultsWrapper: {
  maxHeight: 220, // controls how many show (~3 cards)
  marginTop: 8,
  borderRadius: 10,
  overflow: "hidden",
},

searchResultsScroll: {
  width: "100%",
},
memberInfo: {
  flex: 1,
  paddingRight: 10,
},

removeMemberButton: {
  backgroundColor: "transparent",
  borderWidth: 1,
  borderColor: "#ff4444",
  paddingVertical: 8,
  paddingHorizontal: 12,
  borderRadius: 8,
},

removeMemberButtonText: {
  color: "#ff4444",
  fontWeight: "bold",
  fontSize: 13,
},
  });