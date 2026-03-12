import { StyleSheet, Text, TouchableOpacity, View } from "react-native";

import { Chore } from "./ChoreContext";

type ChoreItemProps = {
  chore: Chore;
  onComplete: () => void;
};

export function ChoreItem({ chore, onComplete }: ChoreItemProps) {
  return (
    <View style={styles.card}>
      <View style={styles.content}>
        {/* This displays the chore name */}
        <Text style={styles.title}>{chore.name}</Text>
        {/* This displays the name of the person assigned to the chore */}
        <Text style={styles.assignee}>Assigned to: {chore.assignedTo}</Text>
        <Text style={styles.meta}>Request date: {chore.requestDate ?? "Unknown"}</Text>
        <Text style={styles.meta}>Due date: {chore.dueDate ?? "Unknown"}</Text>
        <Text style={styles.meta}>Status: {chore.status ?? "Unknown"}</Text>
        {/* This displays the chore description */}
        <Text style={styles.description}>{chore.description}</Text>
      </View>

      <View style={styles.actions}>
        {/* This button checks off the chore and removes it from the board */}
        <TouchableOpacity style={styles.button} onPress={onComplete}>
          <Text style={styles.buttonText}>X</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "white",
    borderRadius: 20,
    padding: 18,
    marginBottom: 14,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 5,
    elevation: 5,
  },
  content: {
    marginBottom: 14,
  },
  title: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#111827",
    marginBottom: 8,
  },
  description: {
    fontSize: 14,
    color: "#4B5563",
    lineHeight: 20,
  },
  assignee: {
    fontSize: 13,
    color: "#6B7280",
    fontWeight: "600",
    marginBottom: 8,
  },
  meta: {
    fontSize: 13,
    color: "#6B7280",
    marginBottom: 6,
  },
  actions: {
    alignItems: "flex-end",
  },
  button: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#000000",
  },
  buttonText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 18,
    lineHeight: 20,
  },
});
