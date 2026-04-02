import {useState, 
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
  Platform
} from "react-native";
const API_URL = "http://127.0.0.1:8000";

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
  const [members, setMembers] = useState([]);
  const [joinUserId, setJoinUserId] = useState("");
  const [isAddingUser, setIsAddingUser] = useState(false);

  const { user } = useAuth(); //get the 'user' object from useAuth instead of 'token' directly
  const token = user?.token; //grab the token from the user object

const fetchMembers = async () => {
    if (!token) return;
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
      } else {
        setHasHousehold(false);
      }
    } catch (error) {
      console.log("Error fetching members:", error);
    }
  };

  useEffect(() => {
    fetchMembers();
  }, [token]);


  const handleCreateHousehold = async () => {
    try {
      setLoading(true);

      if (!token) {
        Alert.alert("Error", "No auth token found. Please log in again.");
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

      Alert.alert(
        "Success",
        `Household created successfully.\nHousehold ID: ${data.householdid}\nMembers: ${data.member_count}`
      );

      setHasHousehold(true);
      fetchMembers();

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

  
  const showMember = ({ item }: { item: Member }) => (
    <View style={styles.memberCard}>
      <Text style={styles.memberName}>{item.fname} {item.lname}</Text>
      <Text style={styles.memberDetails}>Username: {item.username}</Text>
    </View>
  );

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      {hasHousehold ? (
        <View style={styles.listContainer}>
          <Text style={styles.titleText}>Your Household Members</Text>
          
          <TouchableOpacity 
            style={styles.leaveButton} 
          >
            <Text style={styles.leaveButtonText}>Leave Household</Text>
          </TouchableOpacity>

          <FlatList
            data={members}
            keyExtractor={(item) => item.userid.toString()}
            renderItem={showMember}
            contentContainerStyle={{ paddingBottom: 100 }} 
            style={{ flex: 1 }}
          />
          
          {isAddingUser ? (
            <View style={styles.addMemberContainer}>
              <TextInput
                style={styles.input}
                placeholder="Enter User ID to add"
                placeholderTextColor="#888"
                value={joinUserId}
                onChangeText={(text) => {const onlyNumbers = text.replace(/[^0-9]/g, '');
                  setJoinUserId(onlyNumbers);
                }} //this ensures no one types in any letters
                keyboardType="numeric"
              />
              <View style={styles.actionRow}>
                <TouchableOpacity
                  style={[styles.actionButton, styles.cancelButton]}
                  onPress={() => {
                    setIsAddingUser(false);
                    setJoinUserId(""); // Clear input if they cancel
                  }}
                >
                  <Text style={styles.buttonText}>Cancel</Text>
                </TouchableOpacity>
                
                <TouchableOpacity
                  style={[styles.actionButton, styles.submitButton, loading && styles.disabledButton]}
                  onPress={handleJoinHousehold}
                  disabled={loading}
                >
                  <Text style={styles.buttonText}>
                    {loading ? "Adding..." : "Add User"}
                  </Text>
                </TouchableOpacity>
              </View>
            </View>
          ) : (
            <TouchableOpacity 
              style={styles.floatingButton} 
              onPress={() => setIsAddingUser(true)}
            >
              <Text style={styles.floatingButtonText}>+ Add User Here</Text>
            </TouchableOpacity>
          )}

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
  );
}

const styles = StyleSheet.create({
  container: { 
    flex: 1,
    backgroundColor: "#121212", 
    paddingHorizontal: 24,
    paddingTop: 50,
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
  text: { 
    fontSize: 18,
    color: "white",
    marginBottom: 20,
    textAlign: "center",
  },
  memberCard: {
    backgroundColor: "#1e1e1e",
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#333",
  },
  memberName: {
    color: "white",
    fontSize: 18,
    fontWeight: "600",
  },
  memberDetails: {
    color: "#aaa",
    fontSize: 14,
    marginTop: 4,
  },
  floatingButton: {
    position: "absolute",
    //top: "6%",
    bottom:"20%",
    alignSelf: "center", 
    right: 0,
    backgroundColor: "#2b75d5",
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
  buttonText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 16,
  },});