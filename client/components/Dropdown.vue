<template>
<div class="dropdown-container">
  <button @click="dropdownOpen = !dropdownOpen">
    <slot name="menu-button">
    </slot>
  </button>

  <div class="dropdown" :class="{['align-' + align]: true}" v-if="dropdownOpen">
    <slot name="dropdown" :dismiss="dismissDialog" />
  </div>
</div>
</template>
<style lang="scss">
.dropdown-container {
  position: relative;
  overflow: visible;

  .dropdown {
    position: absolute;
    z-index: 100;
    background-color: white;

    &.align-left {
      top: 100%;
      left: 0;
    }
    &.align-right {
      top: 100%;
      right: 0;
    }
  }
}
</style>
<script>

export default {
  props: {
    align: {
      default: 'left',
    }
  },
  data () {
    return {
      dropdownOpen: false,
    }
  },
  mounted () {
    if (typeof document !== 'undefined') {
      document.addEventListener('click', this.$clickEvent = (e) => {
        if (!this.$el.contains(e.target)) {
          this.dropdownOpen = false
        }
      })
    }
  },
  destroyed () {
    if (this.$clickEvent) {
      document.removeEventListener('click', this.$clickEvent)
    }
  },
  methods: {
    dismissDialog () {
      this.dropdownOpen = false
    }
  }
}
</script>

<style>
</style>
