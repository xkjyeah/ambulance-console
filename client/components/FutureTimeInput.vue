<template>
  <TimeInput :value="formattedValue" @input="emitDate($event)" />
</template>

<script>
import leftPad from 'left-pad'
import TimeInput from '~/components/TimeInput'

export default {
  props: ['value'],
  components: {TimeInput},
  computed: {
    formattedValue () {
      return this.value
        ? `${leftPad(this.value.getHours(), 2, '0')}:${leftPad(this.value.getMinutes(), 2, '0')}`
        : ''
    }
  },
  methods: {
    emitDate (v) {
      if (!v) return this.$emit('input', v)

      const [hrs, mns] = v.split(':')
      const d = new Date()
      d.setHours(parseInt(hrs) || 0, parseInt(mns) || 0)

      if (d.getTime() - Date.now() < -60000) {
        d.setDate(d.getDate() + 1)
      }
      this.$emit('input', d)
    }
  }
}
</script>
