import { View, Text, StyleSheet, TouchableOpacity } from "react-native";

export default function Household() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>View Members of your Household Here</Text>

      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>Create a Household</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center" },
  text: { fontSize: 20, fontWeight: "bold", color: "white", marginBottom: 20 },
  button: {
    backgroundColor: "#000000",
    paddingVertical: 15,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: "center",
  },
  buttonText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 16,
  },
});
