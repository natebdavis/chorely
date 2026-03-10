import { View, Text, TextInput, TouchableOpacity, StyleSheet, ImageBackground } from "react-native";
import { router } from "expo-router";

export default function Register() {
  return (
    <ImageBackground
      source={require("../assets/images/background.png")} // same background as login
      style={styles.background}
      resizeMode="cover"
    >
      <View style={styles.container}>
        <View style={styles.card}>
          <Text style={styles.title}>Create an Account</Text>

          <TextInput 
          placeholder="Username" 
           placeholderTextColor="#666"
          style={styles.input} />
          
          <TextInput 
          placeholder="Email/Phone Number" 
           placeholderTextColor="#666"
          style={styles.input} />
          
          <TextInput 
          placeholder="Password" secureTextEntry 
           placeholderTextColor="#666"
          style={styles.input} />

          <TextInput 
          placeholder="Confirm Password" secureTextEntry 
           placeholderTextColor="#666"
          style={styles.input} />

          <TouchableOpacity 
          style={styles.button}
           onPress={() => router.replace("/(tabs)")}>

            <Text style={styles.buttonText}>Register</Text>
          </TouchableOpacity>

          <TouchableOpacity
          style={styles.secondaryButton}
           onPress={() => router.push("/login")}>

            <Text style={styles.secondaryButtonText}>Back to Login</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: { flex: 1 },
  container: { 
    flex: 1, 
    justifyContent: "center", 
    alignItems: "center", 
    padding: 20 
  },
  card: {
    width: "100%",
    padding: 25,
    borderRadius: 20,
    backgroundColor: "white",
    elevation: 5,            
    shadowColor: "#000",     
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.15,
    shadowRadius: 5,
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },
  input: {
    backgroundColor: "rgba(209, 216, 235, 0.7)",
    padding: 14,
    borderRadius: 12,
    marginBottom: 15,
  },
  button: {
    backgroundColor: "#000000",
    padding: 15,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 5,
  },
  buttonText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 16,
  },
  secondaryButton: {
    alignItems: "center",
    marginTop: 14,
  },
  secondaryButtonText: {
    color: "#111827",
    fontSize: 14,
    fontWeight: "600",
    textDecorationLine: "underline",
  },
});
