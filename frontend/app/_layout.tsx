import { Stack } from "expo-router";

import { ChoreProvider } from "../components/ChoreContext";

export default function RootLayout() {
  return (
    <ChoreProvider>
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="login" />
        <Stack.Screen name="(tabs)" />
      </Stack>
    </ChoreProvider>
  );
}
