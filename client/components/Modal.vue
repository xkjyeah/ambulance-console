<style lang="scss">
.modal-backdrop {
  background-color: rgba(0, 0, 0, 0.5);
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.modal-dialog {
  flex: 0 0 auto;
  min-width: 400px;
  width: 80vw;
  background-color: white;
  margin: auto;
  min-height: 400px;
  padding: 1em;
}
</style>
<script>
export default {
  data () {
    return {
      resolve: null, reject: null, props: null, component: null
    }
  },
  render (h) {
    return this.component ? h(
      'div',
      {
        class: {
          'modal-backdrop': true,
        }
      },
      [
        h(
          'div',
          {
            class: {'modal-dialog': true},
          },
          [
            h(this.component, {props: {resolve: this.resolve, reject: this.reject, ...this.props}})
          ]
        )
      ]
    ) : ''
  },
  methods: {
    show (component, props) {
      return new Promise((resolve, reject) => {
        Object.assign(this, {component, props, resolve, reject})
      })
    },
    hide () {
      this.component = this.props = this.resolve = this.reject = null
    }
  }
}
</script>
