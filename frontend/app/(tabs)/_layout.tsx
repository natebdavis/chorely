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
        }}
      >
        <Tabs.Screen
          name="index"
          options={{
            tabBarIcon: ({ focused }) => (
              <Ionicons name="home" size={28} color={focused ? "#4A90E2" : "#999"} />
            ),
          }}
        />
        <Tabs.Screen
          name="household"
          options={{
            tabBarIcon: ({ focused }) => (
              <Ionicons name="people" size={28} color={focused ? "#4A90E2" : "#999"} />
            ),
          }}
        />

        <Tabs.Screen
          name="leaderboard"
          options={{
            tabBarIcon: ({ focused }) => (
              <Ionicons name="trophy" size={28} color={focused ? "#4A90E2" : "#999"} />
            ),
          }}
        />
        
        <Tabs.Screen
          name="profile"
          options={{
            tabBarIcon: ({ focused }) => (
              <Ionicons name="settings-outline" size={28} color={focused ? "#4A90E2" : "#999"} />
            ),
          }}
        />
      </Tabs>

      {/* Blue Floating Plus Sign Button */}
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
    backgroundColor: "white",
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
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
  },
});