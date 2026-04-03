import {
  ImageBackground,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useEffect, useState } from "react";

import { ChoreItem } from "../../components/ChoreItem";
import type { Chore } from "../../components/ChoreContext";
import { useAuth } from "../../components/AuthContext";

type BackendChore = {
  choreid: number | null;
  name: string;
  description: string;
  request_date: number | null;
  due_date: number | null;
  assignee: string | null;
  status: string | null;
};

type Member = {
  userid: number;
  username: string;
  fname: string;
  lname: string;
};

const API_BASE = "https://chorely-beta-release.onrender.com";

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
  const { user } = useAuth();
  const [chores, setChores] = useState<Chore[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDropdownFor, setShowDropdownFor] = useState<string | null>(null);

  const handleStatusChange = async (choreId: string, newStatus: string, assigneeId?: number | null) => {
    try {
      const response = await fetch(`${API_BASE}/chores/${choreId}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${user?.token}`,
        },
        body: JSON.stringify({
          status: newStatus,
          assignee_id: assigneeId ?? null,
        }),
      });

      if (response.ok) {
        const assignedMember = members.find((m) => m.userid === assigneeId);
        setChores((prev) =>
          prev.map((c) =>
            c.id === choreId
              ? {
                  ...c,
                  status: newStatus,
                  assignedTo: assignedMember
                    ? `${assignedMember.fname} ${assignedMember.lname}`
                    : c.assignedTo,
                }
              : c
          )
        );
      }
    } catch (e) {
      // silently fail
    }
  };

  useEffect(() => {
    if (!user?.householdid) {
      setLoading(false);
      return;
    }

    async function loadChores() {
      try {
        const response = await fetch(`${API_BASE}/chores`, {
          headers: { Authorization: `Bearer ${user?.token}` },
        });

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

    async function loadMembers() {
      try {
        const response = await fetch(`${API_BASE}/households/members`, {
          headers: { Authorization: `Bearer ${user?.token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setMembers(data);
        }
      } catch (e) {
        // silently fail
      }
    }

    loadChores();
    loadMembers();
  }, []);

  return (
    <ImageBackground
      source={require("../../assets/images/background.png")}
      style={styles.background}
      resizeMode="cover"
    >
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.title}>Chore Board</Text>

        {!user?.householdid ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>No Household</Text>
            <Text style={styles.emptyText}>
              You must join a household to view chores.
            </Text>
          </View>
        ) : loading ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Loading chores...</Text>
          </View>
        ) : error ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>Failed to load chores</Text>
            <Text style={styles.emptyText}>{error}</Text>
          </View>
        ) : chores.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyTitle}>No chores yet</Text>
            <Text style={styles.emptyText}>
              Create a chore to get started.
            </Text>
          </View>
        ) : (
          chores.map((chore) => (
            <ChoreItem
              key={chore.id}
              chore={chore}
              onComplete={() => {}}
              onStatusChange={handleStatusChange}
              showDropdownFor={showDropdownFor}
              onToggleDropdown={setShowDropdownFor}
              members={members}
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
