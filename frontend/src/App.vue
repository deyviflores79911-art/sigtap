<template>
  <RouterView />
</template>

<script setup>
import { RouterView } from 'vue-router'
</script>

<style>
html,
body,
#app {
  margin: 0;
  width: 100%;
  min-width: 320px;
  min-height: 100%;
}

body {
  min-height: 100vh;
}
</style>