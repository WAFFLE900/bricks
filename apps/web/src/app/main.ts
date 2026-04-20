import { createApp } from "vue";

import App from "./App.vue";
import { pinia } from "./store";
import { router } from "./router";
import { useAuthStore } from "@/features/auth/stores/auth.store";

const app = createApp(App);

app.use(pinia);
app.use(router);

async function bootstrap() {
  const authStore = useAuthStore();
  await authStore.bootstrap();
  app.mount("#app");
}

void bootstrap();
