import {
  ImageBackground,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { ChoreItem } from "../../components/ChoreItem";
import { useChores } from "../../components/ChoreContext";

export default function ChoreBoard() {
  const { chores, deleteChore } = useChores();

  return (
    <ImageBackground
      source={require("../../assets/images/background.png")} 
      style={styles.background}
      resizeMode="cover"
    >
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Chore Board</Text>

        {chores.length === 0 ? (
          <View style={styles.emptyState}>
            {/* This shows when there are no chores on the board yet */}
            <Text style={styles.emptyTitle}>No chores yet</Text>
            <Text style={styles.emptyText}>
              Tap the add button below to create your first chore.
            </Text>
          </View>
        ) : (
          chores.map((chore) => (
            <ChoreItem
              key={chore.id}
              chore={chore}
              // this checks off the chore and removes it from the board
              onComplete={() => deleteChore(chore.id)}
            />
          ))
        )}
      </ScrollView>
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
    paddingTop: 72,
    paddingBottom: 110,
  },
  title: {
    fontSize: 30,
    fontWeight: "bold",
    color: "white",
    marginBottom: 24,
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
});
