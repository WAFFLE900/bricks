<template>
  <AppProviders />
</template>

<script setup lang="ts">
import AppProviders from "./providers/AppProviders.vue";
</script>

<style>
@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap");

:root {
  color: #120406;
  font-family: "Noto Sans TC", "PingFang TC", "Helvetica Neue", sans-serif;
  background: #fff;
}

* {
  box-sizing: border-box;
}

html,
body,
#app {
  min-height: 100%;
  margin: 0;
}

body {
  color: #120406;
}

button,
input,
textarea,
select {
  font: inherit;
}

a {
  color: inherit;
}
</style>
