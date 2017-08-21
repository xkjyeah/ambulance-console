<template>
  <div @click="showComponent"
    ref="cell"
    class="datasheet-cell" tabindex="1">

    <a href="#" @focus="showComponent" class="mock-focusable"
        @click.prevent="1 == 0"
        :tabindex="isEditing ? -1 : 0">
      <slot>
        {{ value }}
      </slot>
    </a>

    <div v-if="isEditing" ref="editor-component" class="the-editor-container">
      <slot name="editor">
      </slot>
    </div>
  </div>
</template>
<style lang="scss">
.mock-focusable {
  text-decoration: none;
  color: #000;
}
.datasheet-cell {
  position: relative;
}
.the-editor-container {
  width: 100%;
  position: absolute;
  top: 0;
  min-height: 100%;
  left: 0;
}
.the-editor {
  position: absolute;
  top: 0;
  min-height: 100%;
  left: 0;
  width: 100%;
}
</style>
<script>
// import _ from 'lodash'

export default {
  props: {
    value: {},
    component: {
      type: String,
      default: 'AutogrowTextarea'
    }
  },
  data () {
    return {
      edit: false,
      isEditing: false,
      editorStyle: null
    }
  },
  watch: {
    value: {
      immediate: true,
      handler (v) {
        this.edit = v
      }
    }
  },
  methods: {
    showComponent (field, value) {
      this.isEditing = true
      this.$nextTick(() => this.$nextTick(() => {
        let child = this.$refs['editor-component']
        child = child.$el || child

        const focusableDescendent =
          child.querySelectorAll('.focusable')[0] ||
          child.querySelectorAll('input, textarea, a')[0]

        if (!focusableDescendent) return

        focusableDescendent.focus()
        focusableDescendent.select()

        focusableDescendent.addEventListener('blur', () => {
          this.isEditing = false
        })
      }))
    },
    commit (v) {
      this.isEditing = false
    }
  }
}
</script>
