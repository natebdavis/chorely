import { View, TouchableOpacity, StyleSheet } from "react-native";
import { Tabs, router } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

export default function HomeLayout() {
  return (
    <>
      <Tabs
        screenOptions={{
          headerShown: false,
          tabBarShowLabel: false,
          tabBarStyle: styles.tabBar,
          tabBarActiveTintColor: "#4A90E2",
          tabBarInactiveTintColor: "#6E6E73",
          sceneStyle: { backgroundColor: "#0D0D0D" }, // screen background
        }}
      >
        <Tabs.Screen
          name="index"
          options={{
            tabBarIcon: ({ color }) => (
              <Ionicons name="home" size={28} color={color} />
            ),
          }}
        />

        <Tabs.Screen
          name="household"
          options={{
            tabBarIcon: ({ color }) => (
              <Ionicons name="people"
                size={28}
                color={color}
                 style={{ transform: [{ translateX: -20 }] }} // moved the icon to the left 
                 />
            ),
          }}
        />

        <Tabs.Screen
          name="leaderboard"
          options={{
            tabBarIcon: ({ color }) => (
              <Ionicons name="trophy"
                size={28}
                color={color}
                 style={{ transform: [{ translateX: 20 }] }} //this moved the icon to the right 
                 />
              ),
          }}
        />

        <Tabs.Screen
          name="profile"
          options={{
            tabBarIcon: ({ color }) => (
              <Ionicons name="settings-outline" size={28} color={color} />
            ),
          }}
        />
      </Tabs>

      {/* Floating Add Button */}
      <TouchableOpacity
        style={styles.fab}
        onPress={() => router.push("/chorecreationform")}
      >
        <Ionicons name="add" size={32} color="white" />
      </TouchableOpacity>
    </>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    position: "absolute",
    height: 70,
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    backgroundColor: "#1C1C1E", 
    borderTopWidth: 0,
    elevation: 10,
    paddingTop: 10,
  },

  fab: {
    position: "absolute",
    bottom: 25,
    alignSelf: "center",
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: "#4A90E2",
    justifyContent: "center",
    alignItems: "center",
    elevation: 5,

    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.6,
    shadowRadius: 4,
  },
});