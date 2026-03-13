import {
  ImageBackground,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useEffect, useState } from "react";

import { ChoreItem } from "../../components/ChoreItem";
import type { Chore } from "../../components/ChoreContext";

type BackendChore = {
  choreid: number | null;
  name: string;
  description: string;
  request_date: number | null;
  due_date: number | null;
  assignee: string | null;
  status: string | null;
};

const API_BASE =
  Platform.OS === "android" ? "https://chorely.onrender.com" : "https://chorely.onrender.com";

function formatUnixTimestamp(timestamp: number | null) {
  if (!timestamp) {
    return "Unknown";
  }

  return new Date(timestamp * 1000).toLocaleString([], {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function ChoreBoard() {
  const [chores, setChores] = useState<Chore[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadChores() {
      try {
        const response = await fetch(`${API_BASE}/chores/1`);

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
            requestDate: formatUnixTimestamp(backendChore.request_date),
            dueDate: formatUnixTimestamp(backendChore.due_date),
            status: backendChore.status ?? "Unknown",
          }))
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    loadChores();
  }, []);

  return (
    <ImageBackground
      source={require("../../assets/images/background.png")} 
      style={styles.background}
      resizeMode="cover"
    >
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Chore Board</Text>

        {loading ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Loading chore...</Text>
            <Text style={styles.emptyText}>
              Trying to load one chore from the backend.
            </Text>
          </View>
        ) : error ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Backend request failed</Text>
            <Text style={styles.emptyText}>{error}</Text>
          </View>
        ) : chores.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>No backend chores found</Text>
            <Text style={styles.emptyText}>
              `GET /chores/1` returned an empty list.
            </Text>
          </View>
        ) : (
          chores.map((chore) => (
            <ChoreItem
              key={chore.id}
              chore={chore}
              onComplete={() => {}}
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
