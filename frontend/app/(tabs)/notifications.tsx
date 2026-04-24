import { useState } from "react";
import {
  Image,
  ImageBackground,
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useAuth } from "../../components/AuthContext";

export default function NotificationsScreen() {
  const { user, logout } = useAuth();

  const username = user?.username ?? "User";
  const userId = user?.userid ?? "N/A";
  const phone = user?.userid ?? "N/A"; //need to update to actual phone
  const email = user?.userid ?? "N/A"; //need to update to actual email

  const [menuVisible, setMenuVisible] = useState(false);
  const [activeTab, setActiveTab] = useState<"inbox" | "sent">("inbox");
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showSettingDropdown, setShowSettingDropdown] = useState(false);

  return (
    <ImageBackground
      source={require("../../assets/images/background.png")}
      style={styles.background}
      resizeMode="cover"
    >
      <View style={styles.headerContainer}>
        <View style={styles.greetingContainer}>
          <TouchableOpacity
            onPress={() => setMenuVisible(true)}
            style={styles.avatarButton}
          >
            <Image
              source={require("../../assets/images/default_profile.png")}
              style={styles.avatar}
            />
          </TouchableOpacity>

          <Text style={styles.greetingText}>Hi, {username}</Text>
        </View>

        <Text style={styles.title}>Notifications</Text>
      </View>

      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.tabContainer}>
          <TouchableOpacity
            style={[styles.tabButton, activeTab === "inbox" && styles.activeTab]}
            onPress={() => setActiveTab("inbox")}
          >
            <Text
              style={[
                styles.tabText,
                activeTab === "inbox" && styles.activeTabText,
              ]}
            >
              Inbox
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.tabButton, activeTab === "sent" && styles.activeTab]}
            onPress={() => setActiveTab("sent")}
          >
            <Text
              style={[
                styles.tabText,
                activeTab === "sent" && styles.activeTabText,
              ]}
            >
              Sent
            </Text>
          </TouchableOpacity>
        </View>

        <View style={styles.emptyCard}>
          <Ionicons
            name={
              activeTab === "inbox"
                ? "mail-outline"
                : "paper-plane-outline"
            }
            size={42}
            color="#4A90E2"
          />

          <Text style={styles.emptyTitle}>
            {activeTab === "inbox"
              ? "No inbox notifications yet"
              : "No sent notifications yet"}
          </Text>

          <Text style={styles.emptyText}>
            {activeTab === "inbox"
              ? "Invites, chore requests, and updates you receive will appear here."
              : "Invites and requests you send to others will appear here."}
          </Text>
        </View>
      </ScrollView>

      <Modal
        visible={menuVisible}
        transparent
        animationType="fade"
        onRequestClose={() => setMenuVisible(false)}
      >
        <Pressable
          style={styles.modalOverlay}
          onPress={() => setMenuVisible(false)}
        >
          <Pressable style={styles.menuContainer}>
            <View style={styles.menuHeader}>
              <Image
                source={require("../../assets/images/default_profile.png")}
                style={styles.menuAvatar}
              />

              <Text style={styles.menuUsername}>Hello, {username}!</Text>
              <Text style={styles.menuId}>ID: {userId}</Text>
            </View>

            <View style={styles.divider} />

            <TouchableOpacity
              style={styles.menuItem}
              onPress={() => setShowProfileDropdown((prev) => !prev)}
            >
              <Ionicons name="person-outline" size={20} color="#fff" />
              <Text style={styles.menuText}>Personal Information</Text>

              <View style={{ marginLeft: "auto" }}>
                <Ionicons
                  name={showProfileDropdown? "chevron-up-outline": "chevron-down-outline"}
                  size={18}
                  color="#fff"
                />
              </View>
            </TouchableOpacity>

            {showProfileDropdown && (
              <View style={styles.profileDropdown}>
                <Text style={styles.profileDetail}>
                  <Text style={styles.profileLabel}>Username: </Text>
                  {username}
                </Text>

                <Text style={styles.profileDetail}>
                  <Text style={styles.profileLabel}>Email: </Text>
                    {email}
                </Text>
                
                <Text style={styles.profileDetail}>
                  <Text style={styles.profileLabel}>Phone: </Text>
                    {phone}
                  </Text>

                <Text style={styles.profileDetail}>
                  <Text style={styles.profileLabel}>User ID: </Text>
                  {userId}
                </Text>
              </View>
            )}
            
            <TouchableOpacity
              style={styles.menuItem}
              onPress={() => setShowSettingDropdown((prev) => !prev)}
            >
              <Ionicons name="settings-outline" size={20} color="#fff" />
              <Text style={styles.menuText}>Edit Profile</Text>

              <View style={{ marginLeft: "auto" }}>
                <Ionicons
                  name={showSettingDropdown ? "chevron-up-outline" : "chevron-down-outline"}
                  size={18}
                  color="#fff"
                />
              </View>
            </TouchableOpacity>
            
            {showSettingDropdown && (
                <View style={styles.profileDropdown}>
                  <Text style={styles.profileDetail}>
                    <Text style={styles.profileLabel}>Change Username </Text>
                  </Text>

                  <Text style={styles.profileDetail}>
                    <Text style={styles.profileLabel}>Change Password </Text>
                  </Text>

                </View>
              )}


            <TouchableOpacity
                style={styles.menuItem}
                onPress={() => {
                setMenuVisible(false);
                router.push("/");
              }}
              >
              <Ionicons name="home-outline" size={20} color="#fff" />
              <Text style={styles.menuText}>Chore Board</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.menuItem}
                onPress={() => {
                setMenuVisible(false);
                router.push("/household");
                }}
              >
              <Ionicons name="home" size={20} color="#fff" />
              <Text style={styles.menuText}>Household</Text>
              </TouchableOpacity>


              <TouchableOpacity
              style={styles.menuItem}
                onPress={() => {
                setMenuVisible(false);
                router.push("/leaderboard");
                }}
              >
              <Ionicons name="trophy" size={20} color="#fff" />
              <Text style={styles.menuText}>Leaderboard</Text>
              </TouchableOpacity>


            <TouchableOpacity
               style={styles.menuItem}
               onPress={() => {
                setMenuVisible(false);
                router.push("/notifications");
              }}
              >
            <Ionicons name="notifications-outline" size={20} color="#fff" />
            <Text style={styles.menuText}>Notifications</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.menuItem}
              onPress={async () => {
                setMenuVisible(false);
                await logout();
                router.replace("/login");
              }}
            >
              <Ionicons name="log-out-outline" size={20} color="#ff8080" />
              <Text style={[styles.menuText, { color: "#ff8080" }]}>
                Logout
              </Text>
            </TouchableOpacity>
          </Pressable>
        </Pressable>
      </Modal>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
  },
  headerContainer: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    paddingTop: 60,
    paddingBottom: 16,
    paddingHorizontal: 20,
    zIndex: 10,
  },
  greetingContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#010b1f",
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 999,
    alignSelf: "flex-start",
  },
  avatarButton: {
    width: 50,
    height: 50,
    borderRadius: 25,
    overflow: "hidden",
  },
  avatar: {
    width: "100%",
    height: "100%",
    borderRadius: 23,
    backgroundColor: "#333",
  },
  greetingText: {
    paddingLeft: 4,
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  title: {
    paddingTop: 15,
    fontSize: 30,
    fontWeight: "bold",
    alignSelf: "center",
    color: "rgba(235, 235, 235, 0.92)",
  },
  container: {
    flexGrow: 1,
    paddingHorizontal: 20,
    paddingTop: 190,
    paddingBottom: 110,
  },
  tabContainer: {
    flexDirection: "row",
    backgroundColor: "rgba(1, 11, 31, 0.85)",
    borderRadius: 16,
    padding: 6,
    marginBottom: 24,
  },
  tabButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 12,
    alignItems: "center",
  },
  activeTab: {
    backgroundColor: "#4A90E2",
  },
  tabText: {
    color: "#cbd5e1",
    fontSize: 16,
    fontWeight: "700",
  },
  activeTabText: {
    color: "#fff",
  },
  emptyCard: {
    backgroundColor: "rgba(255, 255, 255, 0.92)",
    borderRadius: 22,
    padding: 28,
    alignItems: "center",
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: "bold",
    color: "#111827",
    marginTop: 14,
    marginBottom: 8,
    textAlign: "center",
  },
  emptyText: {
    fontSize: 14,
    lineHeight: 20,
    color: "#4B5563",
    textAlign: "center",
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.35)",
    flexDirection: "row",
  },
  menuContainer: {
    width: "80%",
    height: "100%",
    backgroundColor: "#1C1C1E",
    paddingTop: 90,
    paddingHorizontal: 16,
    borderTopRightRadius: 20,
    borderBottomRightRadius: 20,
    borderRightWidth: 1,
    borderColor: "#2E2E32",
  },
  menuHeader: {
    paddingTop: 40,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 25,
  },
  menuAvatar: {
    width: 90,
    height: 90,
    borderRadius: 45,
    marginBottom: 10,
    backgroundColor: "#333",
  },
  menuUsername: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 8,
  },
  menuId: {
    color: "#cbd5e1",
    fontSize: 14,
    fontWeight: "700",
    marginBottom: 10,
    paddingHorizontal: 8,
    paddingTop: 30,
  },
  divider: {
    height: 2,
    backgroundColor: "#2E2E32",
    marginVertical: 10,
  },
  menuItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 10,
  },
  menuText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "500",
  },
  profileDropdown: {
    marginTop: 6,
    marginBottom: 10,
    marginHorizontal: 8,
    paddingVertical: 12,
    paddingHorizontal: 14,
    borderRadius: 12,
  },
  profileDetail: {
    color: "#fff",
    fontSize: 14,
    marginBottom: 8,
    lineHeight: 20,
  },
  profileLabel: {
    fontWeight: "700",
    color: "#4A90E2",
  },
});