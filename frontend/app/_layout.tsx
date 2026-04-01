import { Stack } from "expo-router";

import { ChoreProvider } from "../components/ChoreContext";
import { AuthProvider } from "../components/AuthContext";

export default function RootLayout() {
  return (
    <AuthProvider>
      <ChoreProvider>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="login" />
          <Stack.Screen name="(tabs)" />
        </Stack>
      </ChoreProvider>
    </AuthProvider>
  );
}
