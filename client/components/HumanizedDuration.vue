<template>
  <span>
    <template v-if="duration === null || duration === undefined">
      {{' '}}
    </template>
    <template v-else-if="absDuration < 60e3">
      Around now
    </template>
    <template v-else>
      <template v-if="absDuration < 60 * 60e3">
        {{ (absDuration / 60e3).toFixed(0) }} minutes
      </template>
      <template v-else-if="absDuration < 24 * 3600 * 60e3">
        {{ Math.floor(absDuration / 3600e3) }} hours
        {{ Math.floor((absDuration % 3600e3) / 60e3) }} minutes
      </template>
      <template v-else-if="absDuration < 365 * 24 * 3600 * 60e3">
        {{ (absDuration / 24 / 3600e3).toFixed(0) }} days
      </template>
      <template v-else>
        {{ Math.abs(new Date().getFullYear() - new Date(Date.now() + duration).getFullYear()) }} years
      </template>
      {{ duration < 0 ? 'ago' : 'from now'}}
    </template>
  </span>
</template>

<script>
export default {
  props: ['duration'],
  computed: {
    absDuration () {
      return this.duration && Math.abs(this.duration)
    }
  }
}
</script>
