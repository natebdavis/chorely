import { useCallback, useState } from "react";
import {
  ImageBackground,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useFocusEffect } from "expo-router";
import { useAuth } from "../../components/AuthContext";

//const API_URL = "https://chorely-beta-release.onrender.com";
//const API_URL = "http://127.0.0.1:8000";
const API_URL = "https://chorely-final-1v-release.onrender.com"

type LeaderboardEntry = {
  householdid: number;
  username: string;
  userid: number;
  chores_completed: number;
  percent_of_chores: number;
};

type Member = {
  userid: number;
  username: string;
  fname: string;
  lname: string;
};

const RANK_BG: Record<number, string> = {
  1: "#D4AF37", // gold
  2: "#C0C0C0", // silver
  3: "#CD7F32", // bronze
};

const PEDESTAL_HEIGHT: Record<number, number> = {
  1: 130,
  2: 95,
  3: 70,
};

export default function Leaderboard() {
  const { user } = useAuth();
  const token = user?.token;
  const householdid = user?.householdid;

  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      if (!householdid || !token) {
        setLoading(false);
        return;
      }

      let cancelled = false;
      setLoading(true);
      setError(null);

      async function load() {
        try {
          const [lbRes, memberRes] = await Promise.all([
            fetch(`${API_URL}/leaderboard`, {
              headers: { Authorization: `Bearer ${token}` },
            }),
            fetch(`${API_URL}/households/members`, {
              headers: { Authorization: `Bearer ${token}` },
            }),
          ]);

          if (cancelled) return;

          if (memberRes.ok) {
            setMembers(await memberRes.json());
          }

          if (lbRes.ok) {
            const data: LeaderboardEntry[] = await lbRes.json();
            setEntries(data);
          } else if (lbRes.status === 404) {
            // backend returns 404 when no completions yet — treat as empty, not error
            setEntries([]);
          } else {
            throw new Error(`Request failed with status ${lbRes.status}`);
          }
        } catch (e) {
          if (!cancelled) {
            setError(e instanceof Error ? e.message : "Unknown error");
          }
        } finally {
          if (!cancelled) setLoading(false);
        }
      }

      load();
      return () => {
        cancelled = true;
      };
    }, [token, householdid])
  );

  const sortedEntries = [...entries].sort((a, b) => {
    if (b.chores_completed !== a.chores_completed) {
      return b.chores_completed - a.chores_completed;
    }
    return a.username.localeCompare(b.username);
  });

  const displayName = (entry: LeaderboardEntry) => {
    const m = members.find((x) => x.userid === entry.userid);
    return m ? `${m.fname} ${m.lname}` : entry.username;
  };

  const top3 = sortedEntries.slice(0, 3);
  const rest = sortedEntries.slice(3);

  const renderPillar = (rank: 1 | 2 | 3) => {
    // top3 is sorted by rank, so index = rank - 1
    const entry = top3[rank - 1];
    if (!entry) return <View style={styles.podiumSlot} />;

    const isMe = entry.userid === user?.userid;
    return (
      <View style={styles.podiumSlot}>
        <Text
          style={[styles.podiumName, isMe && styles.podiumNameMe]}
          numberOfLines={1}
        >
          {displayName(entry)}
          {isMe ? " (you)" : ""}
        </Text>
        <Text style={styles.podiumCount}>{entry.chores_completed}</Text>
        <Text style={styles.podiumLabel}>
          chores · {entry.percent_of_chores}%
        </Text>
        <View
          style={[
            styles.pedestal,
            {
              backgroundColor: RANK_BG[rank],
              height: PEDESTAL_HEIGHT[rank],
            },
          ]}
        >
          <Text style={styles.pedestalRank}>{rank}</Text>
        </View>
      </View>
    );
  };

  return (
    <ImageBackground
      source={require("../../assets/images/background.png")}
      style={styles.background}
      resizeMode="cover"
    >
      <View style={styles.headerContainer}>
        <Text style={styles.title}>Leaderboard</Text>
      </View>

      <ScrollView contentContainerStyle={styles.container}>
        {!householdid ? (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>No Household</Text>
            <Text style={styles.cardText}>
              You must join a household to see the leaderboard.
            </Text>
          </View>
        ) : loading ? (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Loading…</Text>
          </View>
        ) : error ? (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Failed to load</Text>
            <Text style={styles.cardText}>{error}</Text>
          </View>
        ) : sortedEntries.length === 0 ? (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>No chores completed yet</Text>
            <Text style={styles.cardText}>Get started!</Text>
          </View>
        ) : (
          <>
            {/* Podium — visual order is 2 | 1 | 3 */}
            <View style={styles.podium}>
              {renderPillar(2)}
              {renderPillar(1)}
              {renderPillar(3)}
            </View>

            {rest.length > 0 && (
              <>
                <Text style={styles.sectionLabel}>Standings</Text>
                {rest.map((entry, i) => {
                  const rank = i + 4;
                  const isMe = entry.userid === user?.userid;
                  return (
                    <View
                      key={entry.userid}
                      style={[styles.row, isMe && styles.rowMe]}
                    >
                      <View style={styles.rankBadge}>
                        <Text style={styles.rankText}>{rank}</Text>
                      </View>
                      <View style={styles.nameCol}>
                        <Text style={styles.name}>
                          {displayName(entry)}
                          {isMe ? " (you)" : ""}
                        </Text>
                        <Text style={styles.username}>@{entry.username}</Text>
                      </View>
                      <View style={styles.statsCol}>
                        <Text style={styles.choreCount}>
                          {entry.chores_completed}
                        </Text>
                        <Text style={styles.percent}>
                          {entry.percent_of_chores}%
                        </Text>
                      </View>
                    </View>
                  );
                })}
              </>
            )}
          </>
        )}
      </ScrollView>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: { flex: 1 },
  headerContainer: {
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "rgba(235, 235, 235, 0.92)",
    textAlign: "center",
  },
  container: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingBottom: 110,
  },
  card: {
    backgroundColor: "rgba(255, 255, 255, 0.92)",
    borderRadius: 20,
    padding: 24,
    alignItems: "center",
    marginTop: 20,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#111827",
    marginBottom: 8,
  },
  cardText: {
    fontSize: 14,
    lineHeight: 20,
    color: "#4B5563",
    textAlign: "center",
  },

  // ----- Podium -----
  podium: {
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "space-between",
    marginTop: 10,
    marginBottom: 28,
  },
  podiumSlot: {
    flex: 1,
    alignItems: "center",
    paddingHorizontal: 4,
  },
  podiumName: {
    color: "#fff",
    fontSize: 13,
    fontWeight: "600",
    textAlign: "center",
    marginBottom: 6,
  },
  podiumNameMe: {
    color: "#4A90E2",
  },
  podiumCount: {
    color: "#fff",
    fontSize: 24,
    fontWeight: "800",
  },
  podiumLabel: {
    color: "rgba(255,255,255,0.6)",
    fontSize: 11,
    marginBottom: 10,
    textAlign: "center",
  },
  pedestal: {
    width: "100%",
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
    alignItems: "center",
    paddingTop: 12,
    shadowColor: "#000",
    shadowOpacity: 0.3,
    shadowRadius: 4,
    shadowOffset: { width: 0, height: 2 },
  },
  pedestalRank: {
    color: "rgba(255,255,255,0.95)",
    fontSize: 32,
    fontWeight: "900",
  },

  // ----- Rest list -----
  sectionLabel: {
    color: "rgba(235, 235, 235, 0.85)",
    fontSize: 13,
    fontWeight: "700",
    letterSpacing: 1,
    textTransform: "uppercase",
    marginBottom: 8,
    marginLeft: 4,
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(1, 11, 31, 0.85)",
    borderRadius: 16,
    padding: 14,
    marginBottom: 10,
  },
  rowMe: {
    borderColor: "#4A90E2",
    borderWidth: 2,
  },
  rankBadge: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: "rgba(255,255,255,0.15)",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 14,
  },
  rankText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "700",
  },
  nameCol: { flex: 1 },
  name: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  username: {
    color: "rgba(255,255,255,0.55)",
    fontSize: 12,
    marginTop: 2,
  },
  statsCol: { alignItems: "flex-end" },
  choreCount: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "700",
  },
  percent: {
    color: "rgba(255,255,255,0.7)",
    fontSize: 12,
    marginTop: 2,
  },
});
