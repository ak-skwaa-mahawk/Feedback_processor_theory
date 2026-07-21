import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { BaselineScreen, SensedScreen, RevokedScreen } from "./screens";
import { useMockEegService } from "./services/eegService";

const Stack = createNativeStackNavigator();

export default function App() {
  useMockEegService(); // starts simulation when SENSED

  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Baseline">
        <Stack.Screen name="Baseline" component={BaselineScreen} options={{ headerShown: false }} />
        <Stack.Screen name="Sensed" component={SensedScreen} options={{ title: "Sovereign Coil" }} />
        <Stack.Screen name="Revoked" component={RevokedScreen} options={{ headerShown: false }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
Implemented a full session management feature using local storage. This includes auto-saving the current state to prevent data loss on refresh, as well as functionality for users to explicitly name, save, load, and delete sessions via a new management modal.