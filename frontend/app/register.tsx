//This is the Registration Screen

import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  StyleSheet, 
  ImageBackground, 
  Image, 
  KeyboardAvoidingView,
  TouchableWithoutFeedback, 
  Platform, 
  Keyboard, 
  ScrollView,
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";

export default function Register() {
  return (
    <ImageBackground
      source={require("../assets/images/background.png")} // same background as login
      style={styles.background}
      resizeMode="cover"
    >
      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <KeyboardAvoidingView
              style={styles.keyboardContainer}
              behavior={Platform.OS === "ios" ? "padding" : "height"}
        >

        <ScrollView
          style={styles.background}
         contentContainerStyle={styles.scrollContainer}
          keyboardShouldPersistTaps="handled">

      <View style={styles.container}>
        <View style={styles.card}>

          <Image //this is the logo
              source={require("../assets/images/chorely_logo.png")}
              style={styles.logo}
          />

          <Text style={styles.title}>Create an Account</Text>

          <View style={styles.inputWrapper}> 
              <Ionicons name="person-outline" size={20} color="#666" style={styles.icon} /> 
                
                <TextInput //this is where users will enter their username
                  placeholder="Username"
                  placeholderTextColor="#666"
                  style={styles.input}/>
            </View>
          
          <View style={styles.inputWrapper}> 
              <Ionicons name="mail-outline" size={20} color="#666" style={styles.icon} /> 
                
                <TextInput //this is where users will enter their email
                  placeholder="Email"
                  placeholderTextColor="#666"
                  style={styles.input}/>
            </View>
          

          <View style={styles.inputWrapper}> 
              <Ionicons name="call-outline" size={20} color="#666" style={styles.icon} /> 
                
                <TextInput //this is where users will enter their phone number
                  placeholder="Phone Number"
                  placeholderTextColor="#666"
                  style={styles.input}/>
            </View>
          
          <View style={styles.inputWrapper}>
              <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.icon} />
              
              <TextInput //this is where users will enter their password
                placeholder=" Password"
                placeholderTextColor="#666"
                secureTextEntry
                style={styles.input}
              />
            </View>

          <View style={styles.inputWrapper}>
              <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.icon} />
              
              <TextInput //this is where users will confirm their password
                placeholder="Confirm Password"
                placeholderTextColor="#666"
                secureTextEntry
                style={styles.input}
              />
            </View>

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
      </ScrollView>
    </KeyboardAvoidingView>
  </TouchableWithoutFeedback>

  </ImageBackground>
  );
}

const styles = StyleSheet.create({
  background: { 
    flex: 1 
  },
  container: { 
    flex: 1, 
    justifyContent: "center", 
    alignItems: "center", 
    padding: 2, 
    width: "100%",
  
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
  keyboardContainer: {
    flex: 1,
  },
  inputWrapper: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "rgba(209, 216, 235, 0.7)", 
    borderRadius: 12,
    paddingHorizontal: 12,
    marginBottom: 15,
  },
  icon: {
    marginRight: 8,
  },
  scrollContainer: {
  flexGrow: 1,
  justifyContent: "center",
  alignItems: "center",
  padding: 20,
},
  logo: {
    width: 120,
    height: 120,
    marginBottom: 20,
    alignSelf: "center"
  },
});
