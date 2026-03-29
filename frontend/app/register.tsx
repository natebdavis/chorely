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
  Alert
} from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useState } from "react";

export default function Register() {
  const [username, setUsername] = useState("");
  const [fname, setFname] = useState("");
  const [lname, setLname] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNum, setPhoneNum] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const passwordsMatch = confirmPassword.length === 0 || password === confirmPassword;

  
  const API_URL = "http://127.0.0.1:8000"; //use this if you are running the IOS simulator on mac
  
  //this makes the phone number appear like (XXX)-XXX-XXXX
    const formatPhoneNumber = (text: string) => {
    const cleaned = text.replace(/\D/g, ""); // remove non-numbers

    const match = cleaned.match(/^(\d{0,3})(\d{0,3})(\d{0,4})$/);

    if (!match) return text;

    let formatted = "";

    if (match[1]) {
      formatted = `(${match[1]}`;
    }
    if (match[2]) {
      formatted += `) ${match[2]}`;
    }
    if (match[3]) {
      formatted += `-${match[3]}`;
    }

    return formatted;
  };


  const handleRegister = async () => {
    if (!username || !fname || !lname || !email || !password || !confirmPassword) {
      Alert.alert("Missing fields", "Please fill out all required fields.");
      return;
    }

    if (!passwordsMatch) {
      return;
    }

    //this takes away the special characters from phone number for the backend 
    const cleanedPhone = phoneNum.replace(/\D/g, "");

    try {
      const response = await fetch(`${API_URL}/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          password,
          fname,
          lname,
          email,
          phone_num: cleanedPhone || null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        Alert.alert("Registration failed", data.detail || "Something went wrong.");
        return;
      }

      Alert.alert("Success", "Account created successfully!");
      router.push("/login");
    } catch (error) {
      console.error("Register error:", error);
      Alert.alert("Connection error", "Could not connect to the backend.");
    }
  };

  return (
    <ImageBackground
      source={require("../assets/images/background.png")} // same background as login
      style={styles.background}
      resizeMode="cover">

      <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <KeyboardAvoidingView
              style={styles.keyboardContainer}
              behavior={Platform.OS === "ios" ? "padding" : "height"}>

        <ScrollView
          style={styles.background}
         contentContainerStyle={styles.scrollContainer}
          keyboardShouldPersistTaps="handled">

          <View style={styles.container}>
            <View style={styles.card}>

              <Image //this is the logo
                  source={require("../assets/images/chorely_logo.png")}
                  style={styles.logo}/>

              <Text style={styles.title}>Create an Account</Text>

              <View style={styles.inputWrapper}> 
                  <Ionicons name="person-outline" size={20} color="#666" style={styles.icon} /> 
                    
                    <TextInput //this is where users will enter their firstname
                      placeholder="First Name"
                      placeholderTextColor="#666"
                      style={styles.input}
                      value={fname}
                      onChangeText={setFname}
                      maxLength={35}
                      />
              </View>

              <View style={styles.inputWrapper}> 
                  <Ionicons name="person-outline" size={20} color="#666" style={styles.icon} /> 
                    
                    <TextInput //this is where users will enter their last name
                      placeholder="Last Name"
                      placeholderTextColor="#666"
                      style={styles.input}
                      value={lname}
                      onChangeText={setLname}
                      maxLength={35}
                      />
              </View>

              <View style={styles.inputWrapper}> 
                  <Ionicons name="person-outline" size={20} color="#666" style={styles.icon} /> 
                    
                    <TextInput //this is where users will enter their username
                      placeholder="Username"
                      placeholderTextColor="#666"
                      style={styles.input}
                      value={username}
                      onChangeText={setUsername}
                      autoCapitalize="none"
                      maxLength={35}/>
              </View>
              
              <View style={styles.inputWrapper}> 
                  <Ionicons name="mail-outline" size={20} color="#666" style={styles.icon} /> 
                    
                    <TextInput //this is where users will enter their email
                      placeholder="Email"
                      placeholderTextColor="#666"
                      style={styles.input}
                      value={email}
                      onChangeText={setEmail}
                      autoCapitalize="none"
                      keyboardType="email-address"/>
              </View>
              

              <View style={styles.inputWrapper}> 
                  <Ionicons name="call-outline" size={20} color="#666" style={styles.icon} /> 
                    
                    <TextInput //this is where users will enter their phone number
                      placeholder="Phone Number"
                      placeholderTextColor="#666"
                      style={styles.input}
                      value={phoneNum}
                      onChangeText={(text) => setPhoneNum(formatPhoneNumber(text))}
                      keyboardType="phone-pad"
                      maxLength={14}/>
                     
              </View>
              
              <View style={styles.inputWrapper}>
                  <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.icon} />
                  
                  <TextInput //this is where users will enter their password
                    placeholder=" Password"
                    placeholderTextColor="#666"
                    //secureTextEntry
                    secureTextEntry={!showPassword}
                    style={styles.input}
                    value={password}
                    onChangeText={setPassword} />
              
                  <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                    <Ionicons name={showPassword ? "eye-off-outline" : "eye-outline"} size={20}  color="#666" />
                  </TouchableOpacity>
              </View>


              <View style={styles.inputWrapper}>
                  <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.icon} />
                  
                  <TextInput //this is where users will confirm their password
                    placeholder="Confirm Password"
                    placeholderTextColor="#666"
                    //secureTextEntry
                    secureTextEntry={!showConfirmPassword}
                    style={styles.input}
                    value={confirmPassword}
                    onChangeText={setConfirmPassword}
                  />

                  <TouchableOpacity onPress={() => setShowConfirmPassword(!showConfirmPassword)}> 
                    <Ionicons name={showConfirmPassword ? "eye-off-outline" : "eye-outline"} size={20}  color="#666" />
                  </TouchableOpacity>
                </View>

                {confirmPassword.length > 0 && !passwordsMatch && (
                <Text style={styles.errorText}>Passwords do not match </Text>)} 

                {confirmPassword.length > 0 && passwordsMatch && (
                  <Text style={styles.successText}>Passwords match</Text>)}

              <TouchableOpacity  style={styles.button} onPress={handleRegister}>
                <Text style={styles.buttonText}>Register</Text>
              </TouchableOpacity>

              <TouchableOpacity style={styles.secondaryButton}
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
errorText: {
  color: "red",
  fontSize: 13,
  marginTop: -8,
  marginBottom: 12,
  marginLeft: 8,
},
successText: {
  color: "green",
  fontSize: 13,
  marginTop: -8,
  marginBottom: 12,
  marginLeft: 8,
},
  logo: {
    width: 120,
    height: 120,
    marginBottom: 20,
    alignSelf: "center"
  },
});
