// this is the Login Screen 

import { View, Text, 
  TextInput, 
  StyleSheet, 
  TouchableOpacity, 
  ImageBackground, 
  Image, 
  KeyboardAvoidingView,
  TouchableWithoutFeedback, 
  Platform, 
  Keyboard,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";

export default function Login() {
  return (
    <ImageBackground
      source={require("../assets/images/background.png")} 
      style={styles.background}
      resizeMode="cover"
    >

      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
        <KeyboardAvoidingView
          style={styles.keyboardContainer}
          behavior={Platform.OS === "ios" ? "padding" : "height"}
        >
        <View style={styles.container}>

          {/* Question about registering */}
          <Text style={styles.signupText}>
            Not registered yet?{" "}
            <Text style={styles.signupLink} 
            onPress={() => router.push("/register")}
            >Sign up here</Text>
          </Text>

          {/* white login box */}
        <View style={styles.card}>

            <Image //this is the logo
              source={require("../assets/images/chorely_logo.png")}
              style={styles.logo}
              />

            <Text style={styles.title}>Welcome to Chorely!</Text>

            
            <View style={styles.inputWrapper}> 
            <Ionicons name="person-outline" size={20} color="#666" style={styles.icon} /> 
      
              <TextInput //this is where users will enter their username
                placeholder="Username"
                placeholderTextColor="#666"
                style={styles.input}
              />
            </View>

            <View style={styles.inputWrapper}>
              <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.icon} />
              
              <TextInput //this is where users will enter their password
                placeholder="Password"
                placeholderTextColor="#666"
                secureTextEntry
                style={styles.input}
              />
            </View>

            <TouchableOpacity //this is the Login Button 
              style={styles.button}
              onPress={() => router.replace("/(tabs)")}
            >
              <Text style={styles.buttonText}>Login</Text>
            </TouchableOpacity>
          </View>

        </View>
       </KeyboardAvoidingView>
      </TouchableWithoutFeedback>

    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: {
    flex: 1,
  },
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  signupText: {
    color: "white",
    marginBottom: 20,
    fontSize: 14,
  },
  signupLink: {
    fontWeight: "bold",
    textDecorationLine: "underline",
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
  inputWrapper: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(209, 216, 235, 0.7)", 
    borderRadius: 12,
    paddingHorizontal: 12,
    marginBottom: 15,
  },
  input: {
    padding: 14,
    borderRadius: 10,
    marginBottom: 5,
    marginTop: 5, 
    flex: 1,
    paddingVertical: 14,
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
  icon: {
    marginRight: 8,
  },
  keyboardContainer: {
    flex: 1,
  },
  logo: {
    width: 120,
    height: 120,
    marginBottom: 20,
    alignSelf: "center"
  },
});

