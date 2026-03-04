import { View, Text, StyleSheet } from "react-native";

export default function ChoreBoard() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Chore Board View (Home Screen)</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: "center", alignItems: "center" },
  text: { fontSize: 20, fontWeight: "bold" ,color: "white" },
});
