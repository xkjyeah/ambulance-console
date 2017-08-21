<template>
  <div v-if="value === null || (now > value)" class="free">
    Free
  </div>
  <div v-else-if="(value - now) < 10 * 60e3" class="soon">
    Ending at {{dateformat(value, 'HH:MM')}}
  </div>
  <div v-else class="busy">
    Ending at {{dateformat(value, 'HH:MM')}}
  </div>
</template>
<style scoped>
.free {
  color: #0C0;
}
.soon {
  color: #D90;
}
.busy {
  color: #C00;
}
</style>

<script>
import dateformat from 'dateformat'
import Vue from 'vue'

const timer = new Vue({
  data () {
    return {
      now: Date.now()
    }
  },
  created () {
    this.$theInterval = setInterval(() => {
      this.now = Date.now()
    }, 20000)
  },
  destroyed () {
    clearInterval(this.$theInterval)
  },
  methods: {
    dateformat
  }
})

export default {
  props: ['value'],
  computed: {
    now () {
      return timer.now
    }
  },
}
</script>
