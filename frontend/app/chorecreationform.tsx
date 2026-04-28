import { useState, useEffect } from "react";
import {
  ImageBackground,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
  ScrollView,
  Alert,
} from "react-native";
import DateTimePicker from "@react-native-community/datetimepicker";
import { router } from "expo-router";
import { useAuth } from "../components/AuthContext";

//const API_URL = "https://chorely-beta-release.onrender.com";
const API_URL = "https://chorely-final-1v-release.onrender.com";

type Member = {
  userid: number;
  username: string;
  fname: string;
  lname: string;
};

export default function CreateChore() {
  const { user } = useAuth();
  const token = user?.token;
  const householdid = user?.householdid;

  const [choreName, setChoreName] = useState("");
  const [description, setDescription] = useState("");
  const [dueDate, setDueDate] = useState(() => {
    const d = new Date();
    d.setHours(d.getHours() + 1, 0, 0, 0);
    return d;
  });
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  const [members, setMembers] = useState<Member[]>([]);
  const [selectedAssignee, setSelectedAssignee] = useState<Member | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [loading, setLoading] = useState(false);

  // Fetch household members to populate assignee dropdown
  useEffect(() => {
    if (!token || !householdid) return;

    async function fetchMembers() {
      try {
        const response = await fetch(`${API_URL}/households/members`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setMembers(data);
        }
      } catch (e) {
        // silently fail, dropdown will just be empty
      }
    }

    fetchMembers();
  }, [token, householdid]);

  // If user has no household, show restriction message
  if (!householdid) {
    return (
      <ImageBackground
        source={require("../assets/images/background.png")}
        style={styles.background}
        resizeMode="cover"
      >
        <View style={styles.container}>
          <View style={styles.card}>
            <Text style={styles.title}>Create a Chore</Text>
            <Text style={styles.restrictionText}>
              You must join a household before creating a chore.
            </Text>
            <TouchableOpacity style={styles.button} onPress={() => router.back()}>
              <Text style={styles.buttonText}>Go Back</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ImageBackground>
    );
  }

  const isSubmitDisabled = !choreName.trim() || !description.trim() || loading;

  const handleCreateChore = async () => {
    if (isSubmitDisabled) return;

    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/chores`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          householdid,
          requester_id: user?.userid,
          name: choreName.trim(),
          description: description.trim(),
          due_date: dueDate.toISOString().replace("Z", ""),
          assignee_id: selectedAssignee?.userid ?? null,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        Alert.alert("Error", data.detail || "Failed to create chore");
        return;
      }

      router.replace("/(tabs)");
    } catch (e) {
      Alert.alert("Error", "Could not connect to the server");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ImageBackground
      source={require("../assets/images/background.png")}
      style={styles.background}
      resizeMode="cover"
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={styles.keyboardView}
      >
        <ScrollView contentContainerStyle={styles.container}>
          <View style={styles.card}>
            <Text style={styles.title}>Create a Chore</Text>

            {/* Chore name */}
            <TextInput
              value={choreName}
              onChangeText={setChoreName}
              placeholder="Chore name"
              placeholderTextColor="#666"
              style={styles.input}
            />

            {/* Description */}
            <TextInput
              value={description}
              onChangeText={setDescription}
              placeholder="Description"
              placeholderTextColor="#666"
              multiline
              numberOfLines={5}
              style={[styles.input, styles.descriptionInput]}
              textAlignVertical="top"
            />

            {/* Due date + time pickers */}
            <View style={styles.dateTimeRow}>
              <TouchableOpacity
                style={[styles.input, styles.dateTimeInput]}
                onPress={() => setShowDatePicker(true)}
              >
                <Text style={{ color: "#333" }}>
                  {dueDate.toLocaleDateString([], { month: "short", day: "numeric", year: "numeric" })}
                </Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={[styles.input, styles.dateTimeInput]}
                onPress={() => setShowTimePicker(true)}
              >
                <Text style={{ color: "#333" }}>
                  {dueDate.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}
                </Text>
              </TouchableOpacity>
            </View>

            {showDatePicker && (
              <DateTimePicker
                value={dueDate}
                mode="date"
                minimumDate={new Date()}
                onChange={(event, date) => {
                  setShowDatePicker(false);
                  if (date) {
                    const combined = new Date(date);
                    combined.setHours(dueDate.getHours(), dueDate.getMinutes(), 0, 0);
                    setDueDate(combined);
                  }
                }}
              />
            )}

            {showTimePicker && (
              <DateTimePicker
                value={dueDate}
                mode="time"
                onChange={(event, time) => {
                  setShowTimePicker(false);
                  if (time) {
                    const combined = new Date(dueDate);
                    combined.setHours(time.getHours(), time.getMinutes(), 0, 0);
                    setDueDate(combined);
                  }
                }}
              />
            )}

            {/* Assignee dropdown */}
            <TouchableOpacity
              style={styles.input}
              onPress={() => setShowDropdown(!showDropdown)}
            >
              <Text style={{ color: selectedAssignee ? "#333" : "#666" }}>
                {selectedAssignee
                  ? `${selectedAssignee.fname} ${selectedAssignee.lname} (@${selectedAssignee.username})`
                  : "Assign to (optional)"}
              </Text>
            </TouchableOpacity>

            {showDropdown && (
              <View style={styles.dropdown}>
                <TouchableOpacity
                  style={styles.dropdownItem}
                  onPress={() => { setSelectedAssignee(null); setShowDropdown(false); }}
                >
                  <Text style={styles.dropdownText}>Unassigned</Text>
                </TouchableOpacity>
                {members.map((member) => (
                  <TouchableOpacity
                    key={member.userid}
                    style={styles.dropdownItem}
                    onPress={() => { setSelectedAssignee(member); setShowDropdown(false); }}
                  >
                    <Text style={styles.dropdownText}>
                      {member.fname} {member.lname} (@{member.username})
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            )}

            <TouchableOpacity
              style={[styles.button, isSubmitDisabled && styles.buttonDisabled]}
              disabled={isSubmitDisabled}
              onPress={handleCreateChore}
            >
              <Text style={styles.buttonText}>
                {loading ? "Creating..." : "Create Chore"}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.secondaryButton}
              onPress={() => router.back()}
            >
              <Text style={styles.secondaryButtonText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  container: {
    flexGrow: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
    paddingVertical: 40,
  },
  card: {
    width: "100%",
    padding: 25,
    borderRadius: 20,
    backgroundColor: "white",
    elevation: 5,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 5,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },
  restrictionText: {
    fontSize: 15,
    color: "#666",
    textAlign: "center",
    marginBottom: 20,
    lineHeight: 22,
  },
  input: {
    backgroundColor: "rgba(209, 216, 235, 0.7)",
    padding: 14,
    borderRadius: 12,
    marginBottom: 15,
    justifyContent: "center",
  },
  descriptionInput: {
    minHeight: 130,
  },
  dateTimeRow: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 15,
  },
  dateTimeInput: {
    flex: 1,
    marginBottom: 0,
  },
  dropdown: {
    backgroundColor: "white",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#ddd",
    marginBottom: 15,
    overflow: "hidden",
  },
  dropdownItem: {
    padding: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  dropdownText: {
    fontSize: 14,
    color: "#333",
  },
  button: {
    backgroundColor: "#000000",
    padding: 15,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 5,
  },
  buttonDisabled: {
    opacity: 0.55,
  },
  buttonText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 16,
  },
  secondaryButton: {
    alignItems: "center",
    marginTop: 14,
  },
  secondaryButtonText: {
    color: "#111827",
    fontSize: 14,
    fontWeight: "600",
    textDecorationLine: "underline",
  },
});
