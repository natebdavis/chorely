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
  const [usernameError, setUsernameError] = useState("");
  const [fname, setFname] = useState("");
  const [lname, setLname] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNum, setPhoneNum] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const passwordsMatch = confirmPassword.length === 0 || password === confirmPassword;
  const isValidEmail = (email: string) => {return /^[^\s@]+@[^\s@.]+\.[a-zA-Z]{2,}$/.test(email);}; 
  
  const emailValid = email.length === 0 || isValidEmail(email);
  const isUsernameValid = username.length === 0 || username.length >= 6;
  const isPasswordValid = password.length === 0 || password.length >= 6;
  const cleanedPhoneForCheck = phoneNum.replace(/\D/g, "");
  const isPhoneValid = phoneNum.length === 0 || cleanedPhoneForCheck.length === 10;

  const API_URL = "https://chorely-beta-release.onrender.com";
  
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
    if (!username || !fname || !lname || !email || !password || !confirmPassword || !phoneNum) {
      Alert.alert("Missing fields", "Please fill out all required fields.");
      return;
    }

    if (username.length < 6) {
      Alert.alert("Invalid Username", "Username must be at least 6 characters.");
      return;
    }

    if (password.length < 6) {
      Alert.alert("Invalid Password", "Password must be at least 6 characters.");
      return;
    }

    //this takes away the special characters from phone number for the backend 
    const cleanedPhone = phoneNum.replace(/\D/g, "");
    if (cleanedPhone.length !== 10) {
      Alert.alert("Invalid Phone Number", "Please enter a complete 10-digit phone number.");
      return;
    }

    if (!passwordsMatch) {
      return;
    }

    if (!emailValid) {
      return;
    }

  

    try {
      const response = await fetch(`${API_URL}/user/create`, {
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

    console.log("RESPONSE STATUS:", response.status); //this is for testing
    console.log("RESPONSE DATA:", data); //this is for testing

     // if (!response.ok) {
       // Alert.alert("Registration failed", data.detail || "Something went wrong.");
        //return;
      //}
      if (!response.ok) {
        if (data.detail === "Username not available") {
           setUsernameError("Username is already taken");
          } else {
          Alert.alert("Registration failed", data.detail || "Something went wrong");
           }
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
                      onChangeText={(text) => {setUsername(text);setUsernameError(""); }}
                      autoCapitalize="none"
                      maxLength={35}/>

                      {usernameError !== "" && (<Text style={styles.errorText}>{usernameError}</Text>)}
              </View>
              {!isUsernameValid && (<Text style={styles.errorText}>Usernamemust be at least 6 characters</Text>)}
              
              <View style={styles.inputWrapper}> 
                  <Ionicons name="mail-outline" size={20} color="#666" style={styles.icon} /> 
                    
                    <TextInput //this is where users will enter their email
                      placeholder="Email"
                      placeholderTextColor="#666"
                      style={styles.input}
                      value={email}
                      onChangeText={setEmail}
                      autoCapitalize="none"
                      keyboardType="email-address"
                      />
              </View>
              {email.length > 0 && !emailValid && (<Text style={styles.errorText}>Invalid email address</Text>)}
              {email.length > 0 && emailValid && (<Text style={styles.successText}>Valid email address</Text>)}
              

              <View style={styles.inputWrapper}> 
                  <Ionicons name="call-outline" size={20} color="#666" style={styles.icon} /> 
                    
                    <TextInput //this is where users will enter their phone number
                      placeholder="Phone Number"
                      placeholderTextColor="#666"
                      style={styles.input}
                      value={phoneNum}
                      onChangeText={(text) => setPhoneNum(formatPhoneNumber(text))}
                      //keyboardType="phone-pad"
                      maxLength={14}/>    
              </View>
              {!isPhoneValid && (<Text style={styles.errorText}>Phone number must be 10-digits</Text>)}
              
              <View style={styles.inputWrapper}>
                  <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.icon} />
                  
                  <TextInput //this is where users will enter their password
                    placeholder=" Password"
                    placeholderTextColor="#666"
                    secureTextEntry={!showPassword}
                    style={styles.input}
                    value={password}
                    onChangeText={setPassword} 
                    />
              
                  <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                    <Ionicons name={showPassword ? "eye-off-outline" : "eye-outline"} size={20}  color="#666" />
                  </TouchableOpacity>
                  
              </View>
              {!isPasswordValid && (<Text style={styles.errorText}>Password must be at least 6 characters</Text>)}


              <View style={styles.inputWrapper}>
                  <Ionicons name="lock-closed-outline" size={20} color="#666" style={styles.icon} />
                  
                  <TextInput //this is where users will confirm their password
                    placeholder="Confirm Password"
                    placeholderTextColor="#666"
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
