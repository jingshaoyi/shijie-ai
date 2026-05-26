<template>
  <a-breadcrumb>
    <a-breadcrumb-item v-for="(item, index) in breadcrumbs" :key="index">
      <router-link v-if="item.path && index < breadcrumbs.length - 1" :to="item.path">
        {{ item.title }}
      </router-link>
      <span v-else>{{ item.title }}</span>
    </a-breadcrumb-item>
  </a-breadcrumb>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbs = computed(() => {
  const matched = route.matched.filter((item) => item.meta?.title)
  return matched.map((item) => ({
    title: item.meta.title,
    path: item.path,
  }))
})
</script>
