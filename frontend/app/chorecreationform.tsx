import { useState } from "react";
import {
  ImageBackground,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import { router } from "expo-router";

import { useChores } from "../components/ChoreContext";

export default function CreateChore() {
  const [choreName, setChoreName] = useState("");
  const [assignedTo, setAssignedTo] = useState("");
  const [description, setDescription] = useState("");
  const { addChore } = useChores();

  const isSubmitDisabled =
    !choreName.trim() || !assignedTo.trim() || !description.trim();

  const handleCreateChore = () => {
    if (isSubmitDisabled) {
      return;
    }

    addChore(choreName, description, assignedTo);
    setChoreName("");
    setAssignedTo("");
    setDescription("");
    router.replace("/(tabs)");
  };

  return (
    <ImageBackground
      source={require("../assets/images/background.png")} // same background as login/register
      style={styles.background}
      resizeMode="cover"
    >
      <KeyboardAvoidingView
        behavior={Platform.OS === "ios" ? "padding" : undefined}
        style={styles.keyboardView}
      >
        <View style={styles.container}>
          <View style={styles.card}>
            <Text style={styles.title}>Create a Chore</Text>

            <TextInput // enter the chore name
              value={choreName}
              onChangeText={setChoreName}
              placeholder="Chore name"
              placeholderTextColor="#666"
              style={styles.input}
            />

            <TextInput // enter who the chore is assigned to
              value={assignedTo}
              onChangeText={setAssignedTo}
              placeholder="Assigned to"
              placeholderTextColor="#666"
              style={styles.input}
            />

            <TextInput // enter the chore description
              value={description}
              onChangeText={setDescription}
              placeholder="Description"
              placeholderTextColor="#666"
              multiline
              numberOfLines={5}
              style={[styles.input, styles.descriptionInput]}
              textAlignVertical="top"
            />

            <TouchableOpacity // this is the Create Chore button
              style={[styles.button, isSubmitDisabled && styles.buttonDisabled]}
              disabled={isSubmitDisabled}
              onPress={handleCreateChore}
            >
              <Text style={styles.buttonText}>Create Chore</Text>
            </TouchableOpacity>

            <TouchableOpacity // this takes the user back to the previous screen
              style={styles.secondaryButton}
              onPress={() => router.back()}
            >
              <Text style={styles.secondaryButtonText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
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
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
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
  input: {
    backgroundColor: "rgba(209, 216, 235, 0.7)",
    padding: 14,
    borderRadius: 12,
    marginBottom: 15,
  },
  descriptionInput: {
    minHeight: 130,
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
